"""Real-time telemetry ingestion and recent-history endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query
from starlette.concurrency import run_in_threadpool

from src.api.schemas.telemetry_schemas import (
    TelemetryBatch,
    TelemetryRecentResponse,
)
from src.layer1_ingestion.telemetry_store import telemetry_store

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("", status_code=202)
@router.post("/ingest", status_code=202, include_in_schema=False)
async def ingest_telemetry(batch: TelemetryBatch) -> dict[str, int]:
    """Accept a bounded batch without doing blocking work on the event loop."""
    accepted = await run_in_threadpool(telemetry_store.append, batch.points)
    return {"accepted": accepted}


@router.get("/recent", response_model=TelemetryRecentResponse)
async def get_recent_telemetry(
    well_id: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(100, ge=1, le=1000),
) -> TelemetryRecentResponse:
    points = await run_in_threadpool(telemetry_store.recent, well_id, limit)
    return TelemetryRecentResponse(well_id=well_id, points=points)
