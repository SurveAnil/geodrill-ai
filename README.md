# GeoDrill AI 🛢️

**Agentic Oil & Gas Knowledge System for Drilling Report Extraction and Offset-Well Intelligence**

GeoDrill AI processes unstructured drilling reports (Well Completion Reports, Daily Drilling Reports) to extract structured well headers, drilling incidents (mud losses, stuck pipe, kicks, torque spikes), and mitigation lessons learned.

---

## 🏛️ Architecture

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
