"""
incident_schemas.py
===================
Data contract defining well headers, drilling events, confidence levels,
and extraction results for the GeoDrill AI platform.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    MUD_LOSS = "mud_loss"
    KICK = "kick"
    STUCK_PIPE = "stuck_pipe"
    CEMENTING_ISSUE = "cementing_issue"
    TORQUE_SPIKE = "torque_spike"
    OVERPRESSURE = "overpressure"
    FISHING = "fishing"
    NPT_OTHER = "npt_other"
    OTHER = "other"


class Confidence(str, Enum):
    HIGH = "high"      # value explicitly stated in text, unambiguous
    MEDIUM = "medium"  # value inferred from context, likely correct
    LOW = "low"        # value uncertain / OCR was degraded / conflicting text


class WellHeader(BaseModel):
    """Anchors every event to a real well record."""
    well_id: str = Field(..., description="Well name/UWI exactly as it appears in the document")
    operator: Optional[str] = None
    field_name: Optional[str] = None
    spud_date: Optional[date] = None
    completion_date: Optional[date] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_depth_m: Optional[float] = Field(None, description="Total depth in metres")

    @field_validator("latitude")
    @classmethod
    def lat_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("latitude out of range (-90 to 90)")
        return v

    @field_validator("longitude")
    @classmethod
    def lon_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("longitude out of range (-180 to 180)")
        return v


class DrillingEvent(BaseModel):
    """One incident / lesson-learned record, extracted from narrative text."""
    well_id: str = Field(..., description="Must match the WellHeader.well_id for this document")
    event_type: EventType
    depth_m: Optional[float] = Field(None, description="Measured depth in metres, null if not stated")
    formation: Optional[str] = None
    event_date: Optional[date] = None
    description: str = Field(..., description="What happened (the EVENT)")
    symptom: Optional[str] = Field(None, description="Observed indicator, e.g. 'torque increased sharply'")
    action_taken: Optional[str] = Field(None, description="Mitigation / response taken (the ACTION)")
    confidence: Confidence = Confidence.MEDIUM
    source_page: Optional[int] = Field(None, description="Page number in source doc this was extracted from")
    source_section: Optional[str] = Field(None, description="Section or heading in source document, when available")
    source_snippet: Optional[str] = Field(
        None, description="Short verbatim excerpt supporting this record, for traceability"
    )


class EventNearQuery(BaseModel):
    """Query parameters for offset well correlation near a target well/depth."""
    well_id: str = Field(..., min_length=1, max_length=200)
    depth_m: float = Field(..., ge=0, le=100000)
    window_m: float = Field(default=100.0, gt=0, le=10000, description="Depth window search radius (+/- metres)")
    formation: Optional[str] = None


class EventFilterParams(BaseModel):
    """Filter parameters for querying historical drilling incidents."""
    well_id: Optional[str] = None
    event_type: Optional[EventType] = None
    formation: Optional[str] = None
    min_depth_m: Optional[float] = None
    max_depth_m: Optional[float] = None
    min_confidence: Optional[Confidence] = None
