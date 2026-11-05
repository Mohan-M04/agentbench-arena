import uuid
import datetime
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import BenchmarkRun, AgentRun, ToolCall, Trace, FailureEvent, Metric
from tools.sandbox import ToolSandbox
from metrics_engine import MetricsEngine
from agents.react_agent import DirectReActAgent
from agents.langgraph_agent import LangGraphAgent
from agents.custom_json_agent import CustomJsonAgent
from agents.webhook_agent import HttpWebhookAgent
from agents.react_retry_agent import ReActWithRetryAgent

class BenchmarkOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.agent_registry = {
            "agent-react-01": DirectReActAgent(),
            "agent-react-retry-05": ReActWithRetryAgent(),
            "agent-langgraph-02": LangGraphAgent(),
            "agent-custom-03": CustomJsonAgent(),
            "agent-webhook-04": HttpWebhookAgent()
        }

    async def execute_suite_run(
        self,
        run_name: str,
        tasks: List[Dict[str, Any]],
        agent_ids: List[str],
        config: Dict[str, Any]
    ) -> BenchmarkRun:
        run_id = f"brun-{uuid.uuid4().hex[:8]}"
        b_run = BenchmarkRun(
            id=run_id,
            name=run_name,
            status="running",
            config=config,
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(b_run)
        self.db.commit()

        repeated_runs = config.get("repeated_runs", 1)
        chaos_cfg = config.get("chaos", {})

        agent_results_map: Dict[str, List[Dict[str, Any]]] = {aid: [] for aid in agent_ids}

        for task in tasks:
            # Merge task-specific chaos with global run chaos
            merged_chaos = {**chaos_cfg, **task.get("failure_injection", {})}

            for agent_id in agent_ids:
                agent = self.agent_registry.get(agent_id, DirectReActAgent(agent_id=agent_id))

                for iteration in range(1, repeated_runs + 1):
                    # Identical sandbox environment per run
                    sandbox = ToolSandbox(chaos_config=merged_chaos)

                    # Execute agent
                    result = await agent.run(task, sandbox, config)

                    # Verify run
                    verification = MetricsEngine.verify_run(task, result.final_answer, result.tool_failure_recovery)
                    is_success = verification["pass_task"]
                    final_score = result.score if is_success else min(result.score, 30.0)

                    agent_run_id = f"arun-{uuid.uuid4().hex[:10]}"
                    arun = AgentRun(
                        id=agent_run_id,
                        benchmark_run_id=run_id,
                        agent_id=agent_id,
                        task_id=task["id"],
                        run_iteration=iteration,
                        status="success" if is_success else "failed",
                        final_answer=result.final_answer,
                        task_success=is_success,
                        success_score=final_score,
                        total_steps=result.total_steps,
                        total_tool_calls=result.total_tool_calls,
                        total_tokens=result.total_tokens,
                        estimated_cost_usd=result.estimated_cost_usd,
                        completion_time_seconds=result.completion_time_seconds,
                        tool_failure_recovery=result.tool_failure_recovery,
                        verifier_explanation=verification["explanation"]
                    )
                    self.db.add(arun)

                    # Store traces
                    for t in result.traces:
                        trace_obj = Trace(
                            id=f"tr-{uuid.uuid4().hex[:8]}",
                            agent_run_id=agent_run_id,
                            step_number=t.step_number,
                            action_type=t.action_type,
                            model_provider=t.model_provider,
                            content=t.content,
                            metadata_json={"latency_ms": t.latency_ms, "tokens": t.tokens, "cost_usd": t.cost_usd}
                        )
                        self.db.add(trace_obj)

                    # Store tool logs
                    for tl in sandbox.tool_logs:
                        tc_obj = ToolCall(
                            id=f"tc-{uuid.uuid4().hex[:8]}",
                            agent_run_id=agent_run_id,
                            tool_name=tl["tool_name"],
                            input_arguments=tl["input_arguments"],
                            raw_output=tl["raw_output"] if isinstance(tl["raw_output"], dict) else {"output": str(tl["raw_output"])},
                            status=tl["status"],
                            latency_ms=tl["latency_ms"],
                            retry_count=tl["retry_count"],
                            cost_usd=tl["cost_usd"]
                        )
                        self.db.add(tc_obj)

                    # Record failure events if applicable
                    if merged_chaos.get("inject_500") or result.tool_failure_recovery:
                        fe_obj = FailureEvent(
                            id=f"fe-{uuid.uuid4().hex[:8]}",
                            agent_run_id=agent_run_id,
                            failure_type="HTTP_500" if merged_chaos.get("inject_500") else "PROVIDER_FAILOVER",
                            location="ToolSandbox",
                            did_retry=result.tool_failure_recovery,
                            did_switch_tools=False,
                            did_complete_task=is_success,
                            recovery_strategy="Bifrost Provider Failover + Backoff",
                            details="Simulated fault injected into tool pipeline."
                        )
                        self.db.add(fe_obj)

                    agent_results_map[agent_id].append({
                        "task_success": is_success,
                        "success_score": final_score,
                        "total_steps": result.total_steps,
                        "total_tool_calls": result.total_tool_calls,
                        "total_tokens": result.total_tokens,
                        "estimated_cost_usd": result.estimated_cost_usd,
                        "completion_time_seconds": result.completion_time_seconds,
                        "tool_failure_recovery": result.tool_failure_recovery
                    })

        # Calculate and store aggregated metrics per agent
        for aid, runs in agent_results_map.items():
            agg = MetricsEngine.aggregate_runs(runs)
            m_obj = Metric(
                id=f"met-{uuid.uuid4().hex[:8]}",
                benchmark_run_id=run_id,
                agent_id=aid,
                avg_success_rate=agg.get("avg_success_rate", 0.0),
                success_variance=agg.get("success_variance", 0.0),
                avg_steps=agg.get("avg_steps", 0.0),
                avg_tool_calls=agg.get("avg_tool_calls", 0.0),
                avg_tokens=agg.get("avg_tokens", 0.0),
                avg_cost_usd=agg.get("avg_cost_usd", 0.0),
                avg_completion_time_sec=agg.get("avg_completion_time_sec", 0.0),
                failure_recovery_rate=agg.get("failure_recovery_rate", 0.0),
                best_score=agg.get("best_score", 0.0),
                worst_score=agg.get("worst_score", 0.0)
            )
            self.db.add(m_obj)

        b_run.status = "completed"
        b_run.completed_at = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(b_run)
        return b_run
