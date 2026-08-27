"""Starter endpoint for frontend document ingestion uploads."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status


router = APIRouter(tags=["Documents & Ingestion"])
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".las", ".witsml"}


@router.post("/ingest-document", status_code=status.HTTP_200_OK)
async def ingest_document(file: UploadFile = File(...)) -> dict[str, str | bool]:
    """Accept a supported drilling document and return an ingestion status."""
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{filename}'. Allowed extensions: {allowed}.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    # Layer 1: Document Intelligence (OCR / Text Extraction)
    # TODO: Route the file to the format-specific extraction pipeline.

    # Layer 2: Knowledge Graph Integration (ChromaDB / Neo4j)
    # TODO: Persist extracted entities and relationships.

    return {
        "success": True,
        "filename": filename,
        "message": "Document uploaded and queued for processing.",
    }
