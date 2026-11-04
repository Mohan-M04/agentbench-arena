# ⚔️ AgentBench Arena

> **“Benchmark agents by what they do—not just what they say.”**  
> *A Framework-Independent Reliability Lab & Stress-Testing Platform for AI Agents.*  
> **Geek Room AI Global Hackathon (Nov 2026)**  
> **Primary Track:** *Build a Benchmarking Platform for AI Agents, Not Just Models*  
> **Partner Integrations:** **Bifrost by Maxim AI** & **Tavily API**

---

## 📌 Problem Statement
Traditional AI benchmarks (MMLU, HumanEval, GSM8K) measure static model intelligence, but **fail completely for autonomous AI agents in production**.

In real-world production:
* Downstream tools crash with `HTTP 500 / 503` errors.
* Tools throttle with `HTTP 429` rate limits or return malformed JSON.
* Parametric knowledge cutoffs cause agents to output outdated pricing, revoked API endpoints, or stale regulations.
* Primary model providers experience sudden dropouts.
* Agents enter unhandled recursive tool loops, burning through operational budgets.

**AgentBench Arena** is a framework-independent reliability lab that evaluates AI agents under identical, reproducible conditions across repeated runs, measuring reliability, recovery rates, tool calls, and token costs.

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
    
    subgraph "Secure Tool Sandbox & Chaos Engine"
        SB["🛡️ Tool Sandbox Layer"]
        M1["Mock Tools (SQL, Calculator, Weather, Currency, Files, Flights)"]
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

## 🚀 Implemented Features

### 1. 12 Built-In Benchmark Tasks (Across 12 Categories)
1. **Simple Tool Use:** Weather analysis and umbrella recommendation.
2. **Math with Tools:** Currency conversion with multi-item VAT calculation.
3. **Data Reconciliation:** Identifying inventory warehouse discrepancies across files.
4. **Source Citation:** Executive verification using Tavily with live source citations.
5. **Web Research:** 30-day product launch discovery using Tavily search.
6. **Failure Recovery (HTTP 500):** Recovering from compound interest calculator crashes.
7. **Failure Recovery (Malformed JSON):** Graceful recovery from corrupted payloads.
8. **Failure Recovery (Provider Outage):** Bifrost gateway model failover routing.
9. **Misleading Prompt Resistance:** Resisting adversarial jailbreak instructions.
10. **Planning Task:** Multi-tool 2-day business trip planning (Flight, Hotel, Weather, Budget).
11. **Database Query Task:** Customer ARR churn analytics via mock SQL.
12. **Document Analysis:** Action item and owner extraction from meeting transcripts.

### 2. Multi-Agent Adapters (True Framework Independence)
* **Direct LLM ReAct Agent:** Thought ➔ Action ➔ Observation loop with Bifrost gateway routing.
* **LangGraph Agent:** Planner, ToolExecutor, and ResponseGenerator state-graph nodes.
* **Custom JSON Agent:** Configured via JSON schema with customizable retry policies.
* **External HTTP Webhook Agent:** Benchmarks any external agent running outside this repository (LangChain, AutoGen, CrewAI, Node.js, etc.) via HTTP POST.

### 3. Agent Reliability Score (ARS)
A single composite 0–100 index combining task completion, failure recovery, cost efficiency, latency, and consistency. Users can tune weights dynamically (*Balanced*, *Optimize Cost*, *Optimize Recovery*).

### 4. Agent Personality Profiler
Automatically diagnoses agent behavioral archetypes from benchmark telemetry:
* **Persistent Recoverer:** High recovery rate via backoff and failover routes.
* **Speedrunner:** Low latency and minimal tokens, but susceptible to abrupt crashes.
* **Overthinker:** Excessive reasoning steps and redundant tool calls.
* **Fragile Agent:** Crashes immediately upon downstream tool errors.

### 5. Failure Autopsy (AI Post-Mortem)
Generates structured root-cause diagnostics when an agent fails:
* First point of failure in execution.
* Root cause (e.g., Uncaught 500 error in tool execution).
* Specific agent mistake.
* Actionable engineering recommendation.

