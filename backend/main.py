import os
import sys
import types

# Windows Defender Application Control / Smart App Control compatibility guard:
try:
    import _multiprocessing
except (ImportError, OSError):
    mock_mp = types.ModuleType("_multiprocessing")
    mock_mp.closesocket = lambda fd: None
    mock_mp.send = lambda fd, buf, flags=0: None
    mock_mp.recv = lambda fd, size, flags=0: b""
    sys.modules["_multiprocessing"] = mock_mp

# Ensure backend directory is in sys.path regardless of execution entrypoint
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base, SessionLocal
from models import BenchmarkTask, Agent
from tasks.seed_tasks import SEED_TASKS
from routes import tasks, agents, benchmarks, lab
from stale_detector import StaleAnswerDetector
from pydantic import BaseModel



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create DB tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed default tasks & agents if empty
    db = SessionLocal()
    try:
        if db.query(BenchmarkTask).count() == 0:
            print("🌱 Seeding 12 built-in benchmark tasks...")
            for t in SEED_TASKS:
                task_obj = BenchmarkTask(**t)
                db.add(task_obj)
            db.commit()

        if db.query(Agent).count() == 0:
            print("🌱 Seeding reference agents (LangGraph, ReAct w/ Retry, Custom JSON, Naive ReAct, Webhook)...")
            default_agents = [
                Agent(
                    id="agent-langgraph-02",
                    name="LangGraph Agent",
                    agent_type="langgraph",
                    description="State-graph based agent with Planner, ToolExecutor, and ResponseGenerator nodes.",
                    model="gpt-4o-mini",
                    max_steps=12
                ),
                Agent(
                    id="agent-react-retry-05",
                    name="ReAct w/ Retry & Fallback",
                    agent_type="react_retry",
                    description="ReAct loop equipped with exponential backoff and parametric fallback synthesis.",
                    model="gpt-4o-mini",
                    max_steps=10
                ),
                Agent(
                    id="agent-custom-03",
                    name="Custom JSON Agent",
                    agent_type="custom_json",
                    description="Configured via JSON with custom exponential backoff retry guardrails.",
                    model="gpt-4o-mini",
                    max_steps=8,
                    config={"retry_policy": {"max_retries": 3, "backoff": "exponential"}}
                ),
                Agent(
                    id="agent-react-01",
                    name="Naive ReAct Loop (No Retry)",
                    agent_type="react",
                    description="Standard Reason-Act-Observe loop without retry or fallback handlers.",
                    model="gpt-4o-mini",
                    max_steps=10
                ),
                Agent(
                    id="agent-webhook-04",
                    name="External Framework Webhook",
                    agent_type="external_webhook",
                    description="Benchmarks any external agent running outside the repository via HTTP POST.",
                    model="external",
                    max_steps=10,
                    config={"endpoint_url": "http://localhost:9000/agent/act"}
                )
            ]
            for a in default_agents:
                db.add(a)
            db.commit()
    finally:
        db.close()

    yield

app = FastAPI(
    title="AgentBench Arena API",
    description="A Benchmarking Platform for AI Agents, Not Just Models. Built for Geek Room AI Global Hackathon.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tasks.router)
app.include_router(agents.router)
app.include_router(benchmarks.router)
app.include_router(lab.router)

stale_detector = StaleAnswerDetector()

class StaleVerifyRequest(BaseModel):
    query: str
    raw_answer: str = None

@app.post("/api/stale-detector/verify")
async def verify_stale_answer(req: StaleVerifyRequest):
    return await stale_detector.analyze_and_verify(req.query, req.raw_answer)


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/")
def serve_arena():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AgentBench Arena API active. Frontend index.html not found."}

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "app": "AgentBench Arena",
        "version": "2.0.0",
        "tagline": "Benchmark agents by what they do—not just what they say.",
        "partners": {
            "title_partner": "Bifrost by Maxim AI (AI Gateway)",
            "track_partner": "Tavily (Real-Time Search & Extract API)"
        }
    }

@app.get("/api/gateway/status")
def gateway_status():
    from bifrost_gateway import _is_gateway_listening
    host = os.getenv("BIFROST_HOST", "http://localhost:8080")
    is_live = _is_gateway_listening(host)
    return {
        "gateway": "Bifrost (Maxim AI)",
        "host": host,
        "is_live": is_live,
        "mode": "live_proxy" if is_live else "simulation_mode"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
