# GeoDrill Phase 1 Engineering Handoff

## 1. Project identity

- **Project:** GeoDrill
- **SIH context:** eRTMAC-NWIS (Nearby Wells Intelligence System)
- **Current phase:** **Phase 1 COMPLETE / FROZEN**
- **Purpose:** Provide a coherent operational foundation for nearby-well intelligence: canonical well and formation data, historical incident correlation, telemetry/risk/alert contracts, document/Copilot surfaces, and a shared active-well workflow.
- **Scope boundary:** Do not start Phase 2 from this handoff. Phase 1 is the validated foundation, not a production live-drilling or trained-ML system.

## 2. Current architecture

### Frontend

- Next.js App Router, TypeScript, React, Zustand.
- React Leaflet with CARTO Voyager raster tiles.
- Shared shell in `frontend/src/components/layout/`.
- API client in `frontend/src/lib/api.ts`.
- Operational data must come from FastAPI/SQLite; frontend demo values are limited to explicitly labelled simulated telemetry or UI fallback states.

### Backend

- FastAPI application in `src/api/main.py`.
- Python route modules in `src/api/routes/`.
- Pydantic contracts in `src/api/schemas/`.
- SQLite through `DatabaseService` (`src/layer4_knowledge_graph/db_service.py`).
- Chroma persistent vector retrieval for document/event search.
- Existing Copilot, deterministic risk, alert, ingestion, telemetry, trajectory, and incident components are preserved.

**Architectural principle:** one canonical operational data source. Frontend wells, offsets, formations, incidents, and active-well metadata must be sourced from backend contracts rather than independent hard-coded operational datasets.

## 3. Frontend routes

- `/` redirects to `/overview`.
- `/overview`: active-well summary, risk/action, telemetry summary, alerts, evidence, and geospatial panel.
- `/telemetry`: explicitly DEMO/SIMULATED telemetry, gauges, charts, scenario controls, and API stream controls.
- `/ai`: ingestion status, document surface, Copilot search, and citations.
- `/offset-wells`: backend nearby-well query, radius selector, Leaflet map, and offset table.
- `/stratigraphy`: formation/depth correlation and historical horizon context.
- `/lessons`: searchable/correlated historical incidents and evidence.
- `/alerts`: active/acknowledged/resolved alert presentation.

## 4. Shared active-well context

`frontend/src/store/useDrillStore.ts` owns:

- `activeWellId`, `wellName`, `field`, `operator`
- `activeWellLocation.latitude/longitude`
- `targetTotalDepthM`
- `telemetry.measuredDepthM`, TVD, and `currentFormation`
- operating mode, selected scenario, risk, alert count, backend status

`AppShell` restores the selected ID from local storage and resolves it against `GET /api/v1/wells`. Selecting an offset row uses the complete backend well metadata through `setActiveWellContext`, atomically updating ID, coordinates, depth, formation, operator, field, and total depth. Client-side navigation preserves context; direct refresh restores it when the backend catalog contains the ID.

Canonical examples:

- `OIL-NWIS-01` is the initial active well.
- `OIL-NWIS-02` is a validated selectable offset.
- The selected offset is not permanently the active well; the backend catalog and user selection decide.

## 5. Canonical Northwind dataset

- **Field:** Northwind Field
- **Wells:** `OIL-NWIS-01`, `OIL-NWIS-02`, `OIL-NWIS-03`, `OIL-NWIS-04`
- `OIL-NWIS-01` is active by default; the other three are nearby offsets.
- Coordinates, current depths, formations, total depths, casing/cementing/mud programs, and historical events are defined in `src/layer4_knowledge_graph/seed_data.py`.
- Formations include Harbour Shale and Northwind Sandstone.
- Events cover kick/influx, mud loss, stuck pipe, torque spike, and cementing issues with depth, severity, evidence, and mitigation fields.

