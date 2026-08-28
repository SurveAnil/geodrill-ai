"""Shared safeguards for user-supplied document uploads."""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


async def read_validated_upload(
    file: UploadFile,
    *,
    allowed_extensions: set[str],
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> bytes:
    """Read a bounded upload and perform basic extension/content validation."""
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in allowed_extensions:
        if allowed_extensions == {".pdf"}:
            detail = f"Unsupported file format '{filename}'. Only PDF documents (.pdf) are supported."
        else:
            allowed = ", ".join(sorted(allowed_extensions))
            detail = f"Unsupported file format '{filename}'. Allowed extensions: {allowed}."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    contents = await file.read(max_bytes + 1)
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds the {max_bytes // (1024 * 1024)} MB limit.",
        )
    if not contents:
        detail = "The uploaded PDF file is empty (0 bytes)." if allowed_extensions == {".pdf"} else "The uploaded file is empty."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    # Do not trust the filename or client-provided content type.
    if extension == ".pdf" and not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid PDF document.",
        )
    if extension == ".docx" and not contents.startswith(b"PK"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid DOCX document.",
        )
    if extension == ".las" and b"~version" not in contents[:8192].lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid LAS document.",
        )
    if extension == ".witsml":
        try:
            text = contents.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not valid WITSML/XML text.",
            )
        if "<" not in text or ">" not in text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not valid WITSML/XML text.",
            )
    return contents
