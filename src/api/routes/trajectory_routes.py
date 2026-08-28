"""Safe, deterministic Phase 2 trajectory and correlation endpoints."""
from __future__ import annotations
from typing import Any, Dict, List
from fastapi import APIRouter, File, HTTPException, UploadFile
from src.api.schemas.trajectory_schemas import TrajectoryRequest, FormationCorrelationRequest
from src.layer3_trajectory.survey_calculator import minimum_curvature
from src.layer3_trajectory.las_parser import parse_las
from src.layer3_trajectory.spatial_interpolator import correlate_formations
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/trajectory", tags=["Trajectory & Correlation"])

@router.post("/calculate")
def calculate_trajectory(request: TrajectoryRequest) -> Dict[str, Any]:
    try:
        stations = minimum_curvature([s.model_dump() for s in request.stations])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"stations": stations, "method": "minimum_curvature",
            "explanation": "North/east displacement and TVD are integrated between consecutive survey stations."}

@router.post("/parse-las")
async def parse_las_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not (file.filename or "").lower().endswith(".las"):
        raise HTTPException(status_code=400, detail="Only LAS files (.las) are supported")
    content = await file.read(10 * 1024 * 1024 + 1)
    if not content or len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="LAS file must be between 1 byte and 10 MB")
    try:
        parsed = await run_in_threadpool(_parse_las_content, content)
        return parsed
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


def _parse_las_content(content: bytes) -> Dict[str, Any]:
    """Parse and calculate trajectory away from the event loop."""
    parsed = parse_las(content.decode("utf-8", errors="replace"))
    parsed["trajectory"] = minimum_curvature(parsed["stations"])
    return parsed

@router.post("/correlate-formations")
def correlate_formation_tops(request: FormationCorrelationRequest) -> Dict[str, Any]:
    try:
        result = correlate_formations(request.formation_tops, [s.model_dump() for s in request.stations])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"correlations": result, "explanation": "Formation top MDs are linearly interpolated against the calculated trajectory."}