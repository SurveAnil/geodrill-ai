# GeoDrill AI — REST API Contract & Downstream Integration Guide

This document defines the REST API contract for GeoDrill AI, serving as the formal integration boundary for Stage 2 (RAG & Vector Search), Stage 3 (VLM/OCR), Stage 5 (Copilot Agent), and Frontend UI teams.

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

## 1. Document Ingestion & Extraction Endpoints

### `POST /api/v1/ingest-document`
Queues a validated `.pdf`, `.docx`, `.las`, or `.witsml` upload for background ingestion.
The upload is stored under a generated, non-user-controlled filename and removed after processing.
Returns `202 Accepted` with a durable job record (`status`: `queued`, `running`, `succeeded`, or `failed`).

### `GET /api/v1/ingestion-jobs/{job_id}`
Returns the durable status and failure detail (when applicable) for an ingestion job.
`404 Not Found` is returned for an unknown job ID. `/api/v1/ingestion-jobs` (POST) is an equivalent
job-creation route.

### `POST /api/v1/documents/process-file`
Uploads a Well Completion Report (WCR) or Daily Drilling Report (DDR) in PDF format, extracts structured well metadata and drilling events, and stores the records in the database and ChromaDB vector store.

- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `file`: PDF file binary (`.pdf`)
- **Responses**:
  - `200 OK`: Extraction successful or flagged for review.
  - `400 Bad Request`: Non-PDF file, empty file (0 bytes), or corrupt PDF syntax.
  - `500 Internal Server Error`: Unhandled server/pipeline error.

#### Example Response (Digital Native PDF):
```json
{
  "success": true,
  "source_doc": "wcr_volve_15_9_f11b.pdf",
  "extraction_result": {
    "source_doc": "wcr_volve_15_9_f11b.pdf",
    "extraction_method": "digital_parse",
    "well_header": {
      "well_id": "15/9-F-11B",
      "operator": "Statoil ASA",
      "field_name": "Volve",
      "spud_date": "2007-08-24",
      "completion_date": "2007-10-15",
      "latitude": 58.4394,
      "longitude": 1.8875,
      "total_depth_m": 3200.0
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
        "source_snippet": "at 2450m encountered mud loss of 15 bbl/hr, pumped LCM pill"
      }
    ],
    "formation_tops": [
      {
        "well_id": "15/9-F-11B",
        "formation_name": "Hugin Formation",
        "top_depth_m": 2420.0,
        "base_depth_m": 2750.0,
        "lithology_notes": "Sandstone reservoir, fine to medium grained",
        "source_page": 2,
        "source_snippet": "entering the target Hugin Formation at 2420 m MD"
      }
    ],
    "casing_program": [
      {
        "well_id": "15/9-F-11B",
        "casing_type": "intermediate",
        "depth_set_m": 2600.0,
        "size_inches": 9.625,
        "weight_ppf": 47.0,
        "source_page": 4,
        "source_snippet": "Casing 9-5/8 inch was set and cemented without issues at 2600 m MD"
      }
    ],
    "cementing_records": [
      {
        "well_id": "15/9-F-11B",
        "casing_stage": "intermediate",
        "cement_type": "Class G + silica",
        "volume_bbl": 280.0,
        "top_of_cement_m": 1800.0,
        "issues_noted": null,
        "source_page": 4,
        "source_snippet": "Casing 9-5/8 inch was set and cemented without issues"
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
        "source_snippet": "12-1/4 inch hole section through Hugin Formation at 2450.0 m MD"
      }
    ],
    "overall_confidence": "high",
    "processing_notes": null
  },
  "warnings": [],
  "message": "Document successfully processed and stored."
}
```

---

### `GET /api/v1/documents/review-queue`
Retrieves the list of documents marked for human engineer review due to low text density (<40 chars/page), scanned legacy format, or low extraction confidence.

- **Responses**: `200 OK`
- **Example Response**:
```json
[
  {
    "source_doc": "scanned_legacy_log_scan.pdf",
    "extraction_method": "manual_flag",
    "overall_confidence": "low",
    "processing_notes": "Low text density; routed as scanned document needing OCR/VLM.",
    "needs_review": true
  }
]
```

---

## 2. Well & Incident Retrieval Endpoints

### `GET /api/v1/incidents/wells`
Returns a list of all wells currently registered in the system.

