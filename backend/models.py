import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    agent_type = Column(String, nullable=False) # 'react', 'langgraph', 'custom_json'
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    model = Column(String, default="gpt-4o-mini")
    temperature = Column(Float, default=0.2)
    max_steps = Column(Integer, default=10)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BenchmarkSuite(Base):
    __tablename__ = "benchmark_suites"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    task_ids = Column(JSON, default=list) # List of task IDs in this suite
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BenchmarkTask(Base):
    __tablename__ = "benchmark_tasks"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    available_tools = Column(JSON, default=list)
    expected_output = Column(Text, nullable=True)
    verifier_rule = Column(String, default="contains_keywords")
    max_steps = Column(Integer, default=10)
    max_tokens = Column(Integer, default=4000)
    timeout_seconds = Column(Integer, default=30)
    difficulty = Column(String, default="medium")
    failure_injection = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    suite_id = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, running, completed, failed
    config = Column(JSON, default=dict) # repeated_runs, max_steps, chaos settings
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    agent_runs = relationship("AgentRun", back_populates="benchmark_run", cascade="all, delete-orphan")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True)
    benchmark_run_id = Column(String, ForeignKey("benchmark_runs.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    task_id = Column(String, ForeignKey("benchmark_tasks.id"), nullable=False)
    run_iteration = Column(Integer, default=1)
    status = Column(String, default="running") # running, success, failed, timeout
    final_answer = Column(Text, nullable=True)
    task_success = Column(Boolean, default=False)
    success_score = Column(Float, default=0.0)
    total_steps = Column(Integer, default=0)
    total_tool_calls = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    completion_time_seconds = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    tool_failure_recovery = Column(Boolean, default=False)
    instruction_following_score = Column(Float, default=100.0)
    verifier_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    benchmark_run = relationship("BenchmarkRun", back_populates="agent_runs")
    tool_calls = relationship("ToolCall", back_populates="agent_run", cascade="all, delete-orphan")
    traces = relationship("Trace", back_populates="agent_run", cascade="all, delete-orphan")
    failure_events = relationship("FailureEvent", back_populates="agent_run", cascade="all, delete-orphan")

class ToolCall(Base):
    __tablename__ = "tool_calls"
    id = Column(String, primary_key=True)
    agent_run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    tool_name = Column(String, nullable=False)
    input_arguments = Column(JSON, default=dict)
    raw_output = Column(JSON, default=dict)
    status = Column(String, default="success") # success, error, timeout
    latency_ms = Column(Float, default=0.0)
    retry_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    agent_run = relationship("AgentRun", back_populates="tool_calls")

class Trace(Base):
    __tablename__ = "traces"
    id = Column(String, primary_key=True)
    agent_run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    action_type = Column(String, nullable=False) # THOUGHT, TOOL_CALL, OBSERVATION, RECOVERY, FINAL_ANSWER
    model_provider = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict) # tokens, latency, cost per step
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    agent_run = relationship("AgentRun", back_populates="traces")

class FailureEvent(Base):
    __tablename__ = "failure_events"
    id = Column(String, primary_key=True)
    agent_run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    failure_type = Column(String, nullable=False) # HTTP_500, TIMEOUT, MALFORMED_JSON, MISLEADING_INSTRUCTION, PROVIDER_OUTAGE
    location = Column(String, nullable=False)
    did_retry = Column(Boolean, default=False)
    did_switch_tools = Column(Boolean, default=False)
    did_complete_task = Column(Boolean, default=False)
    recovery_strategy = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    agent_run = relationship("AgentRun", back_populates="failure_events")

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(String, primary_key=True)
    benchmark_run_id = Column(String, ForeignKey("benchmark_runs.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    avg_success_rate = Column(Float, default=0.0)
    success_variance = Column(Float, default=0.0)
    avg_steps = Column(Float, default=0.0)
    avg_tool_calls = Column(Float, default=0.0)
    avg_tokens = Column(Float, default=0.0)
    avg_cost_usd = Column(Float, default=0.0)
    avg_completion_time_sec = Column(Float, default=0.0)
    failure_recovery_rate = Column(Float, default=0.0)
    best_score = Column(Float, default=0.0)
    worst_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ModelProviderEvent(Base):
    __tablename__ = "model_provider_events"
    id = Column(String, primary_key=True)
    agent_run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    primary_model = Column(String, nullable=False)
    fallback_model = Column(String, nullable=True)
    failover_occurred = Column(Boolean, default=False)
    latency_ms = Column(Float, default=0.0)
    tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    gateway = Column(String, default="Bifrost")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
