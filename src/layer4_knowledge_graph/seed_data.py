"""Deterministic fictional NWIS foundation records used for local development."""

from datetime import date

from src.api.schemas.document_schemas import ExtractionMethod, ExtractionResult
from src.api.schemas.incident_schemas import Confidence, DrillingEvent, EventType, WellHeader
from src.api.schemas.well_program_schemas import (
    CasingProgram,
    CasingType,
    CementingRecord,
    FormationTop,
    MudProgramEntry,
)

SEED_SOURCE_DOC = "seed_oil_nwis_foundation_v1"

SEED_WELLS = [
    WellHeader(
        well_id="OIL-NWIS-01", operator="Orion Inlet Limited", field_name="Northwind Field",
        spud_date=date(2019, 4, 12), completion_date=date(2019, 6, 28),
        latitude=58.4121, longitude=1.8422, total_depth_m=3415.0,
    ),
    WellHeader(
        well_id="OIL-NWIS-02", operator="Orion Inlet Limited", field_name="Northwind Field",
        spud_date=date(2017, 8, 4), completion_date=date(2017, 10, 19),
        latitude=58.4198, longitude=1.8567, total_depth_m=3388.0,
    ),
    WellHeader(
        well_id="OIL-NWIS-03", operator="Orion Inlet Limited", field_name="Northwind Field",
        spud_date=date(2021, 2, 16), completion_date=date(2021, 4, 30),
        latitude=58.4015, longitude=1.8694, total_depth_m=3520.0,
    ),
    WellHeader(
        well_id="OIL-NWIS-04", operator="Orion Inlet Limited", field_name="Northwind Field",
        spud_date=date(2022, 6, 8), completion_date=date(2022, 8, 21),
        latitude=58.4262, longitude=1.8269, total_depth_m=3475.0,
    ),
]


