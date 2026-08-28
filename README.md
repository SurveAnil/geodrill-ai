# GeoDrill AI 🛢️

**Agentic Oil & Gas Knowledge System for Drilling Report Extraction and Offset-Well Intelligence**

GeoDrill AI processes unstructured drilling reports (Well Completion Reports, Daily Drilling Reports) to extract structured well headers, drilling incidents (mud losses, stuck pipe, kicks, torque spikes), and mitigation lessons learned.

---

## 🏛️ Architecture

For the complete project overview, MVP coverage, architecture, demonstration
workflow, API surfaces, validation status, and production roadmap, see the
[Project Documentation](docs/project-documentation.md).

The platform is organized as a seven-phase drilling intelligence experience:

1. **Layer 1: Document Intelligence** — Ingests digital and scanned reports, applies OCR, and extracts structured well data.
2. **Layer 2: Entity and Trajectory Intelligence** — Identifies drilling entities and calculates wellbore survey geometry.
3. **Layer 3: Stratigraphic Depth Cross-Correlation** — Correlates formation depths across wells with a live laser projection beam.
4. **Layer 4: Lessons Learned Repository** — Presents historical drilling incidents and mitigations in a searchable timeline.
5. **Layer 5: AI Copilot** — Provides multi-provider extraction, retrieval, and drilling-focused assistance.
6. **Layer 6: Geospatial Offset Intelligence** — Maps wells and correlates nearby incidents for offset-well planning.
7. **Layer 7: Live Operations Telemetry** — Visualizes real-time gauges, charts, alerts, and operational risk signals.

### Key Technical Implementations

- **10Hz Data Throttling:** `useDrillStore.subscribe()` runs outside the React render cycle, updating charts at approximately 3.3Hz while the store continues ticking at 10Hz to prevent render storms.
- **Chart.js Ring Buffers:** Live telemetry uses fixed-size array slicing with `.slice(-100)` to bound chart history and prevent memory leaks.
- **Next.js SSR Safety:** `next/dynamic` with `{ ssr: false }` safely loads Leaflet GIS maps in the server-side rendered application.
- **UI Stability:** CSS `tabular-nums` keeps live telemetry digits aligned and prevents layout jitter as values change.