`DatabaseService` initializes `data/geodrill.db` and uses `GEODRILL_SEED_DATA`. The canonical marker is `seed_oil_nwis_foundation_v1`. `seed_demo_data()` is idempotent and checks the marker. It does not delete unrelated legacy records.

## 6. Legacy data situation

SQLite contains canonical Northwind data and may also contain older persisted demo data, including `NWIS-DEMO-01`. Chroma currently contains legacy Volve/Hugin material such as `15/9-F-11B`, `15/9-F-12`, Hugin, and Volve documents. These records remain for regression fixtures, compatibility, and historical paths; do not blindly delete them.

Unrestricted Copilot retrieval can still retrieve legacy vector records for a Northwind question. Phase 2 must introduce explicit dataset/field/source scoping and retrieval filtering. Do not solve that requirement by deleting tests or fixtures.

## 7. Backend API contracts

All routes below are registered under `/api/v1` in `src/api/main.py`.

| Endpoint | Purpose | Frontend consumer |
|---|---|---|
| `GET /wells` | Canonical well catalog | `AppShell` |
| `GET /wells/nearby?lat&lon&radius_km&exclude_well_id` | Haversine nearby offsets | `GeospatialPanel` |
| `GET /wells/{well_id}/formations` | Stored formation tops | future/formation surfaces |
| `GET /wells/{well_id}/programs` | Casing, cementing, mud programs | future/program surfaces |
| `POST /telemetry` | Accept bounded telemetry batch; returns 202 | `TopNav` API stream |
| `GET /telemetry/recent?well_id&limit` | Recent process-local samples | telemetry consumers |
| `GET /incidents/correlate-near?well_id&depth_m&window_m&formation` | Nearby historical event correlation | Lessons |
| `GET /incidents/risk-check?...` | Deterministic proactive risk check | backend/API consumers |
| `POST /trajectory/correlate-formations` | Correlate reached formation tops against survey | Stratigraphy |
| `POST /predictive-risk` | Heuristic hazard probabilities | `TopNav` |
| `POST /alerts` | Deterministic alert evaluation | `TopNav`/alerts |
| `POST /alerts/{alert_id}/acknowledge` | Acknowledge alert | alert UI |
| `POST /ingest-document` | Queue supported document ingestion | Smart Ingestion Studio |
| `GET /ingestion-jobs/{job_id}` | Ingestion status | Smart Ingestion Studio |
| `POST /copilot/search` | Retrieval and cited answer | GeminiChat |

Pydantic validation remains active. Invalid telemetry, invalid query ranges, and formation tops outside the surveyed interval return validation errors rather than being silently accepted.

## 8. API base URL

The frontend uses `NEXT_PUBLIC_API_URL` in `frontend/src/lib/api.ts` and `SmartIngestionStudio.tsx`. The local default is `http://localhost:8000`; canonical paths append `/api/v1`. Production URLs must be supplied through environment configuration.

Previously observed 404s were Next.js development static/chunk requests such as `/_next/static/css/app/layout.css` and `/_next/static/chunks/app/offset-wells/page.js` after stale dev-server/build chunks. Clean runtime verification showed no FastAPI `/api/v1` 404. Always distinguish Next.js static asset failures from backend API route failures.

## 9. Radius / nearby-well state

`GeospatialPanel` owns the single `radiusKm` state, initially 10. It drives:

1. selector value
2. `GET /api/v1/wells/nearby` `radius_km`
3. map circle radius
4. offset table heading
5. result set/count

Transitions `10 → 25 → 50 → 10` were browser-verified with matching requests, SVG circle radii, headings, and backend results. Do not add duplicate radius state.

## 10. Map implementation

The blank `/offset-wells` map issue is closed. `GeospatialPanel` provides a fixed-height map slot. `WellMap` uses the existing Leaflet `ResizeObserver`/`requestAnimationFrame` `invalidateSize()` synchronizer. Overview, direct offset load, refresh, navigation, active marker, nearby markers, and radius changes were validated.

