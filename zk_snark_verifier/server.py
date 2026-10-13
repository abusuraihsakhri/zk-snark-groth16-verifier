"""FastAPI interface for threshold audits and the standalone educational web page."""
from pathlib import Path
from typing import Any, Dict

from .agents import ZKSNARKCoordinator
from .models import FrontierPayload

coordinator = ZKSNARKCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError("Install server extras: pip install -e '.[server]'") from exc

    app = FastAPI(
        title="Groth16 Educational Simulator and Threshold Audit",
        description="Threshold-based audit API; not a real Groth16 cryptographic verifier.",
        version="2.0.0",
    )

    class TaskRequest(BaseModel):
        task_id: str = "TASK-001"
        target_identifier: str = "DEMO-TARGET"
        primary_metric: float = Field(default=28.5, allow_inf_nan=False)
        secondary_metric: float = Field(default=14.2, allow_inf_nan=False)
        status_descriptor: str = "DISCORDANT_ANOMALY"
        is_critical_flag: bool = False
        attributes: Dict[str, Any] = Field(default_factory=dict)

    class ChatRequest(BaseModel):
        query: str

    @app.get("/health")
    def health():
        return {"status": "HEALTHY", "system": "zk-snark-groth16-verifier", "version": "2.0.0"}

    @app.post("/api/audit")
    def api_audit(req: TaskRequest):
        return coordinator.process(FrontierPayload(**req.model_dump()))

    @app.post("/api/chat")
    def api_chat(req: ChatRequest):
        return {"response": coordinator.query_supervisory_chat(req.query)}

    web_directory = Path(__file__).resolve().parent.parent / "web"
    if (web_directory / "index.html").is_file():
        app.mount("/", StaticFiles(directory=str(web_directory), html=True), name="web")

    return app
