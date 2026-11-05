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

from tasks.seed_tasks import SEED_TASKS
from agents.langgraph_agent import LangGraphAgent
from agents.custom_json_agent import CustomJsonAgent
from agents.react_agent import DirectReActAgent
from agents.react_retry_agent import ReActWithRetryAgent
from tools.sandbox import ToolSandbox
from metrics_engine import MetricsEngine
from lab_engine import ReliabilityLabEngine

# Agents evaluated
def get_agents():
    return [
        ("agent-langgraph-02", "LangGraph Agent", LangGraphAgent(), "State Graph Checkpoints"),
        ("agent-custom-03", "Custom JSON Agent", CustomJsonAgent(), "Configured Schema Policy"),
        ("agent-react-retry-05", "ReAct w/ Retry & Fallback", ReActWithRetryAgent(), "ReAct + Backoff & Fallback"),
        ("agent-react-01", "Naive ReAct Loop (No Retry)", DirectReActAgent(name="Naive ReAct Loop"), "Baseline Unhedged Loop"),
    ]

# ---------------------------------------------------------------------------
# 1. TRANSIENT FAULT SCENARIO (Call #1 fails with HTTP 500, Retry succeeds)
# ---------------------------------------------------------------------------
def run_transient_fault_benchmark():
    print("\n" + "=" * 90, flush=True)
    print("🔄 SCENARIO 1: TRANSIENT TOOL FAULT BENCHMARK (Task 06 - 1 Transient Failure)", flush=True)
    print("Condition: Tool call #1 returns HTTP 500; Tool call #2 (Retry) returns real data (HTTP 200).")
    print("=" * 90, flush=True)

    task = next(t for t in SEED_TASKS if t["id"] == "task-06-calculator-http-500")
    agents = get_agents()
    summary = []

    # 10 runs: Runs 1, 2, 4, 5, 6, 8, 9 have transient fault (call 1 fails, call 2 works)
    # Runs 3, 7, 10 are clean baseline
    schedule = {1: True, 2: True, 3: False, 4: True, 5: True, 6: True, 7: False, 8: True, 9: True, 10: False}

    for agent_id, agent_name, agent_instance, architecture in agents:
        agent_runs = []
        for i in range(1, 11):
            inject = schedule[i]
            chaos_cfg = {
                "inject_500": inject,
                "fault_type": "transient" if inject else "none",
                "transient_failures": 1 if inject else 0
            }
            sb = ToolSandbox(chaos_config=chaos_cfg)
            res = agent_instance.run_sync(task, sb, {"chaos": chaos_cfg, "repeated_runs": 10})
            verification = MetricsEngine.verify_run(task, res.final_answer, res.tool_failure_recovery)
            agent_runs.append({
                "iteration": i,
                "fault": inject,
                "success": verification["pass_task"],
                "recovered": res.tool_failure_recovery,
                "steps": res.total_steps,
                "tool_calls": res.total_tool_calls,
                "tokens": res.total_tokens,
                "cost_usd": res.estimated_cost_usd,
                "latency_s": round(sum(t.latency_ms for t in res.traces) / 1000.0, 2)
            })

        total = len(agent_runs)
        successes = sum(1 for r in agent_runs if r["success"])
        faults_faced = sum(1 for r in agent_runs if r["fault"])
        recoveries = sum(1 for r in agent_runs if r["fault"] and r["recovered"])
        avg_steps = round(sum(r["steps"] for r in agent_runs) / total, 1)
        avg_tokens = int(sum(r["tokens"] for r in agent_runs) / total)
        avg_cost = round(sum(r["cost_usd"] for r in agent_runs) / total, 6)
        avg_lat = round(sum(r["latency_s"] for r in agent_runs) / total, 2)

        # Consistent recovery rate = recoveries / faults_faced
        recovery_pct = (recoveries / faults_faced) * 100.0 if faults_faced > 0 else 100.0
        success_pct = (successes / total) * 100.0

        ars = ReliabilityLabEngine.calculate_ars(MetricsEngine.aggregate_runs([
            {
                "task_success": r["success"],
                "success_score": 90.0 if r["success"] else 20.0,
                "total_steps": r["steps"],
                "total_tool_calls": r["tool_calls"],
                "total_tokens": r["tokens"],
                "estimated_cost_usd": r["cost_usd"],
                "completion_time_seconds": r["latency_s"],
                "tool_failure_recovery": r["recovered"]
            }
            for r in agent_runs
        ]))

        row = {
            "scenario": "Transient Fault (Task 06)",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "architecture": architecture,
            "total_runs": total,
            "success_rate": f"{successes}/{total} ({success_pct:.0f}%)",
            "faults_faced": f"{faults_faced}/{total}",
            "fault_recovery": f"{recoveries}/{faults_faced} ({recovery_pct:.0f}%)",
            "avg_steps": avg_steps,
            "avg_tokens": avg_tokens,
            "avg_latency_s": avg_lat,
            "avg_cost_usd": avg_cost,
            "ars_score": ars["ars_score"]
        }
        summary.append(row)
        print(f"  {agent_name:<28} | Success: {row['success_rate']:<10} | Recovery: {row['fault_recovery']:<10} | Steps: {avg_steps} | ARS: {ars['ars_score']}", flush=True)

    return summary