Do not replace or reopen Leaflet initialization, sizing, or CARTO behavior without a new reproducible map defect.

## 11. CARTO

`WellMap.tsx` uses the raster Voyager endpoint only. The key is supplied through ignored `frontend/.env.local` as `NEXT_PUBLIC_CARTO_API_KEY`. `frontend/.env.example` contains only an empty placeholder. Never put the actual key in source, memory, prompts, docs, Git, or commits.

## 12. Stratigraphy 422 fix

`StratigraphicCorrelation` previously sent tops at approximately 3380m and 3500m while its generated survey ended at the current depth (approximately 3108m). FastAPI correctly returned 422 because interpolation rejects tops outside the surveyed interval. The frontend now filters to tops already reached and displays an explicit no-tops state when appropriate. Backend validation was not weakened.

## 13. Telemetry

Telemetry is DEMO/SIMULATED and process-local, not production eRTMAC live telemetry. Validated ingestion returns HTTP 202. The UI labels simulated values clearly. Do not describe this as live drilling telemetry.

## 14. Alerts

Alert evaluation is deterministic and process-local/simulated. Acknowledgement is not a durable production notification system. No external notifications or production alert persistence are implemented.

## 15. Copilot / retrieval

`POST /api/v1/copilot/search` flows through `copilot_routes.py`, `HybridRetriever.retrieve()`, Chroma similarity/lexical retrieval, and cited answer generation. Phase 1 is not production-grade predictive AI. Limitations include legacy Chroma records, missing dataset scoping, heuristic risk, document/OCR/manual-review limitations, and compatibility extraction paths.

## 16. Risk / AI limitations

Predictive risk is a deterministic `heuristic-baseline-v1` style implementation, not trained or statistically validated production ML. Probabilities are signals derived from bounded telemetry and historical evidence. Advanced anomaly detection, trained models, and production recommendations are future work.

## 17. Document ingestion

The ingestion surface supports PDF, DOCX, LAS, and WITSML-labelled workflows according to the existing UI/contracts. Digital parsing, deterministic extraction, manual review, and LAS parsing exist. OCR/scanned-document handling and NER are not production-ready; low-confidence/scanned paths require review. Do not claim full OCR/NER production capability.

## 18. Current validation status

- Backend: `$env:PYTHONPATH="$PWD"; pytest -q` → **94 passed**.
- Frontend: `npm run build` → **passed**.
- Known build warning: multiple lockfiles caused Next.js workspace-root inference; non-blocking and pre-existing.
- Browser: no operational API 4xx/5xx; telemetry 202; nearby wells 200; incident correlation 200; wells 200; formation correlation 200.
- Radius `10 → 25 → 50 → 10` verified.
- `OIL-NWIS-02` persisted across route navigation and direct refresh.
- `/offset-wells` renders with active marker and canonical nearby wells.

## 19. Hydration warning

Reported attributes `bis_skin_checked`, `bis_register`, `data-new-gr-c-s-check-loaded`, `data-gr-ext-installed`, and `__processed_*` are browser-extension markers. They were absent in the clean browser context, so no application hydration changes were made. Reproduce with extensions disabled before changing layout/components.

## 20. Known limitations / technical debt

### Phase 1 accepted

- Telemetry is simulated/process-local.
- Alerts are deterministic/process-local.
- Risk is heuristic, not trained ML.
- Legacy SQLite/Chroma records remain for compatibility.
- Existing legacy tests and `NWIS-DEMO-01` may remain persisted.
- OCR/NER and scanned-document handling require manual review.
- Next.js multiple-lockfile warning remains.

### Phase 2 targets

- Retrieval dataset/field/source scoping.
- Formation-aware evidence ranking and event normalization.
- Curated validation datasets and stronger citation grounding.
- Durable telemetry/alerts and eventual predictive intelligence.

## 21. Phase 2 starting backlog (not implemented)

