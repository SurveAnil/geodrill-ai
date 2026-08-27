"""
main.py
=======
FastAPI application entry point for GeoDrill AI.
Provides RESTful APIs for document ingestion, LLM schema extraction, incident correlation,
and Copilot knowledge retrieval.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.ocr_routes import router as ocr_router
from src.api.routes.incident_routes import router as incident_router
from src.api.routes.copilot_routes import router as copilot_router
from src.api.routes.wells_routes import router as wells_router
from src.layer4_knowledge_graph.db_service import db_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: initializes database tables and resources on startup."""
    db_service.init_db()
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route handlers
app.include_router(ocr_router, prefix="/api/v1")
app.include_router(incident_router, prefix="/api/v1")
app.include_router(copilot_router, prefix="/api/v1")
app.include_router(wells_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "GeoDrill AI", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
