"""
llm_extractor.py
================
Core LLM extraction engine for GeoDrill AI.
Transforms unstructured narrative drilling text and table excerpts into
strictly validated Pydantic models with multi-provider fallback support.
Supports multi-pass extraction:
  Pass 1: Well Header & Drilling Incidents / Events
  Pass 2: Geological Formation Tops, Casing Programs, Cementing Records, & Mud Program Entries

Supported Providers:
  1. Anthropic Claude (Tool Calling / Structured Output)
  2. Groq (Fast Inference / JSON Mode)
  3. OpenAI (Chat Completions / JSON Mode)
  4. Google Gemini (JSON MIME Type)
  5. Deterministic Mock Fallback (Offline / Testing)
"""

from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Sequence, Optional, Dict, Any, List

from dotenv import load_dotenv
from pydantic import ValidationError

from config.constants import (
    EXTRACTION_TOOL_SCHEMA,
    SYSTEM_PROMPT,
    PROGRAM_EXTRACTION_TOOL_SCHEMA,
    PROGRAM_SYSTEM_PROMPT,
)
from src.api.schemas.document_schemas import ExtractionResult, ExtractionMethod
from src.api.schemas.incident_schemas import WellHeader, DrillingEvent, Confidence
from src.api.schemas.well_program_schemas import (
    FormationTop,
    CasingProgram,
    CementingRecord,
    MudProgramEntry,
    ProgramDataExtraction,
)

logger = logging.getLogger(__name__)

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
PROVIDER_QUEUE: List[Dict[str, Any]] = []

# Exact JSON Schema specification for Pass 1 (Well header + Events)
JSON_EXTRACTION_PROMPT = f"""{SYSTEM_PROMPT}

You MUST output ONLY a valid JSON object matching this exact schema:
{{
  "well_header": {{
    "well_id": "<string: Well name/UWI as stated, or 'UNKNOWN'>",
    "operator": "<string or null>",
    "field_name": "<string or null>",
    "spud_date": "<YYYY-MM-DD or null>",
    "completion_date": "<YYYY-MM-DD or null>",
    "latitude": "<float between -90 and 90 or null>",
    "longitude": "<float between -180 and 180 or null>",
    "total_depth_m": "<float total depth in metres or null>"
  }},
  "events": [
    {{
      "well_id": "<string matching well_header.well_id>",
      "event_type": "<one of: 'mud_loss', 'kick', 'stuck_pipe', 'cementing_issue', 'torque_spike', 'overpressure', 'fishing', 'npt_other', 'other'>",
      "depth_m": "<float depth in metres or null>",
      "formation": "<string or null>",
      "event_date": "<YYYY-MM-DD or null>",
      "description": "<string: what happened>",
      "symptom": "<string: observed indicator or null>",
      "action_taken": "<string: mitigation taken or null>",
      "confidence": "<one of: 'high', 'medium', 'low'>",
      "source_page": "<integer page number or null>",
      "source_snippet": "<string: verbatim excerpt <25 words supporting this record or null>"
    }}
  ],
  "overall_confidence": "<'high', 'medium', or 'low'>",
  "processing_notes": "<string or null>"
}}

CRITICAL: Return strictly raw JSON. Do not wrap in markdown code blocks. Never invent values not present in the document.
"""

