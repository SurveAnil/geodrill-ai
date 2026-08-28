# eRTMAC-NWIS (Nearby Wells Intelligence System)

## Project Documentation

**Repository:** [SurveAnil/geodrill-ai](https://github.com/SurveAnil/geodrill-ai)  
**Project type:** AI-enabled drilling decision-support MVP  
**Primary users:** Drilling engineers, geologists, mud engineers, and operations teams

## 1. Executive Summary

eRTMAC-NWIS is an AI-powered offset-well intelligence platform designed to work
alongside Oil India Limited's eRTMAC system. It converts historical drilling
reports and well documents into searchable operational knowledge, correlates
nearby wells by location, depth, and formation, and provides explainable
real-time risk signals and recommendations.

The MVP demonstrates the complete decision-support journey:

```text
Historical documents
  -> OCR and structured extraction
  -> Knowledge and vector retrieval
  -> Nearby-well and formation correlation
  -> Telemetry risk evaluation
  -> Alerts and recommended actions
```

## 2. Problem Being Solved

Drilling knowledge is commonly distributed across completion reports, daily
drilling reports, mud logs, geological records, and individual experience.
Manually finding a relevant offset-well incident can delay decisions and make
lessons difficult to reuse.

The system provides one workflow for:

- Finding nearby wells around an active well.
- Searching historical drilling events and lessons learned.
- Comparing events by measured depth and formation.
- Detecting telemetry patterns associated with drilling hazards.
- Presenting evidence-backed alerts and recommendations in a dashboard.

## 3. Current MVP Coverage

| Requirement | MVP status | What is implemented |
| --- | --- | --- |
| Document intelligence | Implemented | PDF/DOCX/LAS/WITSML upload validation, PDF extraction, OCR routing, structured schemas, and ingestion jobs |
| Nearby-well visualization | Implemented | Radius-based nearby-well API and interactive frontend map/radar with demo fallback data |
| Knowledge repository | Implemented | SQLite/ChromaDB-backed storage, keyword/vector retrieval, historical incidents, lessons learned, and citations |
| Depth and formation correlation | Implemented | Survey calculations, LAS parsing, formation-top correlation, and offset incident matching |
| Predictive risk intelligence | MVP baseline | Explainable heuristic scoring for mud losses, stuck pipe, overpressure, torque, cementing, and related signals |
| Real-time alerts | Implemented for demo | Validated telemetry ingestion, deterministic alert evaluation, recommendations, and acknowledgement |
| User dashboard | Implemented | Next.js dashboard with ingestion, Copilot, map, stratigraphy, lessons, telemetry, and triage panels |

### Important accuracy statement

The predictive-risk feature is currently an explainable
`heuristic-baseline-v1`. It is not a statistically trained or calibrated
production ML model yet. Training and validation require labelled historical
telemetry and incident outcomes from the target operating environment.

The demo uses simulated telemetry and seeded/sample historical data when
real OIL/eRTMAC feeds or documents are not available. The frontend clearly
indicates whether the backend is **CONNECTED** or using **DEMO FALLBACK**.

## 4. Architecture

The backend is organized as a five-layer AI pipeline. The frontend presents
these capabilities through a seven-phase operational dashboard.

### Backend AI pipeline

1. **Document Intelligence:** PDF loading, table extraction, OCR routing, and
   structured report extraction.
2. **Knowledge Retrieval:** Entity normalization, relational persistence,
   ChromaDB vector retrieval, hybrid search, and citation validation.
3. **Correlation and Analytics:** Well trajectories, LAS logs, depth windows,
   formation matching, and spatial offset correlation.
4. **Predictive Risk Models:** Validated telemetry features and explainable
   hazard scoring.
5. **Alerting and Recommendation:** Deterministic thresholds, evidence-backed
   recommendations, alert acknowledgement, and triage output.

### Frontend dashboard phases

1. Document Intelligence
2. Entity and Trajectory Intelligence
3. Stratigraphic Depth Cross-Correlation
4. Lessons Learned Repository
5. AI Copilot
6. Geospatial Offset Intelligence
7. Live Operations Telemetry

## 5. Main Technology Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Zustand
- **Backend:** Python, FastAPI, Pydantic, Uvicorn
- **Document processing:** PDF loaders, table extraction, OCR interface, DOCX/LAS/WITSML validation
- **AI and retrieval:** Provider-agnostic LLM layer, NLP extraction, ChromaDB vectors, hybrid keyword/vector retrieval
- **Data and analytics:** SQLite-compatible persistence, trajectory calculations, spatial correlation, deterministic risk scoring
- **Visualization:** Leaflet map integration, Chart.js telemetry charts, live operational dashboard
- **Quality:** Pytest backend suite and Next.js production build

## 6. End-to-End Demonstration

1. Start the FastAPI backend and Next.js frontend.
2. Upload a supported historical report in **Smart Ingestion Studio**.
3. Poll the ingestion job until extraction and persistence complete.
4. Ask the **AI Copilot** a drilling question and inspect its source citations.
5. Select an active-well location and inspect nearby offset wells.
6. Review historical incidents and lessons correlated by depth and formation.
7. Submit formation tops or survey data to view stratigraphic correlation.
8. Run the telemetry simulator or send validated telemetry samples.
9. Review the highest-risk hazard, recommendation, evidence, and alert status.
10. Acknowledge the alert from the triage panel.

## 7. Running Locally

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

Backend API documentation:

<http://localhost:8000/docs>

### Frontend

```powershell
npm install --prefix frontend
npm run dev --prefix frontend
```

Open <http://localhost:3000>.

For a different backend URL, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 8. Key API Surfaces

- `POST /api/v1/ingest-document` — queue document ingestion
- `GET /api/v1/ingestion-jobs/{job_id}` — inspect ingestion status
- `POST /api/v1/copilot/search` — grounded knowledge search
- `GET /api/v1/wells/nearby` — nearby wells within a radius
- `GET /api/v1/incidents/correlate-near` — correlate offset incidents
- `POST /api/v1/trajectory/correlate-formations` — correlate formations and depths
- `POST /api/v1/telemetry` — ingest validated telemetry
- `POST /api/v1/predictive-risk` — evaluate explainable risk signals
- `POST /api/v1/alerts` — generate deterministic alerts and recommendations
- `POST /api/v1/alerts/{alert_id}/acknowledge` — acknowledge an alert

## 9. Engineering Highlights

- **10Hz telemetry throttling:** Zustand updates the high-frequency store while
  chart rendering is throttled outside the React render cycle.
- **Bounded chart buffers:** Chart history is limited with `.slice(-100)` to
  prevent unbounded memory growth.
- **Next.js SSR safety:** Leaflet is loaded dynamically with server-side
  rendering disabled.
- **Stable live UI:** `tabular-nums` prevents telemetry digits from shifting
  the layout.
- **Resilient demonstration mode:** Connected API responses are preferred, but
  deterministic fallback scenarios keep the dashboard usable offline.
- **Evidence-first Copilot:** Retrieval responses preserve source references
  and avoid presenting unsupported generic answers as grounded evidence.

## 10. Validation and Test Status

The current backend regression suite passes:

```text
88 passed
```

The frontend also has a production build validation command:

```powershell
npm run build --prefix frontend
```

## 11. Production Roadmap

The following integrations are intentionally outside the current demo MVP:

- OIL eRTMAC live stream integration.
- WITSML, MQTT, OPC-UA, Kafka, or equivalent streaming adapters.
- Distributed ingestion workers using a queue such as Redis/Celery.
- Durable multi-instance telemetry and alert storage.
- Environment-driven production CORS and authentication.
- Labelled-data training, calibration, and independent validation of risk models.
- Production-grade PostgreSQL, vector database, graph database, observability,
  notification routing, and audit controls.

## 12. Presentation Guidance

Use the following concise description in a hackathon presentation:

> eRTMAC-NWIS gives drilling teams institutional memory. It combines document
> intelligence, offset-well search, geospatial and formation correlation, and
> explainable telemetry risk alerts in one decision-support dashboard.

Be explicit that the current demonstration is an API-connected MVP using
simulated telemetry and seeded data, while the production roadmap connects the
same interfaces to OIL's live operational and historical data sources.