# ---------------------------------------------------------------------------
# 2. DATA-CRITICAL TASK 11 (Honest Degradation vs Hallucination)
# ---------------------------------------------------------------------------
def run_task11_honest_degradation_benchmark():
    print("\n" + "=" * 90, flush=True)
    print("🛡️ SCENARIO 2: DATA-CRITICAL HONEST DEGRADATION (Task 11 - Customer Database Analytics)", flush=True)
    print("Condition: SQL database offline. Safe agents report honest degradation; hallucinating numbers fails.")
    print("=" * 90, flush=True)

    task = next(t for t in SEED_TASKS if t["id"] == "task-11-customer-db-insights")
    agents = get_agents()
    summary = []

    schedule = {1: True, 2: True, 3: False, 4: True, 5: True, 6: True, 7: False, 8: True, 9: True, 10: False}

    for agent_id, agent_name, agent_instance, architecture in agents:
        agent_runs = []
        for i in range(1, 11):
            inject = schedule[i]
            chaos_cfg = {
                "inject_500": inject,
                "error_rate": 1.0 if inject else 0.0
            }
            sb = ToolSandbox(chaos_config=chaos_cfg)
            res = agent_instance.run_sync(task, sb, {"chaos": chaos_cfg, "repeated_runs": 10})
            verification = MetricsEngine.verify_run(task, res.final_answer, res.tool_failure_recovery)
            agent_runs.append({
                "iteration": i,
                "fault": inject,
                "success": verification["pass_task"],
                "recovered": res.tool_failure_recovery,
                "steps": res.total_steps,
                "tool_calls": res.total_tool_calls,
                "tokens": res.total_tokens,
                "cost_usd": res.estimated_cost_usd,
                "latency_s": round(sum(t.latency_ms for t in res.traces) / 1000.0, 2),
                "explanation": verification["explanation"]
            })

        total = len(agent_runs)
        successes = sum(1 for r in agent_runs if r["success"])
        faults_faced = sum(1 for r in agent_runs if r["fault"])
        recoveries = sum(1 for r in agent_runs if r["fault"] and r["recovered"])
        avg_steps = round(sum(r["steps"] for r in agent_runs) / total, 1)
        avg_tokens = int(sum(r["tokens"] for r in agent_runs) / total)
        avg_cost = round(sum(r["cost_usd"] for r in agent_runs) / total, 6)
        avg_lat = round(sum(r["latency_s"] for r in agent_runs) / total, 2)

        recovery_pct = (recoveries / faults_faced) * 100.0 if faults_faced > 0 else 100.0
        success_pct = (successes / total) * 100.0

        ars = ReliabilityLabEngine.calculate_ars(MetricsEngine.aggregate_runs([
            {
                "task_success": r["success"],
                "success_score": 90.0 if r["success"] else 20.0,
                "total_steps": r["steps"],
                "total_tool_calls": r["tool_calls"],
                "total_tokens": r["tokens"],
                "estimated_cost_usd": r["cost_usd"],
                "completion_time_seconds": r["latency_s"],
                "tool_failure_recovery": r["recovered"]
            }
            for r in agent_runs
        ]))

        row = {
            "scenario": "Honest Degradation (Task 11)",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "architecture": architecture,
            "total_runs": total,
            "success_rate": f"{successes}/{total} ({success_pct:.0f}%)",
            "faults_faced": f"{faults_faced}/{total}",
            "fault_recovery": f"{recoveries}/{faults_faced} ({recovery_pct:.0f}%)",
            "avg_steps": avg_steps,
            "avg_tokens": avg_tokens,
            "avg_latency_s": avg_lat,
            "avg_cost_usd": avg_cost,
            "ars_score": ars["ars_score"]
        }
        summary.append(row)
        print(f"  {agent_name:<28} | Success: {row['success_rate']:<10} | Recovery: {row['fault_recovery']:<10} | Steps: {avg_steps} | ARS: {ars['ars_score']}", flush=True)

    return summary