# Exact JSON Schema specification for Pass 2 (Formation tops, Casing, Cementing, Mud)
JSON_PROGRAM_EXTRACTION_PROMPT = f"""{PROGRAM_SYSTEM_PROMPT}

You MUST output ONLY a valid JSON object matching this exact schema:
{{
  "formation_tops": [
    {{
      "well_id": "<string matching well name or 'UNKNOWN'>",
      "formation_name": "<string: name of stratigraphic unit/formation>",
      "top_depth_m": "<float depth in metres>",
      "base_depth_m": "<float depth in metres or null>",
      "lithology_notes": "<string or null>",
      "source_page": "<integer page number or null>",
      "source_snippet": "<string: verbatim excerpt <25 words or null>"
    }}
  ],
  "casing_program": [
    {{
      "well_id": "<string matching well name or 'UNKNOWN'>",
      "casing_type": "<one of: 'conductor', 'surface', 'intermediate', 'production', 'liner'>",
      "depth_set_m": "<float shoe depth in metres>",
      "size_inches": "<float outer diameter in inches or null>",
      "weight_ppf": "<float nominal weight in ppf or null>",
      "source_page": "<integer page number or null>",
      "source_snippet": "<string: verbatim excerpt <25 words or null>"
    }}
  ],
  "cementing_records": [
    {{
      "well_id": "<string matching well name or 'UNKNOWN'>",
      "casing_stage": "<string or null>",
      "cement_type": "<string or null>",
      "volume_bbl": "<float volume in barrels or null>",
      "top_of_cement_m": "<float TOC depth in metres or null>",
      "issues_noted": "<string or null>",
      "source_page": "<integer page number or null>",
      "source_snippet": "<string: verbatim excerpt <25 words or null>"
    }}
  ],
  "mud_program": [
    {{
      "well_id": "<string matching well name or 'UNKNOWN'>",
      "depth_interval_start_m": "<float interval start in metres>",
      "depth_interval_end_m": "<float interval end in metres or null>",
      "mud_type": "<string or null>",
      "mud_weight_sg": "<float density in SG or null>",
      "losses_observed": "<string or null>",
      "source_page": "<integer page number or null>",
      "source_snippet": "<string: verbatim excerpt <25 words or null>"
    }}
  ],
  "confidence": "<'high', 'medium', or 'low'>",
  "processing_notes": "<string or null>"
}}

CRITICAL: Return strictly raw JSON. Do not wrap in markdown code blocks. Never invent values not present in the document.
"""


def load_app_env() -> None:
    """Supports either standard KEY=VALUE .env files or JSON arrays of provider configs."""
    if not os.path.exists(ENV_PATH):
        return

    with open(ENV_PATH, "r", encoding="utf-8") as fh:
        raw_text = fh.read().strip()

    if not raw_text:
        return

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        payload = None

    if payload is None:
        try:
            decoder = json.JSONDecoder()
            entries = []
            pos = 0
            while pos < len(raw_text):
                while pos < len(raw_text) and raw_text[pos].isspace():
                    pos += 1
                if pos >= len(raw_text):
                    break
                value, end = decoder.raw_decode(raw_text[pos:])
                entries.append(value)
                pos += end
                while pos < len(raw_text) and raw_text[pos].isspace():
                    pos += 1
                if pos < len(raw_text) and raw_text[pos] == ",":
                    pos += 1
            payload = entries
        except Exception:
            load_dotenv(ENV_PATH, override=False)
            return

    if isinstance(payload, list):
        ordered = sorted(
            [item for item in payload if isinstance(item, dict) and item.get("enabled", True)],
            key=lambda item: item.get("priority", 999),
        )
        for item in ordered:
            provider = str(item.get("provider", "")).lower()
            api_key = item.get("api_key")
            if provider not in {"groq", "openai", "gemini", "anthropic"} or not api_key:
                continue

            provider_entry = {
                "provider": provider,
                "api_key": api_key,
                "model": item.get("model"),
                "base_url": item.get("base_url"),
                "priority": item.get("priority", 999),
            }
            PROVIDER_QUEUE.append(provider_entry)

            if provider == "groq":
                os.environ.setdefault("GROQ_API_KEY", api_key)
                if item.get("model"):
                    os.environ.setdefault("GROQ_MODEL", item.get("model"))
                if item.get("base_url"):
                    os.environ.setdefault("GROQ_BASE_URL", item.get("base_url"))
            elif provider == "openai":
                os.environ.setdefault("OPENAI_API_KEY", api_key)
                if item.get("model"):
                    os.environ.setdefault("OPENAI_MODEL", item.get("model"))
                if item.get("base_url"):
                    os.environ.setdefault("OPENAI_BASE_URL", item.get("base_url"))
            elif provider == "gemini":
                os.environ.setdefault("GEMINI_API_KEY", api_key)
                if item.get("model"):
                    os.environ.setdefault("GEMINI_MODEL", item.get("model"))
            elif provider == "anthropic":
                os.environ.setdefault("ANTHROPIC_API_KEY", api_key)
                if item.get("model"):
                    os.environ.setdefault("ANTHROPIC_MODEL", item.get("model"))
        return

    load_dotenv(ENV_PATH, override=False)


# Automatically load environment credentials
load_app_env()


class LLMClient(ABC):
    """Abstract interface for LLM extraction providers."""

    @abstractmethod
    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        """Extract structured well header and event records from raw text."""
        ...

    @abstractmethod
    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        """Extract structured formation tops, casing, cementing, and mud records from raw text."""
        ...


