"""
well_program_schemas.py
=======================
Data contracts defining geological formation tops, casing programs,
cementing records, and drilling mud properties for the GeoDrill AI platform.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class CasingType(str, Enum):
    CONDUCTOR = "conductor"
    SURFACE = "surface"
    INTERMEDIATE = "intermediate"
    PRODUCTION = "production"
    LINER = "liner"


class FormationTop(BaseModel):
    """Geological formation boundary depth and lithological characteristics."""
    well_id: str = Field(..., description="Well name/UWI identifier")
    formation_name: str = Field(..., description="Name of the stratigraphic unit or formation")
    top_depth_m: float = Field(..., description="Top boundary measured depth in metres")
    base_depth_m: Optional[float] = Field(None, description="Base boundary measured depth in metres, if stated")
    lithology_notes: Optional[str] = Field(None, description="Lithology or rock type description")
    source_page: Optional[int] = Field(None, description="Page number in source doc")
    source_snippet: Optional[str] = Field(
        None, description="Verbatim excerpt (<25 words) supporting this record"
    )


class CasingProgram(BaseModel):
    """Casing string specification and set depth."""
    well_id: str = Field(..., description="Well name/UWI identifier")
    casing_type: CasingType = Field(..., description="Standard casing classification")
    depth_set_m: float = Field(..., description="Setting depth in metres (shoe depth)")
    size_inches: Optional[float] = Field(None, description="Outer diameter of casing in inches")
    weight_ppf: Optional[float] = Field(None, description="Nominal pipe weight in pounds per foot (ppf)")
    source_page: Optional[int] = Field(None, description="Page number in source doc")
    source_snippet: Optional[str] = Field(
        None, description="Verbatim excerpt (<25 words) supporting this record"
    )


class CementingRecord(BaseModel):
    """Cement slurry placement, volumes, and barrier verification data."""
    well_id: str = Field(..., description="Well name/UWI identifier")
    casing_stage: Optional[str] = Field(None, description="Casing stage or string cemented")
    cement_type: Optional[str] = Field(None, description="Class or blend of cement used")
    volume_bbl: Optional[float] = Field(None, description="Total cement slurry volume pumped in barrels")
    top_of_cement_m: Optional[float] = Field(None, description="Top of cement (TOC) depth in metres")
    issues_noted: Optional[str] = Field(None, description="Operational anomalies, losses, or channeling noted")
    source_page: Optional[int] = Field(None, description="Page number in source doc")
    source_snippet: Optional[str] = Field(
        None, description="Verbatim excerpt (<25 words) supporting this record"
    )


class MudProgramEntry(BaseModel):
    """Drilling fluid system properties across a specific depth interval."""
    well_id: str = Field(..., description="Well name/UWI identifier")
    depth_interval_start_m: float = Field(..., description="Start of depth interval in metres")
    depth_interval_end_m: Optional[float] = Field(None, description="End of depth interval in metres")
    mud_type: Optional[str] = Field(None, description="Mud system type, e.g. WBM, OBM, SOBM")
    mud_weight_sg: Optional[float] = Field(None, description="Mud density in specific gravity (SG)")
    losses_observed: Optional[str] = Field(None, description="Observed fluid losses or seepage")
    source_page: Optional[int] = Field(None, description="Page number in source doc")
    source_snippet: Optional[str] = Field(
        None, description="Verbatim excerpt (<25 words) supporting this record"
    )


class ProgramDataExtraction(BaseModel):
    """Container model for the second-pass extraction of well program data."""
    formation_tops: List[FormationTop] = Field(default_factory=list)
    casing_program: List[CasingProgram] = Field(default_factory=list)
    cementing_records: List[CementingRecord] = Field(default_factory=list)
    mud_program: List[MudProgramEntry] = Field(default_factory=list)
    confidence: Optional[str] = Field("medium", description="Confidence level of program data extraction")
    processing_notes: Optional[str] = None
