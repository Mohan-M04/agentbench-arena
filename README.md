# ⚔️ AgentBench Arena

> **“Benchmark agents by what they do—not just what they say.”**  
> *A Framework-Independent Reliability Lab & Stress-Testing Platform for AI Agents.*  
> **Geek Room AI Global Hackathon (Nov 2026)**  
> **Primary Track:** *Build a Benchmarking Platform for AI Agents, Not Just Models*  
> **Key Partners:** **Bifrost by Maxim AI** & **Tavily API**

---

## 📌 Problem Statement
Traditional AI benchmarks (MMLU, HumanEval, GSM8K) measure static model intelligence, but **fail completely for autonomous AI agents in production**.

In real-world environments:
* Downstream tools crash with `HTTP 500 / 503` errors.
* External APIs throttle with `HTTP 429` rate limits or return malformed JSON.
* Training cutoffs cause agents to output outdated pricing, revoked endpoints, or stale regulations.
* Primary model providers experience sudden dropouts.
* Agents enter unhandled recursive tool loops, wasting operational budgets.

**AgentBench Arena** is an open-source reliability lab that evaluates AI agents under identical, reproducible conditions across repeated runs, measuring task success, recovery rates, tool calls, and token costs.

---

## 🏗️ Architecture

```mermaid
graph TD
    UI["🖥️ AgentBench Arena UI<br/>(Glassmorphic Observatory, Topology, ARS)"] -->|"Configures Benchmark & Chaos"| Orch["⚙️ Benchmark Orchestrator"]
    
    subgraph "Agent Adapters (Framework-Independent)"
        A1["Direct ReAct Agent"]
        A2["LangGraph Agent"]
        A3["Custom JSON Agent"]
        A4["External HTTP Webhook Agent"]
    end
    
    Orch --> A1 & A2 & A3 & A4
    
    subgraph "Tool Sandbox & Chaos Engine"
        SB["🛡️ Secure Tool Sandbox Layer"]
        M1["10 Mock Tools (SQL, Calculator, Weather, Currency, Files, Flights)"]
        T1["🔍 Tavily Real-Time Web Search & Extract"]
    end
    
    A1 & A2 & A3 & A4 -->|"Executes Tool Calls"| SB
    SB --> M1 & T1
    
    subgraph "AI Gateway (Title Partner)"
        BF["⚡ Bifrost AI Gateway (Maxim AI)"]
        BF -->|"Automated Model Failover"| LLMs["gpt-4o-mini ➔ claude-3-haiku ➔ local ollama"]
    end
    
    A1 & A2 & A3 & A4 -->|"Routes Prompts & Tracks Cost"| BF
    
    Orch -->|"Stores Traces & Telemetry"| DB[("🗄️ Database: PostgreSQL / SQLite")]
    DB --> UI
```

---

## 🚀 The 3 Core Pillars

### 1. Controlled Chaos & Fault Injection
AgentBench Arena actively stress-tests agents using real failure scenarios:
* **Tool Outages (`HTTP 500 / 503`):** Forces agents to implement retry logic or switch tools.
* **Rate-Limit Throttling (`HTTP 429`):** Tests exponential backoff behavior.
* **Malformed Payloads:** Intercepts tool outputs with corrupted JSON to evaluate parser error handling.
* **Primary Provider Dropouts:** Triggers automatic fallback routes via **Bifrost Gateway** (`gpt-4o-mini` ➔ `claude-3-haiku` ➔ `ollama`).
* **Adversarial Prompt Overrides:** Inserts misleading system jailbreaks to measure instruction hierarchy adherence.

### 2. Side-by-Side Agent Duel & Execution Trace Viewer
Races two agents head-to-head on identical tasks under identical chaos:
* Step-by-step reasoning, tool arguments, raw outputs, and failovers.
* Milestone Gantt latency waterfalls (Gateway DNS ➔ Tool Run ➔ Failover Synthesis).
* Animated SVG execution cables showing real-time routing status.

### 3. Failure Autopsy & Counterfactual "What-If" Replay
When an agent fails, the lab produces an AI post-mortem report:
* **Root Cause:** Identifies the exact step and exception (e.g. unhandled 500 in calculator).
* **Agent Mistake:** Highlights the missed backoff or parameter error.
* **Counterfactual Replay:** Allows developers to test runtime interventions (*Enable Bifrost Gateway Failover*, *Add Exponential Backoff*, *Remove Misleading Prompt*) and observe the run convert from failed to verified pass.

---

## 📊 Evaluation & Analytical Extensions

### Agent Reliability Score (ARS) Formula
Rather than reporting disconnected metrics, AgentBench Arena computes a single 0–100 **Agent Reliability Score (ARS)** based on weighted operational criteria:

$$\text{ARS} = (\text{Success Rate} \times 0.35) + (\text{Recovery Rate} \times 0.25) + (\text{Cost Score} \times 0.15) + (\text{Speed Score} \times 0.15) + (\text{Consistency} \times 0.10)$$