- **Responses**: `200 OK`
- **Example Response**:
```json
[
  {
    "well_id": "15/9-F-11B",
    "operator": "Statoil ASA",
    "field_name": "Volve",
    "spud_date": "2007-08-24",
    "completion_date": "2007-10-15",
    "latitude": 58.4394,
    "longitude": 1.8875,
    "total_depth_m": 3200.0
  }
]
```

---

### `GET /api/v1/wells/nearby`
Finds offset wells located within a user-defined physical radius (kilometres) using great-circle Haversine distance. Results are sorted nearest-first and include calculated `distance_km`.

- **Query Parameters**:
  - `lat` (float, required): Reference point latitude in decimal degrees (-90.0 to 90.0).
  - `lon` (float, required): Reference point longitude in decimal degrees (-180.0 to 180.0).
  - `radius_km` (float, optional, default: 10.0): Search radius in kilometres (must be > 0).
  - `exclude_well_id` (string, optional): Target well identifier to exclude (e.g. active reference well).
- **Responses**:
  - `200 OK`: List of nearby wells within radius.
  - `400 Bad Request`: Out of range coordinates or non-positive `radius_km`.
- **Example Response**:
```json
[
  {
    "well_id": "15/9-F-12",
    "operator": "Statoil ASA",
    "field_name": "Volve",
    "spud_date": "2008-01-10",
    "completion_date": "2008-03-05",
    "latitude": 58.441,
    "longitude": 1.889,
    "total_depth_m": 3350.0,
    "distance_km": 0.2017
  }
]
```

---

### `GET /api/v1/incidents/well/{well_id}`
Retrieves full header information and extracted drilling events for a specific well.
*Note: Supports well IDs containing forward slashes (e.g. `15/9-F-11B`).*

- **Path Parameters**:
  - `well_id` (string, required): e.g. `15/9-F-11B`
- **Responses**:
  - `200 OK`: Well and events found.
  - `404 Not Found`: Well not found.

---

### `GET /api/v1/incidents/correlate-near`
Queries historical drilling incidents from neighboring offset wells within a given depth radius and optional geological formation.

- **Query Parameters**:
  - `well_id` (string, required): Target well identifier to exclude from offset matches.
  - `depth_m` (float, required): Planned measured depth in metres.
  - `window_m` (float, optional, default: 100.0): Search radius (+/- metres).
  - `formation` (string, optional): Formation name filter.
  - `radius_km` (float, optional, 0-500): Restrict matches to this physical
    radius using well coordinates. Offset events without coordinates are
    excluded; if the target well lacks coordinates, the endpoint falls back
    to depth/formation matching and cannot apply the physical-radius filter.
- **Responses**: `200 OK`
- **Example Response**:
```json
[
  {
    "event_id": 1,
    "well_id": "15/9-F-11B",
    "event_type": "mud_loss",
    "depth_m": 2450.0,
    "formation": "Hugin Formation",
    "event_date": "2007-09-12",
    "description": "Partial mud losses of 15 bbl/hr encountered while drilling through the Hugin Formation.",
    "symptom": "Pit level dropped steadily over 2 hours",
    "action_taken": "Pumped LCM pill (50 bbl, 40 ppb LCM blend); losses reduced to seepage rate.",
    "confidence": "high",
    "source_doc": "wcr_volve_15_9_f11b.pdf",
    "source_page": 3,
    "source_snippet": "at 2450m encountered mud loss of 15 bbl/hr, pumped LCM pill",
    "latitude": 58.4394,
    "longitude": 1.8875,
    "operator": "Statoil ASA",
    "field_name": "Volve"
  }
]
```

---

## 3. Copilot Knowledge Retrieval & Semantic Search (Stage 2)

