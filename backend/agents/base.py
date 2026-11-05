from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel
from tools.sandbox import ToolSandbox

class StepTrace(BaseModel):
    step_number: int
    action_type: str # THOUGHT, TOOL_CALL, OBSERVATION, RECOVERY, FINAL_ANSWER
    content: str
    model_provider: str = "gpt-4o-mini"
    latency_ms: float = 0.0
    tokens: int = 0
    cost_usd: float = 0.0
    mode: str = "SIMULATED"
    gateway: str = "Bifrost (Maxim AI)"

class AgentRunResult(BaseModel):
    agent_id: str
    task_id: str
    final_answer: str
    success: bool
    score: float
    total_steps: int
    total_tool_calls: int
    total_tokens: int
    estimated_cost_usd: float
    completion_time_seconds: float
    tool_failure_recovery: bool
    traces: List[StepTrace] = []

class AgentAdapter(ABC):
    """Common adapter interface for all agent frameworks."""
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}

    @abstractmethod
    async def run(self, task: Dict[str, Any], tools: ToolSandbox, run_config: Dict[str, Any]) -> AgentRunResult:
        pass
