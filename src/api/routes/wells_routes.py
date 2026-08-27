"""
wells_routes.py
===============
FastAPI routes for well catalog discovery and geospatial proximity radius queries.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from src.layer4_knowledge_graph.db_service import db_service

router = APIRouter(prefix="/wells", tags=["Wells & Geospatial Intelligence"])


@router.get("/nearby", summary="Find offset wells within a physical distance radius")
async def get_wells_nearby(
    lat: float = Query(..., description="Latitude of reference point in decimal degrees (-90 to 90)"),
    lon: float = Query(..., description="Longitude of reference point in decimal degrees (-180 to 180)"),
    radius_km: float = Query(10.0, description="Search radius in kilometres (must be > 0)"),
    exclude_well_id: Optional[str] = Query(None, description="Optional well identifier to exclude from results"),
) -> List[Dict[str, Any]]:
    """
    Geospatial radius query endpoint. Computes great-circle Haversine distances
    between the given coordinate and all registered wells, returning those within
    `radius_km` sorted nearest-first.
    """
    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid latitude: {lat}. Must be between -90.0 and 90.0 degrees.",
        )
    if not (-180.0 <= lon <= 180.0):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid longitude: {lon}. Must be between -180.0 and 180.0 degrees.",
        )
    if radius_km <= 0.0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid radius_km: {radius_km}. Must be greater than 0.",
        )

    results = db_service.query_wells_within_radius(
        center_lat=lat,
        center_lon=lon,
        radius_km=radius_km,
        exclude_well_id=exclude_well_id,
    )
    return results