```
geodrill-ai/
├── config/
│   ├── constants.py                  # Extraction schemas, domain prompts, density thresholds
│   └── config.yaml                   # Provider and database configurations
├── src/
│   ├── api/
│   │   ├── main.py                   # FastAPI app initialization with lifespan & routers
│   │   ├── schemas/
│   │   │   ├── incident_schemas.py   # EventType, Confidence, WellHeader, DrillingEvent
│   │   │   ├── document_schemas.py   # IngestResult, PageContent, ExtractionResult, ReviewQueue
│   │   │   └── __init__.py           # Unified schema exports
│   │   └── routes/
│   │       ├── ingest_routes.py       # Supported-format document upload endpoint
│   │       ├── ocr_routes.py          # PDF upload and manual review queue endpoints
│   │       ├── incident_routes.py     # Well history and offset-well spatial correlation
│   │       ├── ner_routes.py          # Geological entity extraction endpoints
│   │       ├── trajectory_routes.py   # Survey and trajectory endpoints
│   │       └── wells_routes.py        # Well program and metadata endpoints
│   ├── layer1_ingestion/
│   │   ├── cv_preprocessor.py         # Image preprocessing for scanned reports
│   │   ├── pdf_loader.py             # PDF text/table loader & digital vs scanned classifier
│   │   ├── table_extractor.py        # PDF table formatter for LLM prompt context
│   │   ├── ocr_engine.py             # Scanned document routing & OCR interface
│   │   └── document_pipeline.py      # Ingest -> Route -> LLM Extract -> Validate -> Store ETL
│   ├── layer2_ner/
│   │   ├── bgs_dataset_loader.py      # Geological entity dataset loading
│   │   ├── inference_engine.py        # Geological NER inference
│   │   ├── model_trainer.py           # NER model training utilities
│   │   └── rules_engine.py            # Domain rule-based entity extraction
│   ├── layer3_trajectory/
│   │   ├── las_parser.py              # LAS well-log parsing
│   │   ├── spatial_interpolator.py    # Spatial and depth interpolation
│   │   └── survey_calculator.py       # Minimum-curvature survey calculations
│   ├── layer4_knowledge_graph/
│   │   ├── db_service.py              # SQLite/PostgreSQL persistence & offset correlation queries
│   │   ├── glossary_normalizer.py     # Drilling terminology normalization
│   │   ├── graph_builder.py           # Knowledge graph construction
│   │   ├── hybrid_retriever.py        # Keyword and vector retrieval
│   │   └── vector_store.py            # ChromaDB vector persistence
│   └── layer5_copilot/
│       ├── agent_workflow.py          # Copilot orchestration workflow
│       ├── incident_correlator.py     # Historical incident correlation
│       ├── llm_extractor.py          # Multi-provider LLM client (Anthropic, Groq, OpenAI, Gemini, Mock)
│       ├── risk_scorer.py             # Drilling risk scoring
│       └── tools.py                   # Agent tools for extraction, offset lookup, and well history
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js application shell and global styles
│   │   ├── components/
│   │   │   ├── ai/
│   │   │   │   ├── AIPanelContainer.tsx
│   │   │   │   ├── GeminiChat.tsx
│   │   │   │   └── SmartIngestionStudio.tsx
│   │   │   ├── geospatial/
│   │   │   │   ├── GeospatialPanel.tsx
│   │   │   │   ├── OffsetRadarTable.tsx
│   │   │   │   └── WellMap.tsx
│   │   │   ├── layout/                # Dashboard grid and navigation
│   │   │   ├── lessons/
│   │   │   │   └── LessonsLearnedRepository.tsx
│   │   │   ├── stratigraphy/
│   │   │   │   └── StratigraphicCorrelation.tsx
│   │   │   ├── telemetry/              # Live charts, gauges, and telemetry panel
│   │   │   └── triage/
│   │   │       └── TriageHero.tsx
│   │   └── store/
│   │       └── useDrillStore.ts        # High-frequency operations telemetry store
│   ├── package.json
│   └── package-lock.json
├── tests/
│   ├── test_schemas.py               # Schema constraints and boundary validation
│   ├── test_ingestion.py             # Table extraction and OCR routing tests
│   ├── test_llm_extractor.py         # LLM provider fallbacks and schema error recovery
│   ├── test_db_service.py            # Relational database persistence and correlation queries
│   └── test_pipeline.py              # End-to-end pipeline orchestration tests
├── requirements.txt
└── .env.example
```

---

## 🚀 Quickstart

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and set your preferred LLM provider API key(s):
```bash
cp .env.example .env
```

Supports:
- **Anthropic Claude** (`ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`)
- **Groq** (`GROQ_API_KEY`, `GROQ_MODEL`)
- **OpenAI** (`OPENAI_API_KEY`, `OPENAI_MODEL`)
- **Google Gemini** (`GEMINI_API_KEY`, `GEMINI_MODEL`)
- **Deterministic Mock Client** (Used automatically if no API key is provided)

### 3. Start the Connected Dashboard

In a second terminal, install and start the Next.js frontend:

```bash
npm install --prefix frontend
npm run dev --prefix frontend
```

