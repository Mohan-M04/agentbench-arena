import os
import sys
import json
import csv
import time
from pathlib import Path

# Setup Python paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
RESULTS_DIR = REPO_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import engine, Base, SessionLocal
from tasks.seed_tasks import SEED_TASKS
from agents.langgraph_agent import LangGraphAgent
from agents.custom_json_agent import CustomJsonAgent
from agents.react_agent import DirectReActAgent
from agents.react_retry_agent import ReActWithRetryAgent
from agents.webhook_agent import HttpWebhookAgent
from tools.sandbox import ToolSandbox
from metrics_engine import MetricsEngine
from lab_engine import ReliabilityLabEngine

# Deterministic fault schedule across 10 iterations:
# 7 runs encounter persistent injected tool outage (Runs 1, 2, 4, 5, 6, 8, 9)
# 3 runs are clean baseline runs (Runs 3, 7, 10)
# Every agent faces 100% IDENTICAL conditions on every run.
DETERMINISTIC_FAULT_SCHEDULE = {
    1: True,
    2: True,
    3: False,
    4: True,
    5: True,
    6: True,
    7: False,
    8: True,
    9: True,
    10: False,
}

def run_benchmark():
    print("=" * 90, flush=True)
    print("🚀 REPRODUCIBLE AGENT BENCHMARK RUNNER (10 RUNS PER AGENT - SEEDED FAULTS)", flush=True)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Task: Tool Outage Recovery (HTTP 500 Outage) - 7 Persistent Fault Runs, 3 Clean Runs", flush=True)
    print(f"Mode: Gateway Simulation Mode (Deterministic Token/Cost & Simulated Model Responses)", flush=True)
    print("=" * 90, flush=True)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    task = next((t for t in SEED_TASKS if t["id"] == "task-06-calculator-http-500"), None)
    if not task:
        raise ValueError("Task 'task-06-calculator-http-500' not found in seed tasks!")

    # Evaluated Framework Agents
    ranked_agents = [
        ("agent-langgraph-02", "LangGraph Agent", LangGraphAgent(), "State Graph Checkpoints"),
        ("agent-custom-03", "Custom JSON Agent", CustomJsonAgent(), "Configured Schema Policy"),
        ("agent-react-retry-05", "ReAct w/ Retry & Fallback", ReActWithRetryAgent(), "ReAct + Backoff & Fallback"),
        ("agent-react-01", "Naive ReAct Loop (No Retry)", DirectReActAgent(name="Naive ReAct Loop"), "Baseline Unhedged Loop"),
    ]

    # Functional Verification Only (Unranked mock proof)
    unranked_agents = [
        ("agent-webhook-04", "External HTTP Webhook", HttpWebhookAgent(agent_id="agent-webhook-04", name="External HTTP Agent"), "HTTP Adapter Verification Mock")
    ]

    all_raw_runs = []
    summary_rows = []
    markdown_rows = []
    num_iterations = 10

    for agent_id, agent_name, agent_instance, architecture in ranked_agents + unranked_agents:
        is_ranked = agent_id != "agent-webhook-04"
        prefix = "▶ [RANKED]" if is_ranked else "▶ [ADAPTER PROOF]"
        print(f"\n{prefix} Executing 10 seeded runs for: {agent_name} ({agent_id})...", flush=True)
        agent_runs = []

        for i in range(1, num_iterations + 1):
            t_start = time.perf_counter()
            inject_fault = DETERMINISTIC_FAULT_SCHEDULE[i]

            chaos_cfg = {
                "inject_500": inject_fault,
                "error_rate": 1.0 if inject_fault else 0.0
            }
            sandbox = ToolSandbox(chaos_config=chaos_cfg)
            run_config = {"repeated_runs": num_iterations, "chaos": chaos_cfg}

            res = agent_instance.run_sync(task, sandbox, run_config)
            elapsed = round(time.perf_counter() - t_start, 3)

            verification = MetricsEngine.verify_run(task, res.final_answer, res.tool_failure_recovery)
            is_success = verification["pass_task"]

            gateway_latency_sec = round(sum(t.latency_ms for t in res.traces) / 1000.0, 2)
            if gateway_latency_sec == 0:
                gateway_latency_sec = max(0.01, round(elapsed, 3))

            run_record = {
                "iteration": i,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "architecture": architecture,
                "is_ranked": is_ranked,
                "task_id": task["id"],
                "fault_injected": inject_fault,
                "success": is_success,
                "recovered": res.tool_failure_recovery,
                "steps": res.total_steps,
                "tool_calls": res.total_tool_calls,
                "tokens": res.total_tokens,
                "cost_usd": res.estimated_cost_usd,
                "latency_seconds": gateway_latency_sec,
                "final_answer": res.final_answer,
                "verifier_explanation": verification["explanation"],
                "traces_count": len(res.traces)
            }
            agent_runs.append(run_record)
            all_raw_runs.append(run_record)
            print(f"  Run {i:02d}/10 (Fault={inject_fault}): Success={is_success} | Recovered={res.tool_failure_recovery} | Steps={res.total_steps} | Tokens={res.total_tokens} | Latency={gateway_latency_sec}s", flush=True)

        transformed_for_agg = [
            {
                "task_success": r["success"],
                "success_score": 90.0 if r["success"] else 20.0,
                "total_steps": r["steps"],
                "total_tool_calls": r["tool_calls"],
                "total_tokens": r["tokens"],
                "estimated_cost_usd": r["cost_usd"],
                "completion_time_seconds": r["latency_seconds"],
                "tool_failure_recovery": r["recovered"]
            }
            for r in agent_runs
        ]
        agg = MetricsEngine.aggregate_runs(transformed_for_agg)
        ars_result = ReliabilityLabEngine.calculate_ars(agg)

        success_count = sum(1 for r in agent_runs if r["success"])
        total_faults = sum(1 for r in agent_runs if r["fault_injected"])
        recoveries_on_faults = sum(1 for r in agent_runs if r["fault_injected"] and r["recovered"])

        verdict_label = ars_result["verdict"] if is_ranked else "Functional Mock (Unranked)"
        score_display = f"**{ars_result['ars_score']}**" if is_ranked else "N/A (Adapter Test)"

        summary_rows.append({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "architecture": architecture,
            "is_ranked": is_ranked,
            "runs": num_iterations,
            "success_count": success_count,
            "success_rate_pct": agg["avg_success_rate"],
            "faults_faced": total_faults,
            "fault_recoveries": recoveries_on_faults,
            "fault_recovery_rate_pct": round((recoveries_on_faults / total_faults) * 100, 1),
            "avg_steps": agg["avg_steps"],
            "avg_tokens": agg["avg_tokens"],
            "avg_cost_usd": agg["avg_cost_usd"],
            "avg_latency_sec": agg["avg_completion_time_sec"],
            "ars_score": ars_result["ars_score"] if is_ranked else "N/A",
            "verdict": verdict_label
        })

        tag = "⭐ " if is_ranked else "🔌 "
        markdown_rows.append(
            f"| {tag}**{agent_name}** | {architecture} | **{success_count}/10 ({agg['avg_success_rate']}%)** | {total_faults}/10 | **{recoveries_on_faults}/{total_faults} ({round((recoveries_on_faults / total_faults) * 100, 1)}%)** | {agg['avg_steps']} | {agg['avg_tokens']} | ${agg['avg_cost_usd']:.6f} | {agg['avg_completion_time_sec']}s | {score_display} |"
        )

    # Save raw runs
    raw_path = RESULTS_DIR / "raw_benchmark_runs.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "benchmark_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_id": task["id"],
                "task_name": task["name"],
                "mode": "Gateway Simulation Mode (Deterministic Token/Cost & Simulated Model Responses)",
                "fault_behavior": "Persistent tool outage on fault runs (error_rate = 1.0). Requires fallback or recovery route to succeed.",
                "runs_per_agent": num_iterations,
                "seeded_fault_schedule": DETERMINISTIC_FAULT_SCHEDULE,
                "faults_per_agent": 7,
                "clean_runs_per_agent": 3,
                "simulated_models": "gpt-4o-mini (primary) / claude-3-haiku (failover)"
            },
            "runs": all_raw_runs
        }, f, indent=2)
    print(f"\n💾 Saved seeded run telemetry to: {raw_path}", flush=True)

    # Save CSV
    csv_path = RESULTS_DIR / "benchmark_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"💾 Saved summary CSV to: {csv_path}", flush=True)

    # Print markdown table
    print("\n" + "=" * 90, flush=True)
    print("📊 SEEDED EMPIRICAL BENCHMARK RESULTS (GATEWAY SIMULATION MODE)", flush=True)
    print("=" * 90, flush=True)
    print("| Agent Variant | Architecture Paradigm | Overall Task Success | Faults Faced | Fault Recovery Rate | Avg Steps | Bifrost Tokens | Avg Cost | Avg Latency | ARS Score |", flush=True)
    print("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |", flush=True)
    for row in markdown_rows:
        print(row, flush=True)
    print("=" * 90, flush=True)

if __name__ == "__main__":
    run_benchmark()
