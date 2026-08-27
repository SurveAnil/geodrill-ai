"""
constants.py
============
Global constants, prompts, and extraction schemas for the GeoDrill AI platform.
"""

from __future__ import annotations

# Text density threshold: minimum average characters per page to consider a PDF digital-native
MIN_CHARS_PER_PAGE_FOR_DIGITAL = 40

# JSON Schema for LLM tool_use structured extraction
EXTRACTION_TOOL_SCHEMA = {
    "name": "record_extraction",
    "description": "Record structured well header and drilling event data extracted from a document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "well_header": {
                "type": "object",
                "properties": {
                    "well_id": {"type": "string"},
                    "operator": {"type": ["string", "null"]},
                    "field_name": {"type": ["string", "null"]},
                    "spud_date": {"type": ["string", "null"], "description": "YYYY-MM-DD or null"},
                    "completion_date": {"type": ["string", "null"], "description": "YYYY-MM-DD or null"},
                    "latitude": {"type": ["number", "null"]},
                    "longitude": {"type": ["number", "null"]},
                    "total_depth_m": {"type": ["number", "null"]},
                },
                "required": ["well_id"],
            },
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "well_id": {"type": "string"},
                        "event_type": {
                            "type": "string",
                            "enum": [
                                "mud_loss",
                                "kick",
                                "stuck_pipe",
                                "cementing_issue",
                                "torque_spike",
                                "overpressure",
                                "fishing",
                                "npt_other",
                                "other",
                            ],
                        },
                        "depth_m": {"type": ["number", "null"]},
                        "formation": {"type": ["string", "null"]},
                        "event_date": {"type": ["string", "null"], "description": "YYYY-MM-DD or null"},
                        "description": {"type": "string"},
                        "symptom": {"type": ["string", "null"]},
                        "action_taken": {"type": ["string", "null"]},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                        "source_page": {"type": ["integer", "null"]},
                        "source_snippet": {
                            "type": ["string", "null"],
                            "description": "Short verbatim excerpt (<25 words) supporting this record",
                        },
                    },
                    "required": ["well_id", "event_type", "description", "confidence"],
                },
            },
            "overall_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "processing_notes": {"type": ["string", "null"]},
        },
        "required": ["well_header", "events", "overall_confidence"],
    },
}

SYSTEM_PROMPT = """You are a drilling-domain data extraction engine for an oil & gas offset-well \
knowledge system. You read raw text extracted from Well Completion Reports and Daily Drilling \
Reports and convert it into structured records using the record_extraction tool.

STRICT RULES:
1. Never invent or estimate a value that is not stated in the text. If a field is not present, \
set it to null. Do not fill dates, depths, or coordinates with plausible-looking guesses.
2. Extract EVERY distinct drilling incident/event mentioned (mud loss, kick, stuck pipe, \
cementing issue, torque spike, overpressure, fishing operation, or other NPT event) as a \
separate event record, even if several occur in one document.
3. For every event, include a short verbatim source_snippet (under 25 words) copied from the \
text that supports the extracted values, plus the page number it came from.
4. Set confidence to "low" for any record where the source text was ambiguous, contradictory, \
or where OCR artifacts made the reading uncertain.
5. Use the EVENT / SYMPTOM / ACTION structure: description = what happened, symptom = the \
observed indicator (if stated), action_taken = the mitigation/response (if stated).
6. Dates must be formatted YYYY-MM-DD or null if not determinable.
7. If the document contains no identifiable well name, set well_id to "UNKNOWN" and note this \
in processing_notes."""

# JSON Schema for second-pass well program data extraction (formation tops, casing, cementing, mud)
PROGRAM_EXTRACTION_TOOL_SCHEMA = {
    "name": "record_program_data_extraction",
    "description": "Record structured formation tops, casing program, cementing records, and mud program entries extracted from a document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "formation_tops": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "well_id": {"type": "string"},
                        "formation_name": {"type": "string"},
                        "top_depth_m": {"type": "number"},
                        "base_depth_m": {"type": ["number", "null"]},
                        "lithology_notes": {"type": ["string", "null"]},
                        "source_page": {"type": ["integer", "null"]},
                        "source_snippet": {
                            "type": ["string", "null"],
                            "description": "Short verbatim excerpt (<25 words) supporting this record",
                        },
                    },
                    "required": ["well_id", "formation_name", "top_depth_m"],
                },
            },
            "casing_program": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "well_id": {"type": "string"},
                        "casing_type": {
                            "type": "string",
                            "enum": ["conductor", "surface", "intermediate", "production", "liner"],
                        },
                        "depth_set_m": {"type": "number"},
                        "size_inches": {"type": ["number", "null"]},
                        "weight_ppf": {"type": ["number", "null"]},
                        "source_page": {"type": ["integer", "null"]},
                        "source_snippet": {
                            "type": ["string", "null"],
                            "description": "Short verbatim excerpt (<25 words) supporting this record",
                        },
                    },
                    "required": ["well_id", "casing_type", "depth_set_m"],
                },
            },
            "cementing_records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "well_id": {"type": "string"},
                        "casing_stage": {"type": ["string", "null"]},
                        "cement_type": {"type": ["string", "null"]},
                        "volume_bbl": {"type": ["number", "null"]},
                        "top_of_cement_m": {"type": ["number", "null"]},
                        "issues_noted": {"type": ["string", "null"]},
                        "source_page": {"type": ["integer", "null"]},
                        "source_snippet": {
                            "type": ["string", "null"],
                            "description": "Short verbatim excerpt (<25 words) supporting this record",
                        },
                    },
                    "required": ["well_id"],
                },
            },
            "mud_program": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "well_id": {"type": "string"},
                        "depth_interval_start_m": {"type": "number"},
                        "depth_interval_end_m": {"type": ["number", "null"]},
                        "mud_type": {"type": ["string", "null"]},
                        "mud_weight_sg": {"type": ["number", "null"]},
                        "losses_observed": {"type": ["string", "null"]},
                        "source_page": {"type": ["integer", "null"]},
                        "source_snippet": {
                            "type": ["string", "null"],
                            "description": "Short verbatim excerpt (<25 words) supporting this record",
                        },
                    },
                    "required": ["well_id", "depth_interval_start_m"],
                },
            },
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "processing_notes": {"type": ["string", "null"]},
        },
        "required": ["formation_tops", "casing_program", "cementing_records", "mud_program"],
    },
}

PROGRAM_SYSTEM_PROMPT = """You are a drilling-domain well-program data extraction engine for an oil & gas \
knowledge system. You read raw text extracted from Well Completion Reports and Daily Drilling Reports and \
convert geological formation tops, casing programs, cementing records, and mud program entries into \
structured records using the record_program_data_extraction tool.

STRICT RULES:
1. Never invent or estimate a value that is not stated in the text. If a field is not present, \
set it to null. Do not fill depths, sizes, or weights with plausible-looking guesses.
2. Extract EVERY mentioned formation top, casing string, cementing job, and mud property entry as \
separate records.
3. For every record, include a short verbatim source_snippet (under 25 words) copied from the \
text that supports the extracted values, plus the page number it came from.
4. Set confidence to "low" for any record where the source text was ambiguous, contradictory, \
or where OCR artifacts made the reading uncertain.
5. Casing type must be one of: 'conductor', 'surface', 'intermediate', 'production', 'liner'.
6. If the document contains no identifiable well name, set well_id to "UNKNOWN" and note this \
in processing_notes."""
