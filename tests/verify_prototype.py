import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from fastapi.testclient import TestClient
from main import app

def run_checks():
    with TestClient(app) as client:
        print("=" * 65)
        print("🧪 AGENTBENCH ARENA — FULL PROTOTYPE INTEGRITY VERIFICATION")
        print("=" * 65)

        # 1. Root & HTML Frontend
        r = client.get("/")
        assert r.status_code == 200, f"Root failed: {r.status_code}"
        assert "AgentBench" in r.text
        print("✅ [1/8] Frontend UI (index.html): 200 OK — Glassmorphic Observatory served")

        # 2. Health & Partners
        r = client.get("/api/health")
        assert r.status_code == 200
        health = r.json()
        assert health["status"] == "online"
        print(f"✅ [2/8] Health Check: 200 OK — Status: {health['status']} | Title Partner: {health['partners']['title_partner']}")

        # 3. Tasks & Agents
        r = client.get("/api/tasks")
        assert r.status_code == 200
        tasks = r.json()
        assert len(tasks) == 12
        print(f"✅ [3/8] Benchmark Tasks: 200 OK — {len(tasks)}/12 tasks loaded")

        r = client.get("/api/agents")
        assert r.status_code == 200
        agents = r.json()
        assert len(agents) >= 4
        print(f"✅ [4/8] Agent Architectures: 200 OK — {len(agents)} architectures seeded")

        # 4. Gateway Status
        r = client.get("/api/gateway/status")
        assert r.status_code == 200
        gw = r.json()
        print(f"✅ [5/8] Bifrost Gateway: 200 OK — {gw['gateway']} (Mode: {gw['mode']})")

        # 5. Live Duel / Benchmark Execution
        r = client.post("/api/benchmarks/start", json={
            "name": "Live Matchup Duel Test",
            "task_ids": [tasks[0]["id"]],
            "agent_ids": [agents[0]["id"], agents[1]["id"]],
            "config": {
                "repeated_runs": 1,
                "chaos": {"inject_500": True, "error_rate": 0.5}
            }
        })
        assert r.status_code == 200, f"Duel failed: {r.status_code} {r.text}"
        duel = r.json()
        assert duel["status"] == "success"
        print(f"✅ [6/8] Matchup Duel Execution: 200 OK — Run ID: {duel['benchmark_run_id']} | Status: {duel['status']}")

        # 6. Counterfactual Replay Engine
        r = client.post("/api/lab/counterfactual", json={
            "task": {"id": "task-06", "prompt": "Calculate compound interest with calculator outage"},
            "original_run": {"status": "FAILED", "score": 20.0, "steps": 6, "cost_usd": 0.000410},
            "intervention": "enable_bifrost_failover"
        })
        assert r.status_code == 200
        rep = r.json()
        assert rep["repaired_replay"]["status"] == "PASSED (RECOVERED)"
        assert rep["repaired_replay"]["score"] == 92.0
        assert "72" in rep["delta"]["score_gain"]
        print(f"✅ [7/8] Counterfactual Replay: 200 OK — {rep['original_run']['score']} pts ➔ {rep['repaired_replay']['score']} pts ({rep['delta']['score_gain']}, {rep['delta']['cost_delta']} cost)")

        # 7. Tavily Stale Answer Detector
        r = client.post("/api/stale-detector/verify", json={
            "query": "What is GPT-4o-mini pricing in 2026?",
            "raw_answer": "GPT-4o-mini costs $0.15 per 1M input tokens."
        })
        assert r.status_code == 200
        stale = r.json()
        assert "freshness_score" in stale
        print(f"✅ [8/8] Tavily Stale-Answer Detector: 200 OK — Freshness Score: {stale['freshness_score']}% | Sources: {len(stale['sources'])}")

        print("=" * 65)
        print("🏆 ALL PROTOTYPE SYSTEMS ARE 100% HEALTHY, FUNCTIONAL & VERIFIED!")
        print("=" * 65)

if __name__ == "__main__":
    run_checks()
