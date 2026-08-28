"""Starter endpoint for frontend document ingestion uploads."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from src.api.schemas.document_schemas import IngestionJobResponse, IngestionJobStatus
from src.layer1_ingestion.document_pipeline import pipeline
from src.layer4_knowledge_graph.db_service import db_service
from src.api.upload_validation import read_validated_upload
from starlette.concurrency import run_in_threadpool


router = APIRouter(tags=["Documents & Ingestion"])
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".las", ".witsml"}
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "data" / "ingestion_uploads"
logger = logging.getLogger(__name__)


def _process_ingestion_job(job_id: str) -> None:
    """Run a queued job and always remove its temporary upload."""
    job = db_service.get_ingestion_job(job_id)
    if not job:
        return
    path = Path(job["stored_path"])
    db_service.update_ingestion_job(job_id, IngestionJobStatus.RUNNING)
    try:
        pipeline.process_document(path, persist=True, source_doc_name=job["filename"])
        db_service.update_ingestion_job(job_id, IngestionJobStatus.SUCCEEDED)
    except Exception as exc:
        logger.exception("Ingestion job %s failed", job_id)
        # Keep the bounded diagnostic for polling clients; HTTP pipeline errors
        # are still sanitized at the synchronous document endpoint.
        db_service.update_ingestion_job(job_id, IngestionJobStatus.FAILED, str(exc)[:2000])
    finally:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Unable to clean up upload for ingestion job %s", job_id)


def _job_response(job: dict) -> IngestionJobResponse:
    return IngestionJobResponse(**{k: job[k] for k in ("job_id", "filename", "status", "error", "created_at", "updated_at")})


@router.post("/ingest-document", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> IngestionJobResponse:
    """Safely store a supported upload and queue durable background processing."""
    filename = file.filename or ""
    contents = await read_validated_upload(file, allowed_extensions=ALLOWED_EXTENSIONS)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    stored_path = UPLOAD_DIR / f"{job_id}{Path(filename).suffix.lower()}"
    try:
        stored_path.write_bytes(contents)
        job = await run_in_threadpool(
            db_service.create_ingestion_job, job_id, Path(filename).name, str(stored_path)
        )
    except Exception:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to create ingestion job.")
    background_tasks.add_task(_process_ingestion_job, job_id)
    return _job_response(job)


@router.post(
    "/ingestion-jobs",
    response_model=IngestionJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@router.post(
    "/ingest/jobs",
    response_model=IngestionJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def create_ingestion_job(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> IngestionJobResponse:
    """Alias for creating an asynchronous ingestion job."""
    return await ingest_document(background_tasks, file)


@router.get("/ingestion-jobs/{job_id}", response_model=IngestionJobResponse)
@router.get("/ingest/jobs/{job_id}", response_model=IngestionJobResponse, include_in_schema=False)
async def get_ingestion_job(job_id: str) -> IngestionJobResponse:
    job = await run_in_threadpool(db_service.get_ingestion_job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")
    return _job_response(job)