1. NWIS retrieval/data scoping: filter Chroma/SQLite evidence by dataset, field, well, and source.
2. Document intelligence: improve extraction contracts and review workflows.
3. Event normalization: normalize event types, severity, symptoms, mitigations, and evidence.
4. Formation-aware retrieval: connect formation tops and depth windows to evidence.
5. Nearby-well intelligence: expand spatial/depth/formation correlation.
6. Lessons learned: durable search and evidence views.
7. Evidence grounding: enforce source/page/snippet citations.
8. Risk reasoning: transparent, validated rule/model progression.
9. Curated validation data: small real dataset without mixing it into the operational demo.
10. Eventual predictive intelligence: only after data and validation gates.

Relevant existing surfaces include `src/layer4_knowledge_graph/`, `src/layer5_copilot/`, incident/trajectory routes, `frontend/src/components/ai/`, lessons, stratigraphy, and tests. Preserve Phase 1 API contracts and Northwind determinism.

## 21A. Agreed implementation roadmap after Phase 1

This is the planned sequence discussed for the remaining GeoDrill build. It is a roadmap only; no phase below Phase 1 is implemented by this handoff.

### Phase 2 — NWIS data model and seed dataset

- Formalize the NWIS entities and relationships around wells, offsets, formations, programs, incidents, documents, evidence, telemetry, risk, and alerts.
- Keep the deterministic Northwind scenario as the operational demo fixture.
- Add explicit dataset, field, source, and provenance identifiers before adding more data.
- Expand the seed only when every new record has a clear well, depth/formation relationship, and evidence path.
- Preserve idempotent initialization and backward-compatible API contracts.

### Phase 3 — Offset-well intelligence

- Strengthen nearby-well ranking using distance, comparable measured depth, formation, trajectory, and event similarity.
- Return explainable comparison factors and evidence, not an opaque score.
- Extend the existing nearby-well and incident-correlation routes rather than creating parallel operational APIs.
- Validate radius, depth-window, formation, empty-result, and invalid-well behavior with deterministic tests.

### Phase 4 — Document intelligence and RAG

- Improve PDF, DOCX, LAS, and WITSML ingestion with stable document/source/page/snippet metadata.
- Add explicit dataset/field/well filtering to Chroma and hybrid retrieval.
- Add OCR and NER only behind confidence/manual-review guardrails; do not silently treat low-confidence extraction as fact.
- Ground Copilot responses in scoped evidence and expose citations in the UI.

### Phase 5 — Depth and formation correlation

- Connect formation tops, survey intervals, event depths, and offset-well comparisons into one validated correlation contract.
- Support formation-aware event windows and explicit handling for unreached formations or out-of-survey depths.
- Preserve backend validation; fix invalid payload construction in clients rather than weakening schemas.
- Add regression coverage for depth/formation transitions and active-well changes.

### Phase 6 — Hybrid risk intelligence

- Evolve `heuristic-baseline-v1` into transparent hybrid reasoning that combines rules, historical evidence, and validated statistical/ML signals where justified.
- Keep risk explanations, source evidence, confidence, and recommended action separate.
- Calibrate against curated validation data before presenting model-derived probabilities as operational guidance.
- Do not call an unvalidated model production ML.

### Phase 7 — Telemetry and proactive alerts

- Replace process-local simulated streams with a stable telemetry ingestion contract that can later accept eRTMAC/external data.
- Add durable, auditable alert state transitions: monitoring, active, acknowledged, resolved, escalated.
- Preserve DEMO/SIMULATED labels and keep external notification integrations out of the core until contracts and security are defined.
- Test delayed, missing, duplicated, and out-of-order telemetry.

### Phase 8 — Grounded AI Copilot

