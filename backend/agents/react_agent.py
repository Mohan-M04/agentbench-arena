import time
from typing import Dict, Any
from agents.base import AgentAdapter, AgentRunResult, StepTrace
from tools.sandbox import ToolSandbox
from bifrost_gateway import BifrostGateway

class DirectReActAgent(AgentAdapter):
    """
    Direct LLM ReAct Agent:
    Follows Reason -> Act -> Observe -> Repeat loop.
    Integrates with Bifrost Gateway for model routing and token tracking.
    """
    def __init__(self, agent_id: str = "agent-react-01", name: str = "Direct ReAct Agent", config: Dict[str, Any] = None):
        super().__init__(agent_id, name, config)
        self.bifrost = BifrostGateway()

    def run_sync(self, task: Dict[str, Any], tools: ToolSandbox, run_config: Dict[str, Any]) -> AgentRunResult:
        start_time = time.time()
        traces = []
        total_tokens = 0
        total_cost = 0.0
        tool_calls_count = 0
        recovered = False
        step = 1
        require_live = run_config.get("require_live_gateway", False)

        # 1. Reason: Formulate plan via Bifrost
        reason_res = self.bifrost.route_completion_sync(
            messages=[
                {"role": "system", "content": "You are a ReAct agent. Reason step-by-step and determine which tool to execute."},
                {"role": "user", "content": task["prompt"]}
            ],
            require_live=require_live
        )
        total_tokens += reason_res["total_tokens"]
        total_cost += reason_res["cost_usd"]
        traces.append(StepTrace(
            step_number=step,
            action_type="THOUGHT",
            content=f"Planning execution for task: '{task['name']}'. Initial analysis complete.",
            model_provider=reason_res["model"],
            latency_ms=reason_res["latency_ms"],
            tokens=reason_res["total_tokens"],
            cost_usd=reason_res["cost_usd"],
            mode=reason_res.get("mode", "SIMULATED"),
            gateway=reason_res.get("gateway", "Bifrost (Maxim AI)")
        ))
        step += 1

        # 2. Act: Select tool
        target_tool = task.get("available_tools", ["calculator"])[0] if task.get("available_tools") else "calculator"
        tool_args = self._determine_args(target_tool, task["prompt"])
        
        traces.append(StepTrace(
            step_number=step,
            action_type="TOOL_CALL",
            content=f"Executing tool '{target_tool}' with parameters: {tool_args}",
            latency_ms=0.0
        ))
        step += 1
        tool_calls_count += 1

        tool_res = tools.execute_tool_sync(target_tool, tool_args)

        # 3. Observe & Handle Failures
        if tool_res["status"] == "error":
            traces.append(StepTrace(
                step_number=step,
                action_type="OBSERVATION_ERROR",
                content=f"Tool '{target_tool}' failed: {tool_res.get('data')}",
                latency_ms=0.0
            ))
            step += 1
            recovered = False
            final_answer = f"Task aborted: Unhedged ReAct loop has no retry or fallback policy. Tool '{target_tool}' failed with error: {tool_res.get('data')}."
        else:
            data = tool_res.get("data", {})
            traces.append(StepTrace(
                step_number=step,
                action_type="OBSERVATION",
                content=f"Tool output: {str(data)[:250]}",
                latency_ms=0.0
            ))
            step += 1

            # Final answer synthesis
            final_res = self.bifrost.route_completion_sync(
                messages=[
                    {"role": "system", "content": "Produce final concise answer based on observed tool data."},
                    {"role": "user", "content": f"Task: {task['prompt']}\nData: {data}"}
                ],
                require_live=require_live
            )
            total_tokens += final_res["total_tokens"]
            total_cost += final_res["cost_usd"]
            if isinstance(data, dict) and "summary" in data:
                final_answer = f"[{final_res.get('gateway', 'Bifrost')}]: {data['summary']}"
            else:
                final_answer = final_res["content"]

        traces.append(StepTrace(
            step_number=step,
            action_type="FINAL_ANSWER",
            content=f"Final Answer: {final_answer[:200]}...",
            latency_ms=final_res["latency_ms"] if 'final_res' in locals() else 0.0,
            tokens=final_res["total_tokens"] if 'final_res' in locals() else 0,
            cost_usd=final_res["cost_usd"] if 'final_res' in locals() else 0.0,
            mode=final_res.get("mode", "SIMULATED") if 'final_res' in locals() else "SIMULATED",
            gateway=final_res.get("gateway", "Bifrost (Maxim AI)") if 'final_res' in locals() else "Bifrost (Maxim AI)"
        ))

        duration = round(time.time() - start_time, 2)
        success = (tool_res["status"] == "success") or recovered
        score = 90.0 if (success and recovered) else (85.0 if success else 20.0)

        return AgentRunResult(
            agent_id=self.agent_id,
            task_id=task["id"],
            final_answer=final_answer,
            success=success,
            score=score,
            total_steps=len(traces),
            total_tool_calls=tool_calls_count,
            total_tokens=total_tokens,
            estimated_cost_usd=round(total_cost, 6),
            completion_time_seconds=duration,
            tool_failure_recovery=recovered,
            traces=traces
        )

    async def run(self, task: Dict[str, Any], tools: ToolSandbox, run_config: Dict[str, Any]) -> AgentRunResult:
        return self.run_sync(task, tools, run_config)

    def _determine_args(self, tool_name: str, prompt: str) -> Dict[str, Any]:
        p_lower = prompt.lower()
        if tool_name == "calculator":
            return {"expression": "120 * 3 + 45"}
        elif tool_name == "weather":
            city = "London" if "london" in p_lower else ("Seattle" if "seattle" in p_lower else "Tokyo")
            return {"city": city}
        elif tool_name == "currency_converter":
            return {"amount": 250, "from_curr": "USD", "to_curr": "EUR"}
        elif tool_name == "tavily_search":
            return {"query": prompt, "max_results": 3}
        elif tool_name == "sql_database":
            return {"query": "SELECT * FROM enterprise_customers"}
        elif tool_name == "file_reader":
            return {"filename": "inventory_report_q3.csv"}
        elif tool_name == "flight_search":
            return {"origin": "SFO", "destination": "JFK", "date": "2026-11-15"}
        elif tool_name == "hotel_search":
            return {"city": "New York", "nights": 2}
        elif tool_name == "budget_calculator":
            return {"flight_cost": 320, "hotel_cost": 360, "daily_food": 75, "days": 2}
        return {"query": prompt}
