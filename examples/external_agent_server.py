"""
Standalone External Agent Server (Port 9000)
Demonstrates AgentBench Arena's true framework independence.
Any external agent framework (LangChain, AutoGen, CrewAI, Node.js)
can be benchmarked simply by exposing an HTTP endpoint.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="External Mock Agent Service")

class AgentTaskRequest(BaseModel):
    task: Dict[str, Any]
    chaos: Dict[str, Any] = {}

@app.post("/agent/act")
def act(req: AgentTaskRequest):
    prompt = req.task.get("prompt", "")
    chaos = req.chaos

    # External agent logic
    if chaos.get("inject_500"):
        return {
            "status": "recovered",
            "success": True,
            "final_answer": f"[External Agent]: Handled tool outage via internal fallback logic for task: {prompt[:50]}",
            "steps_taken": 3,
            "framework": "External-Custom-Framework"
        }

    return {
        "status": "success",
        "success": True,
        "final_answer": f"[External Agent]: Processed objective '{prompt[:50]}' successfully.",
        "steps_taken": 2,
        "framework": "External-Custom-Framework"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting External Agent Webhook Service on http://localhost:9000...")
    uvicorn.run(app, host="0.0.0.0", port=9000)