### `POST /api/v1/copilot/search`
Performs semantic natural language search over historical drilling incidents with acronym normalization (e.g., NPT -> non-productive time), ChromaDB vector retrieval, and citation-grounded answer synthesis.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "query": "What mud losses occurred in the Hugin Formation?",
  "formation": "Hugin Formation",
  "top_k": 5
}
```
- **Responses**:
  - `200 OK`: Search and grounded answer synthesized.
  - `400 Bad Request`: Empty or whitespace query string.

#### Example Response:
```json
{
  "query": "What mud losses occurred in the Hugin Formation?",
  "normalized_query": "What lost circulation material (LCM) / mud losses occurred in the Hugin Formation?",
  "answer": "In well 15/9-F-11B, partial mud losses of 15 bbl/hr occurred at 2450.0m MD in the Hugin Formation on 2007-09-12 [Well 15/9-F-11B, wcr_volve_15_9_f11b.pdf, p. 3]. The mitigation taken was pumping a 50 bbl LCM pill (40 ppb LCM blend), which reduced losses to seepage rate before drilling resumed.",
  "sources": [
    {
      "event_id": 1,
      "well_id": "15/9-F-11B",
      "event_type": "mud_loss",
      "depth_m": 2450.0,
      "formation": "Hugin Formation",
      "description": "Partial mud losses of 15 bbl/hr encountered while drilling through the Hugin Formation.",
      "confidence": "high",
      "source_doc": "wcr_volve_15_9_f11b.pdf",
      "source_page": 3,
      "source_snippet": "at 2450m encountered mud loss of 15 bbl/hr, pumped LCM pill",
      "similarity_score": 0.8841,
      "document_text": "Well 15/9-F-11B | mud_loss at 2450.0m in Hugin Formation: Partial mud losses of 15 bbl/hr encountered while drilling through the Hugin Formation. Symptom: Pit level dropped steadily over 2 hours Action: Pumped LCM pill (50 bbl, 40 ppb LCM blend); losses reduced to seepage rate."
    }
  ]
}
```

---

## 4. Proactive Risk Assessment (Stage 3)

### `GET /api/v1/incidents/risk-check`
Given an active well's current depth and formation, scans the upcoming depth interval for historical incidents in offset wells and returns an explainable, citation-grounded risk score.

The risk score is a **transparent, rule-based heuristic** (frequency × severity weighting) — NOT a trained ML model. This is a deliberate design choice: building and validating a real predictive model requires labeled outcome data and proper statistical validation, which are not achievable with the data volume available. The `explanation` field in the response describes exactly what drove the score.

- **Query Parameters**:
  - `well_id` (string, required): Active well identifier (must exist in the `wells` table).
  - `current_depth_m` (float, required): Current measured depth in metres.
  - `formation` (string, optional): Current geological formation filter.
  - `lookahead_m` (float, optional, default: 50.0): How far ahead to scan (metres).
- **Responses**:
  - `200 OK`: Risk assessment computed.
  - `404 Not Found`: Well identifier not present in the database.
  - `422 Unprocessable Entity`: Missing or non-numeric `current_depth_m`.

#### Example Response (Elevated Risk):
```json
{
  "well_id": "15/9-F-13",
  "current_depth_m": 2440.0,
  "lookahead_m": 80.0,
  "risk_level": "medium",
  "risk_score": 46.0,
  "explanation": "2 historical incident(s) recorded in offset well(s) (15/9-F-11B, 15/9-F-12) within this depth interval: 1 kick incident, 1 mud loss incident. Risk assessment: medium (score 46.0/100). Note: this is a rule-based heuristic score, not a trained predictive model.",
  "contributing_events": [
    {
      "event_id": 1,
      "well_id": "15/9-F-11B",
      "event_type": "mud_loss",
      "depth_m": 2450.0,
      "formation": "Hugin Formation",
      "description": "Partial mud losses of 15 bbl/hr encountered while drilling through the Hugin Formation.",
      "confidence": "high",
      "source_doc": "wcr_volve_15_9_f11b.pdf",
      "source_page": 3,
      "source_snippet": "at 2450m encountered mud loss of 15 bbl/hr, pumped LCM pill"
    },
    {
      "event_id": 3,
      "well_id": "15/9-F-12",
      "event_type": "kick",
      "depth_m": 2510.0,
      "formation": "Hugin Formation",
      "description": "Gas kick detected with 10 bbl pit gain.",
      "confidence": "high",
      "source_doc": "ddr_volve_15_9_f12.pdf",
      "source_page": 2,
      "source_snippet": "gas kick detected, 10 bbl pit gain"
    }
  ]
}
```

#### Example Response (Low Risk — No Historical Incidents):
```json
{
  "well_id": "15/9-F-13",
  "current_depth_m": 1000.0,
  "lookahead_m": 50.0,
  "risk_level": "low",
  "risk_score": 0,
  "explanation": "No historical incidents found in offset wells within this depth interval. Risk assessment: low.",
  "contributing_events": []
}
```

---

## 5. Error Contract
All API errors return consistent JSON detail objects:
```json
{
  "detail": "Search query cannot be empty."
}
```
- `400 Bad Request`: Input validation failed (unsupported extension, 0 bytes, empty query, or corrupted syntax).
- `404 Not Found`: Resource or well identifier not present in database.
- `422 Unprocessable Entity`: Missing or invalid query parameters (e.g., non-numeric depth).
- `500 Internal Server Error`: Unhandled server/pipeline exception.