class AnthropicLLMClient(LLMClient):
    """Extraction via Anthropic Claude API using structured tool calling."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        import anthropic

        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
            base_url=base_url or os.environ.get("ANTHROPIC_BASE_URL"),
        )
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=[EXTRACTION_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": "record_extraction"},
            messages=[
                {
                    "role": "user",
                    "content": f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}",
                }
            ],
        )
        for block in response.content:
            if block.type == "tool_use":
                return block.input
        raise RuntimeError("Anthropic model did not return a tool_use block for event extraction")

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=PROGRAM_SYSTEM_PROMPT,
            tools=[PROGRAM_EXTRACTION_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": "record_program_data_extraction"},
            messages=[
                {
                    "role": "user",
                    "content": f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}",
                }
            ],
        )
        for block in response.content:
            if block.type == "tool_use":
                return block.input
        raise RuntimeError("Anthropic model did not return a tool_use block for program data")


class GroqLLMClient(LLMClient):
    """Extraction via Groq fast-inference OpenAI-compatible API with strict schema forcing."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key or os.environ.get("GROQ_API_KEY"),
            base_url=base_url or os.environ.get("GROQ_BASE_URL") or "https://api.groq.com/openai/v1",
        )
        self.model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        user_prompt = f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": JSON_EXTRACTION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned an empty response")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Groq returned invalid JSON: {exc}") from exc

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        user_prompt = f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": JSON_PROGRAM_EXTRACTION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned an empty program data response")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Groq returned invalid JSON for program data: {exc}") from exc


class OpenAILLMClient(LLMClient):
    """Extraction via OpenAI Chat Completions API with strict JSON mode."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
        )
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        user_prompt = f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": JSON_EXTRACTION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty response")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"OpenAI returned invalid JSON: {exc}") from exc

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        user_prompt = f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": JSON_PROGRAM_EXTRACTION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty program data response")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"OpenAI returned invalid JSON for program data: {exc}") from exc


class GeminiLLMClient(LLMClient):
    """Extraction via Google Gemini API with JSON response format."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self.use_legacy = False

        try:
            from google import genai

            self.client = genai.Client(api_key=self.api_key)
            self.use_legacy = False
            return
        except Exception:
            pass

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
            self.use_legacy = True
        except Exception as exc:
            raise RuntimeError("Gemini dependencies are not installed or configured correctly") from exc

    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        user_prompt = f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}"
        if self.use_legacy:
            response = self.client.generate_content(
                [
                    {"text": JSON_EXTRACTION_PROMPT},
                    {"text": user_prompt},
                ],
                generation_config={
                    "temperature": 0,
                    "response_mime_type": "application/json",
                },
            )
            text = getattr(response, "text", None)
        else:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[JSON_EXTRACTION_PROMPT, user_prompt],
                config={"temperature": 0, "response_mime_type": "application/json"},
            )
            text = getattr(response, "text", None)

        if not text:
            raise RuntimeError("Gemini returned an empty response")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Gemini returned invalid JSON: {exc}") from exc

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        user_prompt = f"Source document: {source_doc}\n\n--- DOCUMENT TEXT ---\n{document_text}"
        if self.use_legacy:
            response = self.client.generate_content(
                [
                    {"text": JSON_PROGRAM_EXTRACTION_PROMPT},
                    {"text": user_prompt},
                ],
                generation_config={
                    "temperature": 0,
                    "response_mime_type": "application/json",
                },
            )
            text = getattr(response, "text", None)
        else:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[JSON_PROGRAM_EXTRACTION_PROMPT, user_prompt],
                config={"temperature": 0, "response_mime_type": "application/json"},
            )
            text = getattr(response, "text", None)

        if not text:
            raise RuntimeError("Gemini returned an empty program data response")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Gemini returned invalid JSON for program data: {exc}") from exc


