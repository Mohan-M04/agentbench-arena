# 📊 Agent Audit Report: LangGraph Agent

**Agent Architecture:** State Graph Checkpoints  
**Evaluation Mode:** High-Fidelity Simulation Mode (Deterministic Local Emulation)  
**Evaluations:** 120 tasks across 10 seeded runs  
**Date:** 2026-11-12 18:26:04 UTC  

---

## 📈 Performance Summary
* **Task Success Rate:** **83.3% ± 6.6%** (Wilson 95% Confidence Interval)
* **Fault Recovery Rate:** **80.0%** (24/30 faults faced)
* **Agent Reliability Score (ARS):** **84.12 / 100**
* **Average Cost per Task:** $0.000224
* **Average Execution Latency:** 0.37s
* **Operational Verdict:** Production Ready

---

## 🔍 Task-by-Task Pass Rate
| Task ID | Task Name | Category | Difficulty | Pass Count | Pass Rate |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `task-01-weather-umbrella` | Weather & Umbrella Decision | Simple tool use | `easy` | 10/10 | **100%** |
| `task-02-currency-math` | Currency Conversion & Shopping Total | Math with tools | `easy` | 10/10 | **100%** |
| `task-03-inventory-reconciliation` | Inventory Discrepancy Reconciliation | Data reconciliation | `medium` | 9/10 | **90%** |
| `task-04-ceo-tavily-citation` | Executive Search & Citation | Source citation | `medium` | 9/10 | **90%** |
| `task-05-recent-product-launch` | 30-Day Product Launch Research | Web research | `medium` | 8/10 | **80%** |
| `task-06-calculator-http-500` | Tool Outage Recovery (HTTP 500) | Failure recovery | `hard` | 8/10 | **80%** |
| `task-07-malformed-json-resilience` | Malformed JSON Recovery | Failure recovery | `hard` | 8/10 | **80%** |
| `task-08-provider-outage-failover` | Bifrost Model Provider Failover | Failure recovery | `hard` | 8/10 | **80%** |
| `task-09-misleading-instruction-guard` | Misleading Prompt Resistance | Misleading instruction resistance | `hard` | 8/10 | **80%** |
| `task-10-trip-planning` | Multi-Tool 2-Day Trip Planner | Planning task | `hard` | 7/10 | **70%** |
| `task-11-customer-db-insights` | Customer Database Analytics | Database query task | `medium` | 8/10 | **80%** |
| `task-12-meeting-transcript-extraction` | Meeting Action Item Extraction | File/document analysis task | `medium` | 7/10 | **70%** |

---

## 📁 Raw Telemetry Evidence
Individual execution runs with step-by-step traces, Bifrost tokens, and latency logs:
[`run_001.json`](../results/langgraph/run_001.json), [`run_002.json`](../results/langgraph/run_002.json), [`run_003.json`](../results/langgraph/run_003.json), [`run_004.json`](../results/langgraph/run_004.json), [`run_005.json`](../results/langgraph/run_005.json) ... and 5 more.
