from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from lab_engine import ReliabilityLabEngine

router = APIRouter(prefix="/api/lab", tags=["Reliability Lab"])
lab = ReliabilityLabEngine()

class ARSRequest(BaseModel):
    agent_metrics: Dict[str, Any]
    weights: Optional[Dict[str, float]] = None

class AutopsyRequest(BaseModel):
    task: Dict[str, Any]
    agent_run: Dict[str, Any]

class CounterfactualRequest(BaseModel):
    task: Dict[str, Any]
    original_run: Dict[str, Any]
    intervention: str = "enable_bifrost_failover"

class CitationAuditRequest(BaseModel):
    query: str
    answer: str

@router.post("/ars")
def calculate_ars(req: ARSRequest):
    return lab.calculate_ars(req.agent_metrics, req.weights)

@router.get("/personalities")
def get_personalities():
    # Sample reference agents evaluated across benchmark suite
    return [
        lab.classify_personality("agent-langgraph-02", {"avg_steps": 3.8, "failure_recovery_rate": 83.3, "avg_success_rate": 91.7, "avg_cost_usd": 0.0003, "avg_completion_time_sec": 1.4}),
        lab.classify_personality("agent-react-01", {"avg_steps": 4.2, "failure_recovery_rate": 35.0, "avg_success_rate": 60.0, "avg_cost_usd": 0.0002, "avg_completion_time_sec": 1.1}),
        lab.classify_personality("agent-custom-03", {"avg_steps": 7.2, "failure_recovery_rate": 65.0, "avg_success_rate": 78.0, "avg_cost_usd": 0.0007, "avg_completion_time_sec": 2.8})
    ]

@router.post("/autopsy")
def generate_autopsy(req: AutopsyRequest):
    return lab.generate_autopsy(req.task, req.agent_run)

@router.post("/counterfactual")
async def run_counterfactual(req: CounterfactualRequest):
    return await lab.run_counterfactual_replay(req.task, req.original_run, req.intervention)

@router.post("/citation-audit")
def audit_citations(req: CitationAuditRequest):
    return lab.audit_citations(req.query, req.answer)

@router.get("/frontier")
def get_pareto_frontier():
    """Returns coordinates for the Cost-to-Success Pareto Frontier Chart."""
    return {
        "frontier_curve": [
            {"cost_usd": 0.0001, "success_rate": 65.0, "label": "Direct ReAct (Baseline)"},
            {"cost_usd": 0.0003, "success_rate": 92.0, "label": "LangGraph (Optimal Pareto)", "is_pareto": True},
            {"cost_usd": 0.0008, "success_rate": 95.0, "label": "Enterprise Custom (High Cost)", "is_pareto": True},
            {"cost_usd": 0.0012, "success_rate": 70.0, "label": "Overthinker (Sub-Optimal)", "is_pareto": False}
        ],
        "quadrants": {
            "top_left": "Cheap & Highly Reliable (The Gold Standard)",
            "top_right": "Expensive but Reliable",
            "bottom_left": "Cheap but Fragile",
            "bottom_right": "Expensive & Fragile (Wasted Budget)"
        }
    }

@router.get("/recipes")
def get_benchmark_recipes():
    return [
        {
            "id": "recipe-stress",
            "name": "Failure-Recovery Stress Test",
            "description": "Puts agents through 500 errors, rate-limits, and provider outages.",
            "task_ids": ["task-06-calculator-http-500", "task-07-malformed-json-resilience", "task-08-provider-outage-failover"],
            "chaos_profile": {"inject_500": True, "provider_outage": True},
            "icon": "flame"
        },
        {
            "id": "recipe-research",
            "name": "Research & Citation Integrity Audit",
            "description": "Tests Tavily live web retrieval, ground truth fidelity, and source citations.",
            "task_ids": ["task-04-ceo-tavily-citation", "task-05-recent-product-launch"],
            "chaos_profile": {},
            "icon": "globe"
        },
        {
            "id": "recipe-adversarial",
            "name": "Adversarial Injection & Jailbreak Guard",
            "description": "Measures whether agents resist embedded misleading system overrides.",
            "task_ids": ["task-09-misleading-instruction-guard"],
            "chaos_profile": {"misleading_instruction": True},
            "icon": "shield-alert"
        },
        {
            "id": "recipe-enterprise",
            "name": "Enterprise Planning & Multi-Tool Suite",
            "description": "Tests complex multi-step reasoning across SQL, Calendar, Flights, and Files.",
            "task_ids": ["task-10-trip-planning", "task-11-customer-db-insights", "task-12-meeting-transcript-extraction"],
            "chaos_profile": {},
            "icon": "briefcase"
        }
    ]
