#!/usr/bin/env python3
"""
AgentBench Arena — CI/CD Agent Reliability Quality Gate
Enforces strict resilience, safety, and cost thresholds in pull requests and continuous deployment.
Usage:
    python scripts/agent_quality_gate.py --min-ars 85.0 --max-cost 0.0005
"""

import sys
import os
import argparse
import csv
from pathlib import Path

def run_gate(min_ars: float, max_cost: float, min_recovery: float, csv_path: str) -> int:
    path = Path(csv_path)
    if not path.exists():
        print(f"❌ Error: Benchmark results summary not found at '{csv_path}'")
        return 1

    print("=" * 65)
    print("🛡️  AGENTBENCH ARENA — CI/CD AGENT RELIABILITY GATE")
    print("=" * 65)
    print(f"Gate Rules: Minimum ARS >= {min_ars} | Recovery >= {min_recovery}% | Max Cost <= ${max_cost:.6f}")
    print("-" * 65)

    failures = []
    evaluated_count = 0

    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agent_name = row.get("agent_name", "Unknown")
            is_ranked = row.get("is_ranked", "True").lower() == "true"
            
            # Skip unranked baseline / mock adapters
            if not is_ranked or "Naive" in agent_name or "Webhook" in agent_name:
                continue

            evaluated_count += 1
            ars_score = float(row.get("ars_score", 0.0))
            avg_cost = float(row.get("avg_cost_usd", 0.0))
            recovery_rate = float(row.get("fault_recovery_rate_pct", 0.0))

            print(f"Evaluating: {agent_name}")
            print(f"  • ARS Score: {ars_score:.1f} / 100")
            print(f"  • Recovery Rate: {recovery_rate:.1f}%")
            print(f"  • Cost per Task: ${avg_cost:.6f}")

            if ars_score < min_ars:
                failures.append(f"Agent '{agent_name}' ARS ({ars_score:.1f}) is below minimum threshold ({min_ars})")

            if avg_cost > max_cost:
                failures.append(f"Agent '{agent_name}' cost (${avg_cost:.6f}) exceeds maximum threshold (${max_cost:.6f})")

            if recovery_rate < min_recovery:
                failures.append(f"Agent '{agent_name}' fault recovery rate ({recovery_rate:.1f}%) is below {min_recovery}% safety requirement")

    print("-" * 65)
    if failures:
        print("❌ QUALITY GATE FAILED: Regressions or safety violations detected:")
        for fail in failures:
            print(f"  ✖ {fail}")
        print("=" * 65)
        return 1

    print(f"✅ QUALITY GATE PASSED: All {evaluated_count} production agents meet enterprise reliability standards.")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgentBench Arena CI/CD Quality Gate")
    parser.add_argument("--min-ars", type=float, default=75.0, help="Minimum acceptable ARS score")
    parser.add_argument("--min-recovery", type=float, default=70.0, help="Minimum acceptable fault recovery rate pct")
    parser.add_argument("--max-cost", type=float, default=0.0005, help="Maximum acceptable cost per task in USD")
    parser.add_argument("--summary-file", type=str, default=str(Path(__file__).parent.parent / "results" / "benchmark_summary.csv"))

    args = parser.parse_args()
    sys.exit(run_gate(args.min_ars, args.max_cost, args.min_recovery, args.summary_file))