*Where:*
* $\text{Recovery Rate} = (\text{Fault Recoveries} / \text{Total Runs}) \times 100$ (e.g., $7/10 = 70.0\%$)
* $\text{Cost Score} = \max(10, \min(100, 100 - (\text{Avg Cost} \times 8000)))$
* $\text{Speed Score} = \max(20, \min(100, 100 - (\text{Avg Latency} \times 10)))$
* $\text{Consistency} = \max(30, 100 - (\text{Variance} \times 2))$ *(In deterministic simulation mode, variance is 0, so consistency defaults to 100 for all agents)*

*Formula Verification (LangGraph Example):*  
$\text{ARS} = (100.0 \times 0.35) + (70.0 \times 0.25) + (98.2 \times 0.15) + (96.3 \times 0.15) + (100.0 \times 0.10) = 35.0 + 17.5 + 14.73 + 14.45 + 10.0 = \mathbf{91.7}$

Users can adjust weight profiles dynamically (*Balanced*, *Optimize for Cost*, *Optimize for Recovery*).

### Additional Lab Capabilities
* **Agent Personality Profiler:** Diagnoses behavioral archetypes (*Persistent Recoverer*, *Speedrunner*, *Overthinker*, *Fragile Agent*).
* **Cost-to-Success Pareto Frontier:** Scatter plot mapping expense vs. reliability to reveal optimal tradeoffs.
* **Real-Time Freshness & Citation Interceptor:** Uses **Tavily** and **Bifrost** to audit claims against 2026 ground truth and auto-correct outdated assertions.

---

## 📈 Seeded Benchmark Results (Simulation Mode Validation)

*Configuration: 10 repeated evaluation runs per agent under deterministic fault seeding (`Task: Tool Outage Recovery [HTTP 500 Outage]`, 7 persistent fault runs, 3 clean baseline runs across all agents). Evaluated in **High-Fidelity Gateway Simulation Mode** (deterministic model token/cost tracking and simulated provider failover modeling). Full telemetry is committed in [`results/raw_benchmark_runs.json`](results/raw_benchmark_runs.json) and summarized in [`results/benchmark_summary.csv`](results/benchmark_summary.csv):*

| Agent Variant | Architecture Paradigm | Overall Task Success | Faults Faced | Fault Recovery Rate | Avg Steps | Bifrost Tokens | Avg Cost | Avg Latency | ARS Rating |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ⭐ **LangGraph Agent** | State Graph Checkpoints | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 3.7 | 446 | $0.000224 | 0.37s | **91.7** |
| ⭐ **Custom JSON Agent** | Configured Schema Policy | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 5.1 | 286 | $0.000156 | 0.50s | **91.6** |
| ⭐ **ReAct w/ Retry & Fallback** | ReAct + Backoff & Fallback | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 5.8 | 350 | $0.000188 | 0.23s | **91.9** |
| ⭐ **Naive ReAct Loop (No Retry)** | Baseline Unhedged Loop | **3/10 (30.0%)** | 7/10 | **0/7 (0.0%)** | 5.4 | 351 | $0.000129 | 0.41s | **42.7** |
| 🔌 **External HTTP Webhook** | HTTP Adapter Verification Mock | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 1.7 | 280 | $0.000120 | 0.07s | *N/A (Adapter Test)* |

*Observations from the platform validation suite:*
* **Identical Conditions:** Runs 1, 2, 4, 5, 6, 8, and 9 encountered a persistent HTTP 500 tool outage (`error_rate = 1.0` during fault runs) for all agents; runs 3, 7, and 10 were clean baseline runs.
* **Persistent Outages Require Fallback:** Because the fault is persistent during an outage run, simply retrying the same broken endpoint will fail. Succeeded agents either route away to state-checkpoint handlers (LangGraph), trigger schema fallback synthesis (Custom JSON), or switch to parametric fallback reasoning (ReAct w/ Fallback).
* **Key Takeaway:** The platform correctly separates agents with error handling (state checkpoints, schema retries, parametric fallbacks) from agents without it, under reproducible, identical faults. The ARS scores for the three hedged architectures (91.7, 91.6, 91.9) demonstrate parity when equipped with recovery policies, while unhedged loops (42.7) fail under persistent faults.
* **Naive ReAct Baseline:** Demonstrates why unhedged agents fail in production: without backoff or fallback handlers, it repeated the failing call and aborted on all 7 fault runs.
* **External Webhook (Unranked):** Sits outside the leaderboard as a functional connectivity proof that external agents on port 9000 can be benchmarked over HTTP.
* **Reproducibility:** Re-run this exact seeded 10-run benchmark at any time:
  ```bash
  python scripts/run_real_benchmark.py
  ```

---

## ⚡ Live Gateway Validation (Maxim AI Bifrost Proxy)