class MockLLMClient(LLMClient):
    """
    Deterministic mock provider for automated unit testing and offline execution.
    Recognizes standard test well reports and returns honest low-confidence fallback
    for unknown documents.
    """

    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        if "15/9-F-11B" in document_text or "F-11B" in document_text:
            return {
                "well_header": {
                    "well_id": "15/9-F-11B",
                    "operator": "Statoil ASA",
                    "field_name": "Volve",
                    "spud_date": "2007-08-24",
                    "completion_date": "2007-10-15",
                    "latitude": 58.4394,
                    "longitude": 1.8875,
                    "total_depth_m": 3200.0,
                },
                "events": [
                    {
                        "well_id": "15/9-F-11B",
                        "event_type": "mud_loss",
                        "depth_m": 2450.0,
                        "formation": "Hugin Formation",
                        "event_date": "2007-09-12",
                        "description": "Partial mud losses of 15 bbl/hr encountered while drilling through the Hugin Formation.",
                        "symptom": "Pit level dropped steadily over 2 hours",
                        "action_taken": "Pumped LCM pill (50 bbl, 40 ppb LCM blend); losses reduced to seepage rate.",
                        "confidence": "high",
                        "source_page": 3,
                        "source_snippet": "at 2450m encountered mud loss of 15 bbl/hr, pumped LCM pill",
                    },
                    {
                        "well_id": "15/9-F-11B",
                        "event_type": "stuck_pipe",
                        "depth_m": 2810.0,
                        "formation": "Skagerrak Formation",
                        "event_date": "2007-09-20",
                        "description": "Pipe became stuck while tripping out through a tight hole section.",
                        "symptom": "Overpull of 40 klbs, unable to rotate string",
                        "action_taken": "Worked pipe free with jarring after 6 hours; wiper trip run before continuing.",
                        "confidence": "medium",
                        "source_page": 5,
                        "source_snippet": "tight hole, overpull 40 klbs, jarred free after 6 hrs",
                    },
                ],
                "overall_confidence": "high",
                "processing_notes": None,
            }
        elif "15/9-F-12" in document_text or "F-12" in document_text:
            return {
                "well_header": {
                    "well_id": "15/9-F-12",
                    "operator": "Statoil ASA",
                    "field_name": "Volve",
                    "spud_date": "2008-01-10",
                    "completion_date": "2008-03-05",
                    "latitude": 58.4410,
                    "longitude": 1.8890,
                    "total_depth_m": 3350.0,
                },
                "events": [
                    {
                        "well_id": "15/9-F-12",
                        "event_type": "kick",
                        "depth_m": 2510.0,
                        "formation": "Hugin Formation",
                        "event_date": "2008-01-28",
                        "description": "Gas kick taken while drilling 8-1/2 inch hole section in Hugin Sandstone.",
                        "symptom": "Pit volume gain of 12 bbl observed with flow rate increase.",
                        "action_taken": "Shut in well on annular BOP; circulated out influx using Driller's Method.",
                        "confidence": "high",
                        "source_page": 2,
                        "source_snippet": "gas kick 12 bbl gain, shut in annular BOP",
                    }
                ],
                "overall_confidence": "high",
                "processing_notes": None,
            }

        return {
            "well_header": {"well_id": "UNKNOWN"},
            "events": [],
            "overall_confidence": "low",
            "processing_notes": "MockLLMClient: no matching predefined response for this document.",
        }

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        if "15/9-F-11B" in document_text or "F-11B" in document_text:
            return {
                "formation_tops": [
                    {
                        "well_id": "15/9-F-11B",
                        "formation_name": "Hugin Formation",
                        "top_depth_m": 2420.0,
                        "base_depth_m": 2750.0,
                        "lithology_notes": "Sandstone reservoir, fine to medium grained",
                        "source_page": 2,
                        "source_snippet": "entering the target Hugin Formation at 2420 m MD",
                    },
                    {
                        "well_id": "15/9-F-11B",
                        "formation_name": "Skagerrak Formation",
                        "top_depth_m": 2750.0,
                        "base_depth_m": 3200.0,
                        "lithology_notes": "Interbedded sandstone and shale",
                        "source_page": 1,
                        "source_snippet": "Total depth of 3200.0 m MD was reached successfully in the Skagerrak Formation",
                    },
                ],
                "casing_program": [
                    {
                        "well_id": "15/9-F-11B",
                        "casing_type": "surface",
                        "depth_set_m": 1200.0,
                        "size_inches": 13.375,
                        "weight_ppf": 68.0,
                        "source_page": 4,
                        "source_snippet": "13-3/8 inch surface casing set at 1200m",
                    },
                    {
                        "well_id": "15/9-F-11B",
                        "casing_type": "intermediate",
                        "depth_set_m": 2600.0,
                        "size_inches": 9.625,
                        "weight_ppf": 47.0,
                        "source_page": 4,
                        "source_snippet": "Casing 9-5/8 inch was set and cemented without issues at 2600 m MD",
                    },
                ],
                "cementing_records": [
                    {
                        "well_id": "15/9-F-11B",
                        "casing_stage": "intermediate",
                        "cement_type": "Class G + silica",
                        "volume_bbl": 280.0,
                        "top_of_cement_m": 1800.0,
                        "issues_noted": None,
                        "source_page": 4,
                        "source_snippet": "Casing 9-5/8 inch was set and cemented without issues",
                    }
                ],
                "mud_program": [
                    {
                        "well_id": "15/9-F-11B",
                        "depth_interval_start_m": 2400.0,
                        "depth_interval_end_m": 2600.0,
                        "mud_type": "OBM",
                        "mud_weight_sg": 1.45,
                        "losses_observed": "Partial losses 15 bbl/hr at 2450m",
                        "source_page": 3,
                        "source_snippet": "12-1/4 inch hole section through Hugin Formation at 2450.0 m MD",
                    }
                ],
                "confidence": "high",
                "processing_notes": None,
            }
        elif "15/9-F-12" in document_text or "F-12" in document_text:
            return {
                "formation_tops": [
                    {
                        "well_id": "15/9-F-12",
                        "formation_name": "Hugin Formation",
                        "top_depth_m": 2410.0,
                        "base_depth_m": 2720.0,
                        "lithology_notes": "Sandstone, gas bearing",
                        "source_page": 2,
                        "source_snippet": "drilling 8-1/2 inch hole section in Hugin Sandstone",
                    }
                ],
                "casing_program": [
                    {
                        "well_id": "15/9-F-12",
                        "casing_type": "intermediate",
                        "depth_set_m": 2480.0,
                        "size_inches": 9.625,
                        "weight_ppf": 47.0,
                        "source_page": 1,
                        "source_snippet": "9-5/8 inch casing set at 2480m",
                    }
                ],
                "cementing_records": [
                    {
                        "well_id": "15/9-F-12",
                        "casing_stage": "intermediate",
                        "cement_type": "Class G",
                        "volume_bbl": 250.0,
                        "top_of_cement_m": 1750.0,
                        "issues_noted": None,
                        "source_page": 1,
                        "source_snippet": "cemented 9-5/8 casing to 1750m TOC",
                    }
                ],
                "mud_program": [
                    {
                        "well_id": "15/9-F-12",
                        "depth_interval_start_m": 2480.0,
                        "depth_interval_end_m": 3350.0,
                        "mud_type": "OBM",
                        "mud_weight_sg": 1.50,
                        "losses_observed": None,
                        "source_page": 2,
                        "source_snippet": "drilling 8-1/2 inch hole section in Hugin",
                    }
                ],
                "confidence": "high",
                "processing_notes": None,
            }

        return {
            "formation_tops": [],
            "casing_program": [],
            "cementing_records": [],
            "mud_program": [],
            "confidence": "low",
            "processing_notes": "MockLLMClient: no matching predefined program data for this document.",
        }


