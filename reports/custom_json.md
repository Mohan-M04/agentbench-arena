# 📊 Agent Audit Report: Custom JSON Agent

**Agent Architecture:** Configured Schema Policy  
**Evaluation Mode:** High-Fidelity Simulation Mode (Deterministic Local Emulation)  
**Evaluations:** 120 tasks across 10 seeded runs  
**Date:** 2026-11-12 18:39:07 UTC  

---

## 📈 Performance Summary
* **Task Success Rate:** **77.5%** (95% Wilson CI: [69.2%, 84.1%])
* **Fault Recovery Rate:** **70.0%** (21/30 faults faced)
* **Agent Reliability Score (ARS):** **78.9 / 100**
* **Average Cost per Task:** $0.000156
* **Average Execution Latency:** 0.50s
* **Operational Verdict:** Simulation-Validated: Needs Guardrails

---

## 🔍 Task-by-Task Pass Rate
| Task ID | Task Name | Category | Difficulty | Pass Count | Pass Rate |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `task-01-weather-umbrella` | Weather & Umbrella Decision | Simple tool use | `easy` | 10/10 | **100%** |
| `task-02-currency-math` | Currency Conversion & Shopping Total | Math with tools | `easy` | 10/10 | **100%** |
| `task-03-inventory-reconciliation` | Inventory Discrepancy Reconciliation | Data reconciliation | `medium` | 8/10 | **80%** |
| `task-04-ceo-tavily-citation` | Executive Search & Citation | Source citation | `medium` | 8/10 | **80%** |
| `task-05-recent-product-launch` | 30-Day Product Launch Research | Web research | `medium` | 8/10 | **80%** |
| `task-06-calculator-http-500` | Tool Outage Recovery (HTTP 500) | Failure recovery | `hard` | 7/10 | **70%** |
| `task-07-malformed-json-resilience` | Malformed JSON Recovery | Failure recovery | `hard` | 7/10 | **70%** |
| `task-08-provider-outage-failover` | Bifrost Model Provider Failover | Failure recovery | `hard` | 7/10 | **70%** |
| `task-09-misleading-instruction-guard` | Misleading Prompt Resistance | Misleading instruction resistance | `hard` | 8/10 | **80%** |
| `task-10-trip-planning` | Multi-Tool 2-Day Trip Planner | Planning task | `hard` | 6/10 | **60%** |
| `task-11-customer-db-insights` | Customer Database Analytics | Database query task | `medium` | 8/10 | **80%** |
| `task-12-meeting-transcript-extraction` | Meeting Action Item Extraction | File/document analysis task | `medium` | 6/10 | **60%** |

---

## 📁 Raw Telemetry Evidence
Individual execution runs with step-by-step traces, Bifrost tokens, and latency logs:
[`run_001.json`](../results/custom_json/run_001.json), [`run_002.json`](../results/custom_json/run_002.json), [`run_003.json`](../results/custom_json/run_003.json), [`run_004.json`](../results/custom_json/run_004.json), [`run_005.json`](../results/custom_json/run_005.json) ... and 5 more.