def build_seed_result() -> ExtractionResult:
    """Return the complete, fictional OIL-style seed dataset."""
    # ExtractionResult represents one source document, so the three headers are
    # persisted directly by DatabaseService.seed_demo_data.
    return ExtractionResult(
        source_doc=SEED_SOURCE_DOC,
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=SEED_WELLS[0],
        events=[
            DrillingEvent(
                well_id="OIL-NWIS-02", event_type=EventType.KICK, depth_m=3118.0,
                formation="Northwind Sandstone",
                description="Transient gas kick while drilling the upper reservoir section.",
                symptom="Pit gain of 8 bbl and flow after pumps off",
                action_taken="Closed BOP, circulated to stable conditions, increased mud weight.",
                event_date=date(2017, 9, 22), confidence=Confidence.HIGH,
                severity="critical", source_page=12,
                source_snippet="Eight-barrel pit gain with flow after pumps off; BOP closed.",
            ),
            DrillingEvent(
                well_id="OIL-NWIS-02", event_type=EventType.MUD_LOSS, depth_m=3172.0,
                formation="Northwind Sandstone",
                description="Partial losses in a naturally fractured reservoir interval.",
                action_taken="Pumped 25 bbl LCM sweep and reduced rate of penetration.",
                event_date=date(2017, 9, 25), confidence=Confidence.HIGH,
                severity="high", source_page=14,
                source_snippet="Partial losses at 3172 m; 25 bbl LCM sweep pumped.",
            ),
            DrillingEvent(
                well_id="OIL-NWIS-03", event_type=EventType.STUCK_PIPE, depth_m=3096.0,
                formation="Northwind Sandstone",
                description="String became stuck during a connection across a tight shale streak.",
                action_taken="Worked pipe, circulated high-viscosity pill, and backed off 6 m.",
                event_date=date(2021, 3, 28), confidence=Confidence.MEDIUM,
                severity="high", source_page=8,
                source_snippet="String stuck during connection across tight shale streak.",
            ),
            DrillingEvent(
                well_id="OIL-NWIS-03", event_type=EventType.CEMENTING_ISSUE, depth_m=2860.0,
                formation="Harbour Shale",
                description="Cement returns were below expected volume on the intermediate string.",
                action_taken="Top-up cement job completed and pressure tested successfully.",
                event_date=date(2021, 3, 19), confidence=Confidence.HIGH,
                source_page=6, source_snippet="Returns below plan; top-up cement job completed.",
            ),
            DrillingEvent(
                well_id="OIL-NWIS-04", event_type=EventType.TORQUE_SPIKE, depth_m=3140.0,
                formation="Northwind Sandstone",
                description="Torque increased sharply while drilling a thin shale streak in the reservoir.",
                symptom="Torque rose from 18 to 29 kN-m with reduced ROP.",
                action_taken="Reduced WOB and rotary speed, circulated clean, and resumed drilling after stable torque.",
                event_date=date(2022, 7, 24), confidence=Confidence.HIGH,
                severity="medium",
                source_page=9, source_snippet="Torque spike and ROP reduction across thin shale streak.",
            ),
        ],
        formation_tops=[
            FormationTop(well_id="OIL-NWIS-01", formation_name="Harbour Shale", top_depth_m=1820, base_depth_m=2380, lithology_notes="Compact marine shale."),
            FormationTop(well_id="OIL-NWIS-01", formation_name="Northwind Sandstone", top_depth_m=3025, base_depth_m=3415, lithology_notes="Interbedded reservoir sandstone and thin shale."),
            FormationTop(well_id="OIL-NWIS-02", formation_name="Harbour Shale", top_depth_m=1795, base_depth_m=2365, lithology_notes="Compact marine shale."),
            FormationTop(well_id="OIL-NWIS-02", formation_name="Northwind Sandstone", top_depth_m=3008, base_depth_m=3388, lithology_notes="Interbedded reservoir sandstone and thin shale."),
            FormationTop(well_id="OIL-NWIS-03", formation_name="Harbour Shale", top_depth_m=1840, base_depth_m=2410, lithology_notes="Compact marine shale."),
            FormationTop(well_id="OIL-NWIS-03", formation_name="Northwind Sandstone", top_depth_m=2990, base_depth_m=3520, lithology_notes="Interbedded reservoir sandstone and thin shale."),
        ],
        casing_program=[
            CasingProgram(well_id="OIL-NWIS-01", casing_type=CasingType.SURFACE, depth_set_m=1200, size_inches=13.375, weight_ppf=68),
            CasingProgram(well_id="OIL-NWIS-01", casing_type=CasingType.INTERMEDIATE, depth_set_m=2780, size_inches=9.625, weight_ppf=47),
            CasingProgram(well_id="OIL-NWIS-02", casing_type=CasingType.SURFACE, depth_set_m=1180, size_inches=13.375, weight_ppf=68),
            CasingProgram(well_id="OIL-NWIS-02", casing_type=CasingType.INTERMEDIATE, depth_set_m=2760, size_inches=9.625, weight_ppf=47),
            CasingProgram(well_id="OIL-NWIS-03", casing_type=CasingType.SURFACE, depth_set_m=1210, size_inches=13.375, weight_ppf=68),
            CasingProgram(well_id="OIL-NWIS-03", casing_type=CasingType.INTERMEDIATE, depth_set_m=2740, size_inches=9.625, weight_ppf=47),
        ],
        cementing_records=[
            CementingRecord(well_id="OIL-NWIS-01", casing_stage="intermediate", cement_type="Class G + 35% silica", volume_bbl=310, top_of_cement_m=1680),
            CementingRecord(well_id="OIL-NWIS-02", casing_stage="intermediate", cement_type="Class G + 35% silica", volume_bbl=305, top_of_cement_m=1690),
            CementingRecord(well_id="OIL-NWIS-03", casing_stage="intermediate", cement_type="Class G + 35% silica", volume_bbl=315, top_of_cement_m=1665, issues_noted="Below planned returns; top-up job performed."),
        ],
        mud_program=[
            MudProgramEntry(well_id="OIL-NWIS-01", depth_interval_start_m=2780, depth_interval_end_m=3415, mud_type="SOBM", mud_weight_sg=1.34, losses_observed="Watch losses in reservoir section."),
            MudProgramEntry(well_id="OIL-NWIS-02", depth_interval_start_m=2760, depth_interval_end_m=3388, mud_type="SOBM", mud_weight_sg=1.35, losses_observed="Partial losses at 3172 m."),
            MudProgramEntry(well_id="OIL-NWIS-03", depth_interval_start_m=2740, depth_interval_end_m=3520, mud_type="SOBM", mud_weight_sg=1.34, losses_observed="No sustained losses recorded."),
        ],
        overall_confidence=Confidence.HIGH,
        processing_notes="Fictional deterministic seed; no operational or regulatory source.",
    )


def seed_demo_data(db) -> bool:
    """Insert the seed once; return True when rows were added."""
    return db.seed_demo_data()