To validate live network integration through Maxim AI's Bifrost daemon, we run a dedicated live validation benchmark (`scripts/run_live_bifrost_benchmark.py`). Bifrost acts as the unified AI proxy on `http://localhost:8080`, handling real HTTP requests, routing, and live latency measurements across agents:

*Configuration: 3 live evaluation runs per agent with dynamic fault injection (`Task: Tool Outage Recovery [HTTP 500 Outage]`). Executed directly against the live Bifrost Gateway daemon (`http://localhost:8080`). Telemetry is recorded in [`results/raw_live_bifrost_runs.json`](results/raw_live_bifrost_runs.json) and summarized in [`results/live_bifrost_benchmark_summary.csv`](results/live_bifrost_benchmark_summary.csv):*

| Agent Variant | Gateway Route | Task Success | Fault Recovery | Measured Latency | Bifrost Tokens | ARS Rating |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| ⭐ **LangGraph Agent** | Live Bifrost Proxy | **3/3 (100.0%)** | **2/2 (100.0%)** | 5.56s | 441 | **83.1** |
| ⭐ **Custom JSON Agent** | Live Bifrost Proxy | **3/3 (100.0%)** | **2/2 (100.0%)** | 3.49s | 280 | **86.3** |
| ⭐ **ReAct w/ Retry & Fallback** | Live Bifrost Proxy | **3/3 (100.0%)** | **2/2 (100.0%)** | 4.19s | 349 | **85.2** |
| ⭐ **Naive ReAct Loop (No Retry)** | Live Bifrost Proxy | **1/3 (33.3%)** | **0/2 (0.0%)** | 4.16s | 359 | **38.3** |

*How to run the live Bifrost validation suite:*
```bash
# 1. Start Bifrost Gateway daemon (confirmed from official docs)
npx -y @maximhq/bifrost
# or via Docker:
# docker run -p 8080:8080 maximhq/bifrost

# 2. Run the live benchmark runner (3-5 runs per agent)
python scripts/run_live_bifrost_benchmark.py 3
```

---

## 🛠️ Quickstart (Run in 2 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/Mohan-M04/agentbench-arena.git
cd agentbench-arena
```

### 2. Install Dependencies
```bash
pip install --break-system-packages -r backend/requirements.txt
```
*(Or inside a standard virtual environment: `pip install -r backend/requirements.txt`)*

### 3. Configure API Keys
Copy the example environment template:
```bash
cp backend/.env.example backend/.env
```
Add your **Tavily API key** (`tvly-...`) inside `backend/.env`.

### 4. Launch AgentBench Arena
From the repository root:
```bash
python main.py
```
Open your browser and navigate to:  
👉 **`http://localhost:8000`**

---

## 🔌 Proving Framework Independence: Running an External Agent
To verify that AgentBench Arena is truly framework-independent and can evaluate agents running outside this codebase:

1. In a separate terminal, launch the standalone external agent mock server:
   ```bash
   python examples/external_agent_server.py
   ```
   *(Runs on `http://localhost:9000/agent/act`)*
2. In the Arena dashboard, select **"External HTTP Webhook"** under agents.
3. The platform dispatches benchmark tasks via HTTP POST and logs the external agent's traces.

---

## ⚡ Bifrost & Tavily Integration Details

* **Bifrost AI Gateway (by Maxim AI):**
  * Sits as an OpenAI-compatible proxy at `http://localhost:8080/v1/chat/completions`.
  * The platform routes model calls through Bifrost, measuring tokens, latency, and simulating provider failovers (`gpt-4o-mini` ➔ `claude-3-haiku` ➔ `ollama`).
  * If the local Bifrost daemon is not running, the client operates in a simulated telemetry mode so developers can test the platform immediately.
* **Tavily Real-Time Search API:**
  * Powers live web retrieval tasks and ground truth verification.
  * Used by the Freshness Interceptor to audit facts against 2026 web sources.

---

## 🤖 AI Usage Disclosure (Hackathon Rule 2 Compliance)
In compliance with Geek Room Hackathon Rule 2, AI tools were utilized throughout the development of this project:
* **Google DeepMind Antigravity / Gemini 3.8 Flash:** Used as an interactive pair-programming assistant for system architecture planning, scaffolding FastAPI routes, authoring SQLAlchemy models, and authoring the responsive SVG cable topology and UI layout.
* **Claude (Anthropic):** Used for rigorous benchmark methodology review, mathematical consistency checks (denominators, ARS formulation), critique of production failure modes, and pitch deck structuring.

---

## 👥 Authors & Submission
* **Developer:** Mohan M (GitHub: [@Mohan-M04](https://github.com/Mohan-M04))
* **Hackathon:** Geek Room AI Global Hackathon (November 2026)
* **Primary Track:** Build a Benchmarking Platform for AI Agents, Not Just Models
