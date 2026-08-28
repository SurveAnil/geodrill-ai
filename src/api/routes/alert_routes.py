"""Deterministic predictive-risk alert endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from src.api.schemas.alert_schemas import (
    AlertAcknowledgement,
    AlertEvaluationRequest,
    AlertEvaluationResponse,
)
from src.layer1_ingestion.telemetry_store import telemetry_store
from src.layer4_knowledge_graph.db_service import db_service
from src.layer5_copilot.alerting import alert_store, evaluate_alerts
from src.layer5_copilot.incident_correlator import correlate_at_depth

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("", response_model=AlertEvaluationResponse)
@router.post("/evaluate", response_model=AlertEvaluationResponse, include_in_schema=False)
async def evaluate(request: AlertEvaluationRequest) -> AlertEvaluationResponse:
    current = request.current_telemetry
    recent = request.recent_telemetry or await run_in_threadpool(
        telemetry_store.recent, current.well_id, 100
    )
    events = await run_in_threadpool(
        correlate_at_depth, current.well_id, current.measured_depth_m,
        request.formation, request.window_m, db_service
    )
    alerts, recommendations, evidence_found = await run_in_threadpool(
        evaluate_alerts, current, recent, formation=request.formation,
        window_m=request.window_m, events=events
    )
    from datetime import datetime, timezone
    return AlertEvaluationResponse(
        well_id=current.well_id, measured_depth_m=current.measured_depth_m,
        alerts=alerts, recommendations=recommendations,
        evaluated_at=datetime.now(timezone.utc), evidence_found=evidence_found,
    )


@router.post("/{alert_id}/acknowledge", response_model=AlertAcknowledgement)
@router.post("/{alert_id}/ack", response_model=AlertAcknowledgement, include_in_schema=False)
async def acknowledge(alert_id: str) -> AlertAcknowledgement:
    alert = await run_in_threadpool(alert_store.acknowledge, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertAcknowledgement(
        alert_id=alert.alert_id, status=alert.status,
        acknowledged_at=alert.acknowledged_at,
    )
