# GeoDrill AI 🛢️

**Agentic Oil & Gas Knowledge System for Drilling Report Extraction and Offset-Well Intelligence**

GeoDrill AI processes unstructured drilling reports (Well Completion Reports, Daily Drilling Reports) to extract structured well headers, drilling incidents (mud losses, stuck pipe, kicks, torque spikes), and mitigation lessons learned.

---

## 🏛️ Architecture

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
│   │       ├── ocr_routes.py         # PDF upload and manual review queue endpoints
│   │       └── incident_routes.py    # Well history and offset-well spatial correlation
│   ├── layer1_ingestion/
│   │   ├── pdf_loader.py             # PDF text/table loader & digital vs scanned classifier
│   │   ├── table_extractor.py        # PDF table formatter for LLM prompt context
│   │   ├── ocr_engine.py             # Scanned document routing & OCR interface
│   │   └── document_pipeline.py      # Ingest -> Route -> LLM Extract -> Validate -> Store ETL
│   ├── layer4_knowledge_graph/
│   │   └── db_service.py             # SQLite/PostgreSQL persistence & offset correlation queries
│   └── layer5_copilot/
│       ├── llm_extractor.py          # Multi-provider LLM client (Anthropic, Groq, OpenAI, Gemini, Mock)
│       └── tools.py                  # Agent tools for extraction, offset lookup, and well history
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
