"""
ocr_routes.py
=============
FastAPI routes for PDF document upload, text ingestion, and structured extraction.
Includes input validation for non-PDFs, empty payloads, and corrupted files.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import logging
from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.api.schemas.document_schemas import (
    DocumentProcessResponse,
    DocumentReviewItem,
)
from src.layer1_ingestion.document_pipeline import pipeline
from src.layer4_knowledge_graph.db_service import db_service
from src.api.upload_validation import read_validated_upload
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/documents", tags=["Documents & Ingestion"])
logger = logging.getLogger(__name__)


@router.post(
    "/process-file",
    response_model=DocumentProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and extract structured well data from a PDF report",
)
async def process_document_file(file: UploadFile = File(...)) -> DocumentProcessResponse:
    """
    Uploads a PDF document (WCR/DDR), runs text/table extraction and LLM schema structuring,
    and stores the resulting well and incident records in the database.

    - Returns **400 Bad Request** for non-PDF files, empty files, or corrupted PDFs.
    - Returns **200 OK** with structured extraction data or manual review flag.
    """
    contents = await read_validated_upload(file, allowed_extensions={".pdf"})

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = await run_in_threadpool(
            pipeline.process_document,
            tmp_path,
            persist=True,
            source_doc_name=file.filename,
        )
        return DocumentProcessResponse(
            success=True,
            source_doc=file.filename,
            extraction_result=result,
            warnings=[],
            message="Document successfully processed and stored.",
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File error: {exc}",
        )
    except ValueError as exc:
        # Detect PDF syntax or corruption errors
        err_msg = str(exc)
        if any(keyword in err_msg.lower() for keyword in ["pdf", "syntax", "corrupt", "header", "trailer", "eof"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted or invalid PDF document.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document extraction failed. Please verify the PDF and try again.",
        )
    except Exception as exc:
        if any(keyword in str(exc).lower() for keyword in ["pdf", "syntax", "corrupt", "header", "trailer", "eof"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted or invalid PDF document.",
            )
        logger.exception("Document extraction pipeline failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document extraction failed. Please try again later.",
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get(
    "/review-queue",
    response_model=List[DocumentReviewItem],
    summary="Retrieve documents flagged for engineer review",
)
async def get_review_queue() -> List[DocumentReviewItem]:
    """
    Retrieves documents that received low confidence or failed validation,
    flagged for engineer manual review.
    """
    return await run_in_threadpool(db_service.get_documents_needing_review)
