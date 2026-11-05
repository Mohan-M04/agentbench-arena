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
* $\text{Cost Score} = \max(10, \min(100, 100 - (\text{Avg Cost} \times 8000)))$
* $\text{Speed Score} = \max(20, \min(100, 100 - (\text{Avg Latency} \times 10)))$
* $\text{Consistency} = \max(30, 100 - (\text{Variance} \times 2))$

Users can adjust weight profiles dynamically (*Balanced*, *Optimize for Cost*, *Optimize for Recovery*).

### Additional Lab Capabilities
* **Agent Personality Profiler:** Diagnoses behavioral archetypes (*Persistent Recoverer*, *Speedrunner*, *Overthinker*, *Fragile Agent*).
* **Cost-to-Success Pareto Frontier:** Scatter plot mapping expense vs. reliability to reveal optimal tradeoffs.
* **Real-Time Freshness & Citation Interceptor:** Uses **Tavily** and **Bifrost** to audit claims against 2026 ground truth and auto-correct outdated assertions.

---

## 📈 Empirical Benchmark Results (Tested Nov 5, 2026)

*Configuration: 10 repeated evaluation runs per agent under deterministic fault seeding (`Task: Tool Outage Recovery [HTTP 500 Outage]`, 7 fault runs, 3 clean baseline runs across all agents). Evaluated in **High-Fidelity Gateway Simulation Mode** (deterministic model token/cost tracking and simulated provider failover modeling). Full telemetry is committed in [`results/raw_benchmark_runs.json`](results/raw_benchmark_runs.json) and summarized in [`results/benchmark_summary.csv`](results/benchmark_summary.csv):*

| Agent Framework | Overall Task Success | Faults Faced | Fault Recovery Rate | Avg Steps | Bifrost Tokens | Avg Cost | Avg Latency | ARS Rating |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **LangGraph Agent** | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 3.7 | 446 | $0.000224 | 0.37s | **91.7 (Highest Resilience in Test)** |
| **Custom JSON Agent** | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 5.1 | 286 | $0.000156 | 0.50s | **91.6 (Configured Fallback Success)** |
| **External HTTP Agent** | **10/10 (100.0%)** | 7/10 | **7/7 (100.0%)** | 1.7 | 280 | $0.000120 | 0.06s | **92.3 (Decoupled Webhook Endpoint)** |
| **Reference ReAct Loop** | **3/10 (30.0%)** | 7/10 | **0/7 (0.0%)** | 5.4 | 351 | $0.000129 | 0.41s | **42.7 (Degraded under Persistent Fault)** |

*Observations from the seeded test suite:*
* **Identical Conditions:** Runs 1, 2, 4, 5, 6, 8, and 9 encountered the injected HTTP 500 tool outage for all agents; runs 3, 7, and 10 were clean baseline runs.
* **LangGraph Agent:** In all 7 fault runs, the state graph routed execution from the failed tool node to its `State Recovery Handler`, completing the task with 100% recovery.
* **Custom JSON Agent:** Applied its configured retry policy (up to 2 retries with backoff) and parametric fallback route, delivering 100% task completion.
* **External HTTP Agent:** Proves true framework independence by dispatching tasks to an external agent running outside this codebase (e.g., [`examples/external_agent_server.py`](examples/external_agent_server.py) on port 9000).
* **Reference ReAct Loop:** Successfully completed the 3 clean runs (Runs 3, 7, 10), but when tools threw 500 errors, our basic reference ReAct loop lacked backoff or fallback handlers; it re-invoked the failing tool without backoff and aborted.
* **Reproducibility:** Re-run this exact seeded 10-run benchmark at any time:
  ```bash
  python scripts/run_real_benchmark.py
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