Open [http://localhost:3000](http://localhost:3000). The frontend uses
`http://localhost:8000` by default for the FastAPI service. To use another
backend URL, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The dashboard displays `API: CONNECTED` when the backend responds. If the API
is unavailable, it explicitly displays `DEMO FALLBACK` and uses deterministic
scenario data so the product can still be demonstrated offline.

---

## 🛠️ Usage

### Running the API
Start the FastAPI server:
```bash
uvicorn src.api.main:app --reload --port 8000
```
Interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### Key Endpoints:
- `POST /api/v1/documents/process-file`: Upload PDF report, execute structured extraction, and store to database.
- `GET /api/v1/documents/review-queue`: List documents flagged for manual review due to low confidence or scanned format.
- `GET /api/v1/incidents/wells`: List all extracted wells.
- `GET /api/v1/incidents/well/{well_id}`: Retrieve well header and historical drilling incidents.
- `GET /api/v1/incidents/correlate-near`: Find historical incidents in offset wells within depth/formation windows.
- `GET /api/v1/wells/nearby`: Find wells within a latitude/longitude radius.
- `POST /api/v1/copilot/search`: Search the grounded drilling knowledge base with citations.
- `POST /api/v1/trajectory/correlate-formations`: Correlate survey stations and formation tops.
- `POST /api/v1/telemetry`: Ingest validated real-time telemetry samples.
- `GET /api/v1/telemetry/recent`: Retrieve recent telemetry for a well.
- `POST /api/v1/predictive-risk`: Evaluate explainable hazard probabilities.
- `POST /api/v1/alerts`: Evaluate deterministic safety alerts and recommendations.
- `POST /api/v1/alerts/{alert_id}/acknowledge`: Acknowledge an operational alert.
- `POST /api/v1/ingest-document`: Queue PDF, DOCX, LAS, or WITSML ingestion.
- `GET /api/v1/ingestion-jobs/{job_id}`: Track a queued ingestion job to completion.

### Connected Dashboard Workflow

The dashboard is organized as a backend-connected decision-support flow:

1. Upload a historical report in **Smart Ingestion Studio**. The frontend
   submits the multipart file and polls the durable ingestion job.
2. The **AI Copilot** calls grounded retrieval and displays source citations.
3. **Geospatial Radar** loads nearby wells from the radius API, with demo data
   available when no well coordinates are stored.
4. **Lessons Learned** loads depth- and formation-correlated incidents.
5. **Stratigraphic Correlation** submits survey and formation-top data to the
   trajectory service.
6. The 10Hz simulator sends validated telemetry to the backend. Every tenth
   sample requests predictive risk and alert evaluation to avoid request storms.
7. The triage card displays the highest returned hazard, recommendation, and
   citation; an engineer can acknowledge an alert through the API.

The simulator remains intentionally available for hackathon demonstrations.
It is clearly labeled as demo fallback data and is not a substitute for an
OIL eRTMAC, WITSML, MQTT, OPC-UA, or Kafka production stream.

### Programmatic Extraction Pipeline
```python
from src.layer1_ingestion.document_pipeline import pipeline

# Process a single PDF report
result = pipeline.process_document("path/to/well_completion_report.pdf")
print(f"Well: {result.well_header.well_id}")
print(f"Extracted {len(result.events)} drilling incidents.")

# Process an entire folder of PDFs
results = pipeline.process_directory("data/raw_reports/")
```

---

## 🧪 Testing

Run the automated test suite with pytest:
```bash
pytest tests/ -v
```

Build the frontend from the repository root:

```bash
npm run build --prefix frontend
```

The backend predictive-risk service currently provides an explainable
`heuristic-baseline-v1`. It is not yet a statistically trained or calibrated
model because labeled historical incident outcomes are required. Production
deployment also requires authentication, distributed workers, durable alert
storage, and live eRTMAC/WITSML telemetry integration.

### Render deployment

The repository includes [`render.yaml`](render.yaml), which pins the service to
Python 3.12, installs all dependencies from `requirements.txt` (including
ChromaDB), starts Uvicorn on Render's `$PORT`, and uses `/health` for health
checks. If the service was created manually in Render, set the build command to
`pip install -r requirements.txt` and redeploy after saving the configuration.
Set `GEODRILL_CORS_ORIGINS` to the exact deployed Vercel origin, for example
`https://your-project.vercel.app`. In Vercel, set
`NEXT_PUBLIC_API_URL` to the public Render service URL and redeploy the frontend
after changing it.