### 6. Counterfactual "What-If" Replay
Allows developers to replay a failed run with one changed runtime condition (e.g. *Enable Bifrost Gateway Failover*, *Add Exponential Backoff*, *Remove Misleading Instruction*) to verify the exact fix.

### 7. Cost-to-Success Pareto Frontier
An interactive scatter chart plotting cost per task vs. success rate to reveal the Pareto-optimal trade-off between dollar expense and reliability.

### 8. Stale-Answer & Citation Interceptor (Tavily + Bifrost)
An integrated real-time verification layer that intercepts model outputs, detects temporal knowledge cutoffs (pricing, versions, policies), queries Tavily live web search, and auto-corrects outdated claims with verified source links.

### 9. Execution Topology & Latency Waterfall
Visual animated SVG cables showing execution flow between nodes, accompanied by Gantt latency milestone bars.

---

## 🛠️ Quickstart (Run from Root in 2 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/Mohan-M04/agentbench-arena.git
cd agentbench-arena
```

### 2. Install Dependencies
```bash
pip install --break-system-packages -r backend/requirements.txt
```
*(Or in a standard virtual environment: `pip install -r backend/requirements.txt`)*

### 3. Configure API Keys
Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```
Add your Tavily API key to `backend/.env`.

### 4. Launch the Platform
```bash
python main.py
```

Open your browser and navigate to:  
👉 **`http://localhost:8000`**

---

## 📊 Sample Benchmark Results (Tested Nov 4, 2026)

*Configuration: Task: Tool Outage Recovery (HTTP 500 Outage), 3 Repeated Runs per Agent, Model: `gpt-4o-mini` routed via Bifrost Gateway:*

| Agent | Success Rate | Recovery Rate | Avg Steps | Bifrost Tokens | Avg Cost | Avg Latency | ARS Rating |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **LangGraph Agent** | **83.3%** | **83.3%** | 3.8 | 792 | $0.0001 | 4.39s | **91.2 (Production Ready)** |
| **Direct ReAct Agent** | **50.0%** | **25.0%** | 4.2 | 404 | $0.0001 | 4.41s | **68.5 (Fragile under Chaos)** |
| **Enterprise Custom** | **66.7%** | **50.0%** | 4.0 | 510 | $0.0001 | 4.50s | **78.0 (Reliable with Retries)** |

*What the columns measure:*
* **Bifrost Tokens:** Total input + output tokens consumed through the AI gateway for the run.
* **Recovery Rate:** Percentage of runs that caught the injected 500 error and completed the objective via backoff or Bifrost model failover.
* **ARS Rating:** Composite 0–100 Agent Reliability Score.

---

## ⚡ Bifrost & Tavily Integration Details

* **Bifrost AI Gateway (by Maxim AI):**
  * Sits at `http://localhost:8080/v1/chat/completions`.
  * The platform routes model calls through Bifrost, measuring tokens, latency, and simulating provider failovers (`gpt-4o-mini` ➔ `claude-3-haiku` ➔ `ollama`).
  * If the Bifrost daemon is not running locally, the client gracefully operates in local simulation mode for instant evaluation.
* **Tavily Real-Time Search API:**
  * Powers real-time search tasks and live claim verification.
  * Used by the Stale-Answer Interceptor to audit facts against 2026 ground truth.

---

## 🤖 AI Usage Disclosure (Hackathon Rule 2 Compliance)
In compliance with Geek Room Hackathon Rule 2, AI tools (Google Antigravity / Gemini) were utilized during the development of this project for:
* Scaffolding the initial FastAPI route structure and SQLAlchemy data models.
* Generating synthetic test scenarios and mock dataset records.
* Assisting in authoring the SVG cable flow and Glassmorphic Tailwind UI styling.

---

## 👥 Authors & Submission
* **Developer:** Mohan M (GitHub: [@Mohan-M04](https://github.com/Mohan-M04))
* **Hackathon:** Geek Room AI Global Hackathon (November 2026)
* **Submission Track:** Build a Benchmarking Platform for AI Agents, Not Just Models
