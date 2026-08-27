"""
test_well_program_schemas.py
============================
Validation tests for well program data schemas: FormationTop, CasingProgram,
CementingRecord, MudProgramEntry, and expanded ExtractionResult container.
"""

import pytest
from pydantic import ValidationError

from src.api.schemas.document_schemas import ExtractionMethod, ExtractionResult
from src.api.schemas.incident_schemas import Confidence, WellHeader
from src.api.schemas.well_program_schemas import (
    CasingType,
    FormationTop,
    CasingProgram,
    CementingRecord,
    MudProgramEntry,
    ProgramDataExtraction,
)


def test_formation_top_schema_valid():
    top = FormationTop(
        well_id="15/9-F-11B",
        formation_name="Hugin Formation",
        top_depth_m=2420.0,
        base_depth_m=2750.0,
        lithology_notes="Sandstone reservoir",
        source_page=2,
        source_snippet="entering the target Hugin Formation at 2420 m MD",
    )
    assert top.well_id == "15/9-F-11B"
    assert top.formation_name == "Hugin Formation"
    assert top.top_depth_m == 2420.0
    assert top.base_depth_m == 2750.0
    assert top.source_page == 2


def test_formation_top_null_if_absent():
    top = FormationTop(
        well_id="15/9-F-12",
        formation_name="Skagerrak Formation",
        top_depth_m=2750.0,
    )
    assert top.base_depth_m is None
    assert top.lithology_notes is None
    assert top.source_page is None
    assert top.source_snippet is None


def test_casing_program_valid():
    cp = CasingProgram(
        well_id="15/9-F-11B",
        casing_type=CasingType.INTERMEDIATE,
        depth_set_m=2600.0,
        size_inches=9.625,
        weight_ppf=47.0,
        source_page=4,
        source_snippet="Casing 9-5/8 inch was set at 2600 m MD",
    )
    assert cp.casing_type == CasingType.INTERMEDIATE
    assert cp.depth_set_m == 2600.0
    assert cp.size_inches == 9.625


def test_casing_program_invalid_enum():
    with pytest.raises(ValidationError):
        CasingProgram(
            well_id="15/9-F-11B",
            casing_type="non_existent_casing_type",  # type: ignore
            depth_set_m=2600.0,
        )


def test_cementing_record_valid():
    cr = CementingRecord(
        well_id="15/9-F-11B",
        casing_stage="intermediate",
        cement_type="Class G + silica",
        volume_bbl=280.0,
        top_of_cement_m=1800.0,
        issues_noted=None,
        source_page=4,
        source_snippet="cemented without issues with 280 bbl Class G",
    )
    assert cr.volume_bbl == 280.0
    assert cr.top_of_cement_m == 1800.0
    assert cr.issues_noted is None


def test_mud_program_entry_valid():
    mp = MudProgramEntry(
        well_id="15/9-F-11B",
        depth_interval_start_m=2400.0,
        depth_interval_end_m=2600.0,
        mud_type="OBM",
        mud_weight_sg=1.45,
        losses_observed="Partial losses 15 bbl/hr",
        source_page=3,
        source_snippet="drilled using OBM with mud weight 1.45 SG",
    )
    assert mp.depth_interval_start_m == 2400.0
    assert mp.mud_weight_sg == 1.45
    assert mp.losses_observed == "Partial losses 15 bbl/hr"


def test_extraction_result_with_well_program():
    res = ExtractionResult(
        source_doc="wcr_test.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=WellHeader(well_id="15/9-F-11B"),
        events=[],
        formation_tops=[
            FormationTop(well_id="15/9-F-11B", formation_name="Hugin", top_depth_m=2420.0)
        ],
        casing_program=[
            CasingProgram(well_id="15/9-F-11B", casing_type=CasingType.SURFACE, depth_set_m=1200.0)
        ],
        cementing_records=[
            CementingRecord(well_id="15/9-F-11B", volume_bbl=250.0)
        ],
        mud_program=[
            MudProgramEntry(well_id="15/9-F-11B", depth_interval_start_m=1200.0, mud_type="WBM")
        ],
    )
    assert len(res.formation_tops) == 1
    assert len(res.casing_program) == 1
    assert len(res.cementing_records) == 1
    assert len(res.mud_program) == 1
