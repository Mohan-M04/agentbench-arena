from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime

class BenchmarkTaskCreate(BaseModel):
    id: str
    name: str
    category: str
    prompt: str
    available_tools: List[str] = []
    expected_output: Optional[str] = None
    verifier_rule: str = "contains_keywords"
    max_steps: int = 10
    max_tokens: int = 4000
    timeout_seconds: int = 30
    difficulty: str = "medium"
    failure_injection: Dict[str, Any] = {}
    tags: List[str] = []

class BenchmarkTaskOut(BenchmarkTaskCreate):
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class AgentCreate(BaseModel):
    id: str
    name: str
    agent_type: str # 'react', 'langgraph', 'custom_json'
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_steps: int = 10
    config: Dict[str, Any] = {}

class AgentOut(AgentCreate):
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ChaosConfig(BaseModel):
    inject_500: bool = False
    inject_timeout: bool = False
    inject_malformed_json: bool = False
    inject_stale_data: bool = False
    tool_unavailable: bool = False
    provider_outage: bool = False
    misleading_instruction: bool = False
    error_rate: float = 0.5
    latency_seconds: float = 0.0

class RunConfig(BaseModel):
    repeated_runs: int = 1
    max_steps: int = 10
    token_limit: int = 5000
    timeout_seconds: int = 30
    chaos: ChaosConfig = Field(default_factory=ChaosConfig)

class BenchmarkStartRequest(BaseModel):
    name: str
    task_ids: List[str]
    agent_ids: List[str]
    config: RunConfig = Field(default_factory=RunConfig)

class TraceOut(BaseModel):
    step_number: int
    action_type: str
    model_provider: Optional[str] = None
    content: str
    metadata_json: Dict[str, Any] = {}
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ToolCallOut(BaseModel):
    tool_name: str
    input_arguments: Dict[str, Any]
    raw_output: Dict[str, Any]
    status: str
    latency_ms: float
    retry_count: int
    cost_usd: float
    class Config:
        from_attributes = True

class AgentRunOut(BaseModel):
    id: str
    agent_id: str
    task_id: str
    run_iteration: int
    status: str
    final_answer: Optional[str]
    task_success: bool
    success_score: float
    total_steps: int
    total_tool_calls: int
    total_tokens: int
    estimated_cost_usd: float
    completion_time_seconds: float
    tool_failure_recovery: bool
    traces: List[TraceOut] = []
    tool_calls: List[ToolCallOut] = []
    class Config:
        from_attributes = True

class BenchmarkRunOut(BaseModel):
    id: str
    name: str
    status: str
    config: Dict[str, Any]
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    agent_runs: List[AgentRunOut] = []
    class Config:
        from_attributes = True
