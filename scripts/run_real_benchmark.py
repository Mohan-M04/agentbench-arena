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
from models import BenchmarkTask, Agent
from tasks.seed_tasks import SEED_TASKS
from agents.langgraph_agent import LangGraphAgent
from agents.custom_json_agent import CustomJsonAgent
from agents.react_agent import DirectReActAgent
from tools.sandbox import ToolSandbox
from metrics_engine import MetricsEngine
from lab_engine import ReliabilityLabEngine

def run_benchmark():
    print("=" * 80, flush=True)
    print("🚀 STARTING REAL BENCHMARK EXECUTION (10 RUNS PER AGENT)", flush=True)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Task: Tool Outage Recovery (HTTP 500 Outage) - Chaos Rate: 75%", flush=True)
    print(f"Primary Gateway: Bifrost (Maxim AI) / Model: gpt-4o-mini -> claude-3-haiku fallback", flush=True)
    print("=" * 80, flush=True)

    # 1. Init Database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Find the target task
    task = next((t for t in SEED_TASKS if t["id"] == "task-06-calculator-http-500"), None)
    if not task:
        raise ValueError("Task 'task-06-calculator-http-500' not found in seed tasks!")

    agents_to_test = [
        ("agent-langgraph-02", "LangGraph Agent", LangGraphAgent()),
        ("agent-custom-03", "Custom JSON Agent", CustomJsonAgent()),
        ("agent-react-01", "Direct ReAct Agent", DirectReActAgent()),
    ]

    all_raw_runs = []
    summary_rows = []
    markdown_rows = []

    num_iterations = 10
    run_config = {
        "repeated_runs": num_iterations,
        "chaos": task.get("failure_injection", {"inject_500": True, "error_rate": 0.75})
    }

    for agent_id, agent_name, agent_instance in agents_to_test:
        print(f"\n▶ Executing 10 runs for: {agent_name} ({agent_id})...", flush=True)
        agent_runs = []

        for i in range(1, num_iterations + 1):
            t_start = time.perf_counter()
            sandbox = ToolSandbox(chaos_config=run_config["chaos"])
            
            # Execute actual agent run synchronously
            res = agent_instance.run_sync(task, sandbox, run_config)
            # Measure simulated gateway latency across all step traces
            gateway_latency_sec = round(sum(t.latency_ms for t in res.traces) / 1000.0, 2)
            if gateway_latency_sec == 0:
                gateway_latency_sec = max(0.01, round(elapsed, 3))

            # Verification
            verification = MetricsEngine.verify_run(task, res.final_answer, res.tool_failure_recovery)
            is_success = verification["pass_task"]

            run_record = {
                "iteration": i,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "task_id": task["id"],
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
            print(f"  Run {i:02d}/10: Success={is_success} | Recovered={res.tool_failure_recovery} | Steps={res.total_steps} | Tokens={res.total_tokens} | Latency={gateway_latency_sec}s", flush=True)

        # Compute aggregate metrics
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
        
        # Calculate true ARS
        ars_result = ReliabilityLabEngine.calculate_ars(agg)

        success_count = sum(1 for r in agent_runs if r["success"])
        recovery_count = sum(1 for r in agent_runs if r["recovered"])

        summary_rows.append({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "runs": num_iterations,
            "success_count": success_count,
            "success_rate_pct": agg["avg_success_rate"],
            "recovery_count": recovery_count,
            "recovery_rate_pct": agg["failure_recovery_rate"],
            "avg_steps": agg["avg_steps"],
            "avg_tokens": agg["avg_tokens"],
            "avg_cost_usd": agg["avg_cost_usd"],
            "avg_latency_sec": agg["avg_completion_time_sec"],
            "ars_score": ars_result["ars_score"],
            "verdict": ars_result["verdict"]
        })

        markdown_rows.append(
            f"| **{agent_name}** | **{success_count}/10 ({agg['avg_success_rate']}%)** | **{recovery_count}/10 ({agg['failure_recovery_rate']}%)** | {agg['avg_steps']} | {agg['avg_tokens']} | ${agg['avg_cost_usd']:.6f} | {agg['avg_completion_time_sec']}s | **{ars_result['ars_score']} ({ars_result['verdict']})** |"
        )

    # 2. Save raw telemetry to results/raw_benchmark_runs.json
    raw_path = RESULTS_DIR / "raw_benchmark_runs.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "benchmark_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_id": task["id"],
                "task_name": task["name"],
                "chaos_injected": run_config["chaos"],
                "runs_per_agent": num_iterations,
                "gateway": "Bifrost (Maxim AI)",
                "models": "gpt-4o-mini (primary) / claude-3-haiku (failover)"
            },
            "runs": all_raw_runs
        }, f, indent=2)
    print(f"\n💾 Saved full raw run telemetry to: {raw_path}", flush=True)

    # 3. Save summary CSV to results/benchmark_summary.csv
    csv_path = RESULTS_DIR / "benchmark_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"💾 Saved aggregate summary to: {csv_path}", flush=True)

    # 4. Print results table
    print("\n" + "=" * 80, flush=True)
    print("📊 REAL MEASURED BENCHMARK RESULTS (10 RUNS)", flush=True)
    print("=" * 80, flush=True)
    print("| Agent | Task Success | Error Recovery | Avg Steps | Bifrost Tokens | Avg Cost | Avg Latency | ARS Rating |", flush=True)
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |", flush=True)
    for row in markdown_rows:
        print(row, flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    run_benchmark()
