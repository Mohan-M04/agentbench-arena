from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import BenchmarkRun, AgentRun, BenchmarkTask, Metric, Trace, ToolCall
from schemas import BenchmarkStartRequest, BenchmarkRunOut
from orchestrator import BenchmarkOrchestrator

router = APIRouter(prefix="/api/benchmarks", tags=["Benchmarks"])

@router.post("/start")
async def start_benchmark(req: BenchmarkStartRequest, db: Session = Depends(get_db)):
    orchestrator = BenchmarkOrchestrator(db)
    
    # Query tasks
    tasks = db.query(BenchmarkTask).filter(BenchmarkTask.id.in_(req.task_ids)).all()
    if not tasks:
        raise HTTPException(status_code=400, detail="No valid tasks found for the provided task_ids")
    
    task_dicts = [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "prompt": t.prompt,
            "available_tools": t.available_tools,
            "expected_output": t.expected_output,
            "verifier_rule": t.verifier_rule,
            "failure_injection": t.failure_injection or {}
        }
        for t in tasks
    ]

    run_obj = await orchestrator.execute_suite_run(
        run_name=req.name,
        tasks=task_dicts,
        agent_ids=req.agent_ids,
        config=req.config.dict()
    )
    return {"status": "success", "benchmark_run_id": run_obj.id, "run_name": run_obj.name}

@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(BenchmarkRun).order_by(BenchmarkRun.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "status": r.status,
            "created_at": r.created_at,
            "completed_at": r.completed_at,
            "runs_count": len(r.agent_runs)
        }
        for r in runs
    ]

@router.get("/{run_id}/compare")
def get_comparison(run_id: str, db: Session = Depends(get_db)):
    b_run = db.query(BenchmarkRun).filter(BenchmarkRun.id == run_id).first()
    if not b_run:
        raise HTTPException(status_code=404, detail="Benchmark run not found")

    metrics = db.query(Metric).filter(Metric.benchmark_run_id == run_id).all()
    agent_runs = db.query(AgentRun).filter(AgentRun.benchmark_run_id == run_id).all()

    # Detailed agent summary
    agents_summary = {}
    for m in metrics:
        agents_summary[m.agent_id] = {
            "agent_id": m.agent_id,
            "avg_success_rate": m.avg_success_rate,
            "avg_score": (m.best_score + m.worst_score) / 2,
            "avg_steps": m.avg_steps,
            "avg_tool_calls": m.avg_tool_calls,
            "avg_tokens": m.avg_tokens,
            "avg_cost_usd": m.avg_cost_usd,
            "avg_completion_time_sec": m.avg_completion_time_sec,
            "failure_recovery_rate": m.failure_recovery_rate,
            "best_score": m.best_score,
            "worst_score": m.worst_score
        }

    # Group runs by task for distinct side-by-side agent view
    tasks_comparison = {}
    seen_agent_task = set()
    for ar in agent_runs:
        key = f"{ar.task_id}_{ar.agent_id}"
        if key in seen_agent_task:
            continue
        seen_agent_task.add(key)

        if ar.task_id not in tasks_comparison:
            tasks_comparison[ar.task_id] = []
        
        traces = [
            {
                "step": t.step_number,
                "action": t.action_type,
                "content": t.content,
                "model": t.model_provider
            }
            for t in ar.traces
        ]

        tasks_comparison[ar.task_id].append({
            "agent_id": ar.agent_id,
            "iteration": ar.run_iteration,
            "status": ar.status,
            "success": ar.task_success,
            "score": ar.success_score,
            "tokens": ar.total_tokens,
            "cost_usd": ar.estimated_cost_usd,
            "latency_sec": ar.completion_time_seconds,
            "recovery": ar.tool_failure_recovery,
            "final_answer": ar.final_answer,
            "explanation": ar.verifier_explanation,
            "traces": traces
        })

    return {
        "benchmark_run_id": run_id,
        "run_name": b_run.name,
        "status": b_run.status,
        "agents_summary": agents_summary,
        "tasks_comparison": tasks_comparison
    }

@router.get("/{run_id}/export")
def export_results(run_id: str, format: str = Query("json", enum=["json", "csv"]), db: Session = Depends(get_db)):
    data = get_comparison(run_id, db)
    return JSONResponse(content=data)