- Make the Copilot context derive from the same active-well, depth, formation, risk, alert, and evidence contracts used by the UI.
- Add scoped retrieval, citation verification, uncertainty language, and refusal behavior for unsupported claims.
- Support operational questions such as comparable offset hazards and recommended mitigations without mixing unrelated Volve/legacy records into Northwind answers.
- Measure answer grounding and retrieval quality on a curated evaluation set.

### Phase 9 — End-to-end demo and hardening

- Validate the complete flow from well selection through offsets, stratigraphy, lessons, telemetry, risk, alerts, and Copilot.
- Add reproducible startup/seed instructions, environment checks, health diagnostics, and failure-state UX.
- Run backend, frontend, contract, browser, security, and data-isolation checks.
- Freeze the demo dataset and record known limitations before any production deployment or external integration.

### Cross-phase gates

- Do not begin a later phase until the preceding phase has tests, documented API/data contracts, and a reproducible validation result.
- Do not mix synthetic Northwind operational data with curated real data without explicit dataset/source labels and retrieval filters.
- Do not introduce production eRTMAC, trained ML, production PostgreSQL, external notifications, or unrestricted OCR/RAG as shortcuts.
- Every phase must preserve the canonical active-well context, environment-based API configuration, and working Leaflet map.

## 22. Dataset strategy

Planning guidance, not implemented scope: retain a deterministic synthetic Northwind scenario for the SIH demo and add a separately labelled curated real dataset for validation/research. Start small: one active well, 3–6 offsets, 10–30 historical wells, 50–200 events, formation tops, DDRs, selected logs, and 20–100 documents. Never mix datasets without explicit source/field labels.

## 23. Important files

- `frontend/src/app/`: route pages.
- `frontend/src/components/layout/`: `AppShell`, `TopNav`, headers, dashboard shell.
- `frontend/src/components/geospatial/`: `GeospatialPanel`, `WellMap`, `OffsetRadarTable`.
- `frontend/src/store/useDrillStore.ts`: active-well, telemetry, scenario, risk state.
- `frontend/src/lib/api.ts`: typed API client and telemetry conversion.
- `src/api/main.py`: FastAPI app, lifespan, CORS, route registration.
- `src/api/routes/`: wells, incidents, telemetry, trajectory, risk, alerts, ingestion, Copilot.
- `src/api/schemas/`: Pydantic contracts.
- `src/layer4_knowledge_graph/seed_data.py`: Northwind seed source.
- `src/layer4_knowledge_graph/db_service.py`: SQLite schema, seed marker, queries.
- `src/layer4_knowledge_graph/hybrid_retriever.py` and `vector_store.py`: Chroma retrieval/indexing.
- `src/layer5_copilot/`: Copilot, extraction, risk, and alert logic.
- `tests/`: backend and compatibility regression suite.
- `.env.example`, `frontend/.env.example`, ignored `frontend/.env.local`: environment configuration.
- `memory.md`: this handoff.

## 24. Git / branch state

- Source worktree branch: `agents/project-restructuring-plan`.
- Intended target repository: `C:\Users\Anil\Desktop\geodrill-ai`.
- Previous baseline: `main` / `origin/main`.
- Intended Phase 1 commit message: `feat: complete Phase 1 NWIS operational foundation`.
- Phase 1 commit: `75b1a8d`.
- Remote branch: `origin/agents/project-restructuring-plan`.
- Never commit directly to `main`; push only `agents/project-restructuring-plan` after verification.

## 25. Handoff rules for future agents

Before modifying code:

1. Read `memory.md`.
2. Check `git status`.
3. Check the current branch.
4. Read only the relevant handoff section and source files.
5. Do not re-audit the entire codebase unless this document is contradicted.
6. Preserve canonical Northwind data.
7. Preserve the working Leaflet map and ResizeObserver implementation.
8. Preserve environment-based API and CARTO configuration.
9. Never expose or commit credentials.
10. Do not start Phase 2 while Phase 1 is being validated/frozen.
11. Update `memory.md` for significant architectural changes.
12. Record validation results after substantial changes.
