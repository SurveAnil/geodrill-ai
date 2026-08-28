"""
main.py
=======
FastAPI application entry point for GeoDrill AI.
Provides RESTful APIs for document ingestion, LLM schema extraction, incident correlation,
and Copilot knowledge retrieval.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import json
import logging
import os
import re
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api.routes.ocr_routes import router as ocr_router
from src.api.routes.incident_routes import router as incident_router
from src.api.routes.copilot_routes import router as copilot_router
from src.api.routes.wells_routes import router as wells_router
from src.api.routes.ingest_routes import router as ingest_router
from src.api.routes.trajectory_routes import router as trajectory_router
from src.api.routes.telemetry_routes import router as telemetry_router
from src.api.routes.predictive_risk_routes import router as predictive_risk_router
from src.api.routes.alert_routes import router as alert_router
from src.layer4_knowledge_graph.db_service import db_service
from src.layer4_knowledge_graph.vector_store import vector_store
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _validate_configuration() -> None:
    """Validate safe, deployment-facing settings without logging credential values."""
    environment = os.getenv("GEODRILL_ENVIRONMENT", "development").strip().lower()
    if environment not in {"development", "test", "staging", "production"}:
        raise RuntimeError("GEODRILL_ENVIRONMENT must be development, test, staging, or production")
    if environment == "production":
        configured_origins = os.getenv("GEODRILL_CORS_ORIGINS", "").strip()
        if not configured_origins:
            logger.warning("Production CORS origins are not explicitly configured; using defaults")
        for name in ("ANTHROPIC_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
            value = os.getenv(name, "")
            if value.lower().startswith("your_") or value.lower() in {"", "changeme"}:
                logger.warning("Production provider credential %s is not configured", name)


def _check_dependencies() -> dict[str, str]:
    """Run inexpensive dependency probes and return status-only details."""
    checks: dict[str, str] = {}
    try:
        with db_service.get_connection() as connection:
            connection.execute("SELECT 1").fetchone()
        checks["sqlite"] = "ok"
    except Exception:
        checks["sqlite"] = "unavailable"
    try:
        vector_store.collection.count()
        checks["chroma"] = "ok"
    except Exception:
        checks["chroma"] = "unavailable"
    return checks


class RequestLoggingMiddleware:
    """Attach a bounded correlation ID and emit one structured access log per request."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        supplied = headers.get(b"x-request-id", b"").decode("latin-1")
        request_id = supplied if _REQUEST_ID.fullmatch(supplied) else str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        status_code = 500
        started = time.perf_counter()

        async def send_with_id(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = list(message.get("headers", []))
                response_headers.append((b"x-request-id", request_id.encode("ascii")))
                message = dict(message, headers=response_headers)
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            logger.info(json.dumps({
                "event": "http_request",
                "request_id": request_id,
                "method": scope.get("method"),
                "path": scope.get("path"),
                "status": status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }, separators=(",", ":")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: initializes database tables and resources on startup."""
    _validate_configuration()
    await run_in_threadpool(db_service.init_db)
    yield


app = FastAPI(
    title="GeoDrill AI API",
    description="Agentic Oil & Gas Knowledge System for Drilling Report Extraction and Offset-Well Intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Include route handlers
app.include_router(ocr_router, prefix="/api/v1")
app.include_router(incident_router, prefix="/api/v1")
app.include_router(copilot_router, prefix="/api/v1")
app.include_router(wells_router, prefix="/api/v1")
app.include_router(ingest_router, prefix="/api/v1")
app.include_router(trajectory_router, prefix="/api/v1")
app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(predictive_risk_router, prefix="/api/v1")
app.include_router(alert_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    """Backward-compatible shallow health endpoint."""
    return {"status": "ok", "app": "GeoDrill AI", "version": "1.0.0"}


@app.get("/health/live", tags=["System"])
@app.get("/livez", tags=["System"], include_in_schema=False)
async def liveness_check():
    """Report whether the process is alive; no dependency calls are made."""
    return {"status": "ok", "app": "GeoDrill AI", "version": "1.0.0"}


@app.get("/health/ready", tags=["System"])
@app.get("/readyz", tags=["System"], include_in_schema=False)
async def readiness_check():
    """Report dependency readiness using status-only, non-sensitive diagnostics."""
    checks = await run_in_threadpool(_check_dependencies)
    ready = all(value == "ok" for value in checks.values())
    payload = {"status": "ok" if ready else "unavailable", "checks": checks}
    if not ready:
        return JSONResponse(status_code=503, content=payload)
    return payload


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
