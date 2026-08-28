"""API for typed, explainable Phase 3 hazard predictions."""
from __future__ import annotations

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from src.api.schemas.predictive_schemas import PredictiveRiskRequest, PredictiveRiskResponse
from src.layer1_ingestion.telemetry_store import telemetry_store
from src.layer5_copilot.hazard_prediction import HAZARDS, MODEL_VERSION, predict_hazards

router = APIRouter(prefix="/predictive-risk", tags=["Predictive Risk"])


@router.post("", response_model=PredictiveRiskResponse)
@router.post("/predict", response_model=PredictiveRiskResponse, include_in_schema=False)
async def predict_risk(request: PredictiveRiskRequest) -> PredictiveRiskResponse:
    current = request.current_telemetry
    recent = request.recent_telemetry or await run_in_threadpool(
        telemetry_store.recent, current.well_id, 100
    )
    hazards = await run_in_threadpool(
        predict_hazards, current, recent,
        formation=request.formation, window_m=request.window_m,
    )
    return PredictiveRiskResponse(
        model_version=MODEL_VERSION, well_id=current.well_id,
        measured_depth_m=current.measured_depth_m, hazards=hazards,
        metadata={
            "baseline_type": "deterministic_heuristic_probability",
            "trained": False,
            "labels_used": False,
            "validated": False,
            "validation_status": "not_statistically_validated",
            "hazard_coverage": list(HAZARDS),
            "evidence_scope": "historical offset incidents near measured depth",
            "limitations": [
                "Probabilities are heuristic signals, not calibrated frequencies.",
                "Historical incident records are unlabeled evidence, not training outcomes.",
                "No alert delivery or operational recommendation is performed.",
            ],
        },
    )
