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

from bifrost_gateway import _is_gateway_listening, BifrostGateway
from tasks.seed_tasks import SEED_TASKS
from agents.langgraph_agent import LangGraphAgent
from agents.custom_json_agent import CustomJsonAgent
from agents.react_agent import DirectReActAgent
from agents.react_retry_agent import ReActWithRetryAgent
from tools.sandbox import ToolSandbox
from metrics_engine import MetricsEngine

from lab_engine import ReliabilityLabEngine

def run_live_benchmark(runs_per_agent: int = 3):
    gateway_host = os.getenv("BIFROST_HOST", "http://localhost:8080")
    is_live = _is_gateway_listening(gateway_host)

    print("=" * 90, flush=True)
    print("⚡ LIVE BIFROST GATEWAY VALIDATION BENCHMARK (3-5 REAL RUNS PER AGENT)", flush=True)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Gateway URL: {gateway_host} | Listening: {'✅ ONLINE' if is_live else '❌ OFFLINE'}", flush=True)
    print(f"Provider Keys: OpenAI={'sk-...' if os.getenv('OPENAI_API_KEY') else 'Not Set'}, Anthropic={'sk-ant-...' if os.getenv('ANTHROPIC_API_KEY') else 'Not Set'}", flush=True)
    print("=" * 90, flush=True)

    if not is_live:
        print("\n⚠️ WARNING: Bifrost daemon is not listening on port 8080.")
        print("To start Bifrost before running this script, run:")
        print("  npx -y @maximhq/bifrost")
        print("or")
        print("  docker run -p 8080:8080 maximhq/bifrost\n")

    task = next((t for t in SEED_TASKS if t["id"] == "task-06-calculator-http-500"), None)
    if not task:
        raise ValueError("Task 'task-06-calculator-http-500' not found in seed tasks!")

    agents = [
        ("agent-langgraph-02", "LangGraph Agent", LangGraphAgent(), "State Graph Checkpoints"),
        ("agent-custom-03", "Custom JSON Agent", CustomJsonAgent(), "Configured Schema Policy"),
        ("agent-react-retry-05", "ReAct w/ Retry & Fallback", ReActWithRetryAgent(), "ReAct + Backoff & Fallback"),
        ("agent-react-01", "Naive ReAct Loop (No Retry)", DirectReActAgent(name="Naive ReAct Loop"), "Baseline Unhedged Loop"),
    ]

    all_raw_runs = []
    summary_rows = []

    for agent_id, agent_name, agent_instance, architecture in agents:
        print(f"\n▶ Executing {runs_per_agent} live runs for: {agent_name} ({agent_id})...", flush=True)
        agent_runs = []

        for i in range(1, runs_per_agent + 1):
            t_start = time.perf_counter()
            inject_fault = (i % 2 == 1)  # alternate fault injection to test recovery live

            chaos_cfg = {
                "inject_500": inject_fault,
                "error_rate": 1.0 if inject_fault else 0.0
            }
            sandbox = ToolSandbox(chaos_config=chaos_cfg)
            run_config = {"repeated_runs": runs_per_agent, "chaos": chaos_cfg}

            res = agent_instance.run_sync(task, sandbox, run_config)
            elapsed = round(time.perf_counter() - t_start, 3)

            verification = MetricsEngine.verify_run(task, res.final_answer, res.tool_failure_recovery)
            is_success = verification["pass_task"]

            run_record = {
                "run_id": f"live-{agent_id}-run-{i:02d}",
                "agent_id": agent_id,
                "agent_name": agent_name,
                "iteration": i,
                "injected_fault": inject_fault,
                "recovered": res.tool_failure_recovery,
                "success": is_success,
                "total_steps": res.total_steps,
                "tokens": res.total_tokens,
                "cost_usd": res.estimated_cost_usd,
                "latency_s": elapsed,
                "final_answer": res.final_answer,
                "mode": "LIVE_BIFROST" if is_live else "SIMULATED",
                "traces": [
                    {
                        "step": tr.step_number,
                        "type": tr.action_type,
                        "latency_ms": tr.latency_ms,
                        "tokens": tr.tokens,
                        "cost": tr.cost_usd,
                        "model": tr.model_provider
                    } for tr in res.traces
                ]
            }
            agent_runs.append(run_record)
            all_raw_runs.append(run_record)
            fault_flag = "⚠️ FAULT" if inject_fault else "✅ BASELINE"
            rec_flag = "RECOVERED" if res.tool_failure_recovery else ("SUCCESS" if is_success else "FAILED")
            print(f"  Run #{i:02d} [{fault_flag}] -> {rec_flag} | Latency: {elapsed}s | Tokens: {res.total_tokens} | Cost: ${res.estimated_cost_usd:.5f}", flush=True)

        # Aggregate per agent
        total_runs = len(agent_runs)
        success_runs = sum(1 for r in agent_runs if r["success"])
        faults_faced = sum(1 for r in agent_runs if r["injected_fault"])
        recoveries = sum(1 for r in agent_runs if r["recovered"] and r["injected_fault"])
        avg_steps = round(sum(r["total_steps"] for r in agent_runs) / total_runs, 1)
        avg_tokens = int(sum(r["tokens"] for r in agent_runs) / total_runs)
        avg_cost = round(sum(r["cost_usd"] for r in agent_runs) / total_runs, 5)
        avg_latency = round(sum(r["latency_s"] for r in agent_runs) / total_runs, 2)

        transformed = [
            {
                "task_success": r["success"],
                "success_score": 90.0 if r["success"] else 20.0,
                "total_steps": r["total_steps"],
                "total_tool_calls": 1,
                "total_tokens": r["tokens"],
                "estimated_cost_usd": r["cost_usd"],
                "completion_time_seconds": r["latency_s"],
                "tool_failure_recovery": r["recovered"]
            }
            for r in agent_runs
        ]
        agg = MetricsEngine.aggregate_runs(transformed)
        ars_calc = ReliabilityLabEngine.calculate_ars(agg)

        summary_rows.append({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "architecture": architecture,
            "mode": "LIVE_BIFROST" if is_live else "SIMULATED",
            "total_runs": total_runs,
            "success_rate": f"{success_runs}/{total_runs} ({(success_runs/total_runs)*100:.0f}%)",
            "fault_recovery": f"{recoveries}/{faults_faced} ({(recoveries/max(1, faults_faced))*100:.0f}%)",
            "avg_latency_s": avg_latency,
            "avg_steps": avg_steps,
            "avg_tokens": avg_tokens,
            "avg_cost_usd": avg_cost,
            "ars_score": ars_calc["ars_score"]
        })

    # Save raw runs
    raw_path = RESULTS_DIR / "raw_live_bifrost_runs.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_raw_runs, f, indent=2)
    print(f"\n💾 Saved raw runs to: {raw_path}", flush=True)

    # Save summary CSV
    csv_path = RESULTS_DIR / "live_bifrost_benchmark_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"💾 Saved summary CSV to: {csv_path}", flush=True)

    # Print summary table
    print("\n" + "=" * 90, flush=True)
    print(f"📊 LIVE BIFROST VALIDATION SUMMARY ({'LIVE BIFROST PROXY' if is_live else 'SIMULATED FALLBACK'})", flush=True)
    print("=" * 90, flush=True)
    header = f"{'Agent Name':<28} | {'Mode':<12} | {'Success':<10} | {'Recovery':<10} | {'Latency':<8} | {'Tokens':<6} | {'ARS':<6}"
    print(header, flush=True)
    print("-" * len(header), flush=True)
    for row in summary_rows:
        print(f"{row['agent_name']:<28} | {row['mode']:<12} | {row['success_rate']:<10} | {row['fault_recovery']:<10} | {row['avg_latency_s']:<8} | {row['avg_tokens']:<6} | {row['ars_score']:<6}", flush=True)
    print("=" * 90, flush=True)

if __name__ == "__main__":
    runs = 3
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        runs = int(sys.argv[1])
    run_live_benchmark(runs)
