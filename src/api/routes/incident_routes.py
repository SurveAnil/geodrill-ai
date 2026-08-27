"""
incident_routes.py
==================
FastAPI routes for retrieving well metadata, drilling incidents, offset-well spatial correlations,
and proactive risk assessment based on historical incident patterns.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from src.layer4_knowledge_graph.db_service import db_service
from src.layer5_copilot.incident_correlator import correlate_ahead
from src.layer5_copilot.risk_scorer import score_risk

router = APIRouter(prefix="/incidents", tags=["Incidents & Offset Intelligence"])


@router.get("/wells", summary="List all wells recorded in the system")
async def list_wells() -> List[Dict[str, Any]]:
    """Lists all wells stored in the database."""
    return db_service.list_wells()


@router.get("/well/{well_id:path}", summary="Retrieve header and event history for a specific well")
async def get_well_details(well_id: str) -> Dict[str, Any]:
    """
    Retrieves header and historical drilling events for a specific well.
    Supports well identifiers with forward slashes (e.g. '15/9-F-11B').
    """
    well = db_service.get_well(well_id)
    if not well:
        raise HTTPException(status_code=404, detail=f"Well '{well_id}' not found.")
    events = db_service.get_well_events(well_id)
    return {
        "well": well,
        "events": events,
    }


@router.get("/correlate-near", summary="Correlate incidents in offset wells near depth and formation")
async def correlate_near_incidents(
    well_id: str = Query(..., description="Target well identifier to exclude from offset matches"),
    depth_m: float = Query(..., description="Planned measured depth in metres"),
    window_m: float = Query(100.0, description="Depth window radius (+/- metres)"),
    formation: Optional[str] = Query(None, description="Optional target formation filter"),
) -> List[Dict[str, Any]]:
    """
    Finds historical drilling incidents (mud loss, stuck pipe, kicks) from neighboring offset wells
    within a depth window and matching formation.
    """
    return db_service.query_events_near(
        well_id=well_id,
        depth_m=depth_m,
        window_m=window_m,
        formation=formation,
    )


@router.get("/risk-check", summary="Proactive risk assessment for an active well at a given depth")
async def risk_check(
    well_id: str = Query(..., description="Active well identifier (must exist in the wells table)"),
    current_depth_m: float = Query(..., description="Current measured depth in metres"),
    formation: Optional[str] = Query(None, description="Current geological formation (optional)"),
    lookahead_m: float = Query(50.0, description="How far ahead to scan for historical incidents (metres)"),
) -> Dict[str, Any]:
    """
    Proactive risk assessment endpoint. Given an active well's current depth and
    formation, scans the upcoming depth interval for historical incidents in offset
    wells and returns an explainable risk score.

    This endpoint implements the "generate proactive alerts when current drilling
    operations approach depths or formations where similar challenges were encountered
    in nearby wells" requirement from the problem statement.

    The risk score is a transparent, rule-based heuristic (frequency × severity
    weighting) — NOT a trained ML model. See the explanation field in the response
    for details on what drove the score.
    """
    # Validate well exists
    if not db_service.well_exists(well_id):
        raise HTTPException(
            status_code=404,
            detail=f"Well '{well_id}' not found in the database.",
        )

    # Find historical incidents in the upcoming interval
    ahead_events = correlate_ahead(
        active_well_id=well_id,
        current_depth_m=current_depth_m,
        formation=formation,
        lookahead_m=lookahead_m,
    )

    # Score the risk
    risk_result = score_risk(ahead_events)

    return {
        "well_id": well_id,
        "current_depth_m": current_depth_m,
        "lookahead_m": lookahead_m,
        "risk_level": risk_result["risk_level"],
        "risk_score": risk_result["risk_score"],
        "explanation": risk_result["explanation"],
        "contributing_events": risk_result["contributing_events"],
    }