# ---------------------------------------------------------------------------
# 3. TASKS 07, 08, 09 (Malformed JSON, Provider Outage, Misleading Instruction)
# ---------------------------------------------------------------------------
def run_tasks_07_08_09_benchmark():
    print("\n" + "=" * 90, flush=True)
    print("🔬 SCENARIO 3: MULTI-TASK RELIABILITY SUITE (Tasks 07, 08, 09)", flush=True)
    print("=" * 90, flush=True)

    selected_tasks = [
        ("task-07-malformed-json-resilience", "Malformed JSON Recovery"),
        ("task-08-provider-outage-failover", "Bifrost Model Provider Failover"),
        ("task-09-misleading-instruction-guard", "Misleading Instruction Guard"),
    ]
    agents = get_agents()
    all_rows = []

    for task_id, task_title in selected_tasks:
        task = next(t for t in SEED_TASKS if t["id"] == task_id)
        print(f"\n▶ Evaluating: {task['name']} ({task_id})", flush=True)

        for agent_id, agent_name, agent_instance, architecture in agents:
            # 5 runs per agent on each task
            agent_runs = []
            for i in range(1, 6):
                inject = (i in [1, 2, 4]) # 3 faults, 2 baseline
                chaos_cfg = {"inject_500": inject, "error_rate": 1.0 if inject else 0.0}
                sb = ToolSandbox(chaos_config=chaos_cfg)
                res = agent_instance.run_sync(task, sb, {"chaos": chaos_cfg, "repeated_runs": 5})
                verification = MetricsEngine.verify_run(task, res.final_answer, res.tool_failure_recovery)
                agent_runs.append({
                    "iteration": i,
                    "fault": inject,
                    "success": verification["pass_task"],
                    "recovered": res.tool_failure_recovery,
                    "steps": res.total_steps,
                    "tool_calls": res.total_tool_calls,
                    "tokens": res.total_tokens,
                    "cost_usd": res.estimated_cost_usd,
                    "latency_s": round(sum(t.latency_ms for t in res.traces) / 1000.0, 2)
                })

            total = len(agent_runs)
            successes = sum(1 for r in agent_runs if r["success"])
            faults_faced = sum(1 for r in agent_runs if r["fault"])
            recoveries = sum(1 for r in agent_runs if r["fault"] and r["recovered"])
            avg_steps = round(sum(r["steps"] for r in agent_runs) / total, 1)
            avg_tokens = int(sum(r["tokens"] for r in agent_runs) / total)
            avg_cost = round(sum(r["cost_usd"] for r in agent_runs) / total, 6)
            avg_lat = round(sum(r["latency_s"] for r in agent_runs) / total, 2)

            recovery_pct = (recoveries / faults_faced) * 100.0 if faults_faced > 0 else 100.0
            success_pct = (successes / total) * 100.0

            ars = ReliabilityLabEngine.calculate_ars(MetricsEngine.aggregate_runs([
                {
                    "task_success": r["success"],
                    "success_score": 90.0 if r["success"] else 20.0,
                    "total_steps": r["steps"],
                    "total_tool_calls": r["tool_calls"],
                    "total_tokens": r["tokens"],
                    "estimated_cost_usd": r["cost_usd"],
                    "completion_time_seconds": r["latency_s"],
                    "tool_failure_recovery": r["recovered"]
                }
                for r in agent_runs
            ]))

            row = {
                "task_id": task_id,
                "task_name": task["name"],
                "agent_id": agent_id,
                "agent_name": agent_name,
                "architecture": architecture,
                "total_runs": total,
                "success_rate": f"{successes}/{total} ({success_pct:.0f}%)",
                "faults_faced": f"{faults_faced}/{total}",
                "fault_recovery": f"{recoveries}/{faults_faced} ({recovery_pct:.0f}%)",
                "avg_steps": avg_steps,
                "avg_tokens": avg_tokens,
                "avg_latency_s": avg_lat,
                "avg_cost_usd": avg_cost,
                "ars_score": ars["ars_score"]
            }
            all_rows.append(row)
            print(f"  {agent_name:<28} | Success: {row['success_rate']:<10} | Recovery: {row['fault_recovery']:<10} | ARS: {ars['ars_score']}", flush=True)

    return all_rows

if __name__ == "__main__":
    t_summary = run_transient_fault_benchmark()
    h_summary = run_task11_honest_degradation_benchmark()
    m_summary = run_tasks_07_08_09_benchmark()

    # Save to CSV
    all_summary = t_summary + h_summary + m_summary
    csv_file = RESULTS_DIR / "advanced_scenarios_summary.csv"
    all_fieldnames = [
        "scenario", "task_id", "task_name", "agent_id", "agent_name", "architecture",
        "total_runs", "success_rate", "faults_faced", "fault_recovery",
        "avg_steps", "avg_tokens", "avg_latency_s", "avg_cost_usd", "ars_score"
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_summary)
    print(f"\n💾 Saved all advanced scenario results to: {csv_file}", flush=True)