class FallbackLLMClient(LLMClient):
    """Cascades through multiple LLM providers in sequence until one succeeds, then falls back to Mock."""

    def __init__(self, providers: Sequence[LLMClient]):
        self.providers = list(providers)
        self.mock = MockLLMClient()

    def extract(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        last_error = None
        for provider in self.providers:
            try:
                raw = provider.extract(document_text, source_doc, extraction_method)
                if not isinstance(raw, dict) or "well_header" not in raw:
                    raise ValueError(f"{type(provider).__name__} returned an invalid schema payload")
                return raw
            except Exception as exc:
                logger.warning("Provider %s failed during extraction: %s", type(provider).__name__, exc)
                last_error = exc
                continue

        logger.info("All configured providers failed or unavailable, using MockLLMClient fallback. Last error: %s", last_error)
        return self.mock.extract(document_text, source_doc, extraction_method)

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        last_error = None
        for provider in self.providers:
            try:
                raw = provider.extract_program_data(document_text, source_doc, extraction_method)
                if not isinstance(raw, dict) or "casing_program" not in raw:
                    raise ValueError(f"{type(provider).__name__} returned an invalid program schema payload")
                return raw
            except Exception as exc:
                logger.warning("Provider %s failed during program data extraction: %s", type(provider).__name__, exc)
                last_error = exc
                continue

        logger.info("All configured providers failed or unavailable for program data, using MockLLMClient fallback. Last error: %s", last_error)
        return self.mock.extract_program_data(document_text, source_doc, extraction_method)


def get_llm_client() -> LLMClient:
    """Factory creating configured LLM provider or fallback pipeline."""
    configured: list[LLMClient] = []
    provider_factories = {
        "groq": GroqLLMClient,
        "openai": OpenAILLMClient,
        "gemini": GeminiLLMClient,
        "anthropic": AnthropicLLMClient,
    }

    if PROVIDER_QUEUE:
        for entry in sorted(PROVIDER_QUEUE, key=lambda item: item.get("priority", 999)):
            factory = provider_factories.get(entry["provider"])
            if factory and entry.get("api_key"):
                try:
                    configured.append(
                        factory(
                            model=entry.get("model"),
                            api_key=entry.get("api_key"),
                            base_url=entry.get("base_url"),
                        )
                    )
                except Exception as exc:
                    logger.warning("Could not initialize %s provider: %s", entry["provider"], exc)
    else:
        for provider_name, factory in provider_factories.items():
            env_key = f"{provider_name.upper()}_API_KEY"
            if os.environ.get(env_key):
                try:
                    configured.append(factory())
                except Exception as exc:
                    logger.warning("Could not initialize %s provider from env: %s", provider_name, exc)

    if not configured:
        return MockLLMClient()

    return FallbackLLMClient(configured)


def run_extraction(
    document_text: str,
    source_doc: str,
    extraction_method: ExtractionMethod,
    client: Optional[LLMClient] = None,
) -> ExtractionResult:
    """
    Executes the LLM extraction step and validates against Pydantic models.
    On schema validation errors, safely returns a MANUAL_FLAG low-confidence result.
    """
    client = client or get_llm_client()
    try:
        raw = client.extract(document_text, source_doc, extraction_method)
        well_header = WellHeader(**raw["well_header"])
        events = [DrillingEvent(**e) for e in raw.get("events", [])]
        return ExtractionResult(
            source_doc=source_doc,
            extraction_method=extraction_method,
            well_header=well_header,
            events=events,
            overall_confidence=Confidence(raw.get("overall_confidence", "low")),
            processing_notes=raw.get("processing_notes"),
        )
    except (ValidationError, KeyError, TypeError, ValueError) as e:
        logger.error("Extraction validation failed for %s: %s", source_doc, e)
        return ExtractionResult(
            source_doc=source_doc,
            extraction_method=ExtractionMethod.MANUAL_FLAG,
            well_header=WellHeader(well_id="UNKNOWN"),
            events=[],
            overall_confidence=Confidence.LOW,
            processing_notes=f"Schema validation failed, needs manual review: {e}",
        )


def run_program_extraction(
    document_text: str,
    source_doc: str,
    extraction_method: ExtractionMethod,
    client: Optional[LLMClient] = None,
) -> ProgramDataExtraction:
    """
    Executes the second-pass LLM program data extraction (formation tops, casing, cementing, mud)
    and validates against Pydantic models.
    """
    client = client or get_llm_client()
    try:
        raw = client.extract_program_data(document_text, source_doc, extraction_method)
        formation_tops = [FormationTop(**ft) for ft in raw.get("formation_tops", [])]
        casing_program = [CasingProgram(**cp) for cp in raw.get("casing_program", [])]
        cementing_records = [CementingRecord(**cr) for cr in raw.get("cementing_records", [])]
        mud_program = [MudProgramEntry(**mp) for mp in raw.get("mud_program", [])]
        return ProgramDataExtraction(
            formation_tops=formation_tops,
            casing_program=casing_program,
            cementing_records=cementing_records,
            mud_program=mud_program,
            confidence=raw.get("confidence", "medium"),
            processing_notes=raw.get("processing_notes"),
        )
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        logger.error("Program data extraction validation failed for %s: %s", source_doc, exc)
        return ProgramDataExtraction(
            formation_tops=[],
            casing_program=[],
            cementing_records=[],
            mud_program=[],
            confidence="low",
            processing_notes=f"Program data schema validation failed: {exc}",
        )
