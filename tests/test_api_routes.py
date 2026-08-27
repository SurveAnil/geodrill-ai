"""
test_api_routes.py
==================
Integration and end-to-end tests for FastAPI REST endpoints.
Tests document upload, error handling, review-queue retrieval, and offset correlation queries.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.layer4_knowledge_graph.db_service import DatabaseService, db_service
from src.layer1_ingestion.document_pipeline import pipeline
from tests.generate_test_reports import generate_all_samples


@pytest.fixture(scope="module")
def setup_samples():
    sample_dir = tempfile.mkdtemp(prefix="geodrill_samples_")
    generate_all_samples(base_dir=sample_dir)
    yield sample_dir


@pytest.fixture
def test_client():
    # Use isolated temporary database for API test session
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    test_db = DatabaseService(db_path=db_path)
    test_db.init_db()

    # Swap singleton instance
    original_db = db_service.db_path
    db_service.db_path = db_path
    pipeline.db = test_db

    with TestClient(app) as client:
        yield client

    # Restore
    db_service.db_path = original_db
    if os.path.exists(db_path):
        os.remove(db_path)


def test_process_file_valid_wcr_pdf(test_client, setup_samples):
    wcr_pdf_path = os.path.join(setup_samples, "wcr_volve_15_9_f11b.pdf")
    assert os.path.exists(wcr_pdf_path)

    with open(wcr_pdf_path, "rb") as fh:
        response = test_client.post(
            "/api/v1/documents/process-file",
            files={"file": ("wcr_volve_15_9_f11b.pdf", fh, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["source_doc"] == "wcr_volve_15_9_f11b.pdf"
    ext_result = data["extraction_result"]
    assert ext_result["well_header"]["well_id"] == "15/9-F-11B"
    assert len(ext_result["events"]) == 2
    assert ext_result["overall_confidence"] == "high"


def test_process_file_offset_ddr_pdf(test_client, setup_samples):
    ddr_pdf_path = os.path.join(setup_samples, "ddr_volve_15_9_f12.pdf")
    assert os.path.exists(ddr_pdf_path)

    with open(ddr_pdf_path, "rb") as fh:
        response = test_client.post(
            "/api/v1/documents/process-file",
            files={"file": ("ddr_volve_15_9_f12.pdf", fh, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    ext_result = data["extraction_result"]
    assert ext_result["well_header"]["well_id"] == "15/9-F-12"
    assert len(ext_result["events"]) == 1
    assert ext_result["events"][0]["event_type"] == "kick"


def test_process_scanned_file_and_review_queue(test_client, setup_samples):
    scan_pdf_path = os.path.join(setup_samples, "scanned_legacy_log_scan.pdf")
    assert os.path.exists(scan_pdf_path)

    with open(scan_pdf_path, "rb") as fh:
        response = test_client.post(
            "/api/v1/documents/process-file",
            files={"file": ("scanned_legacy_log_scan.pdf", fh, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    ext_result = data["extraction_result"]
    assert ext_result["extraction_method"] == "manual_flag"
    assert ext_result["overall_confidence"] == "low"

    # Now verify GET /api/v1/documents/review-queue surfaces it
    queue_resp = test_client.get("/api/v1/documents/review-queue")
    assert queue_resp.status_code == 200
    items = queue_resp.json()
    assert len(items) >= 1
    found = any("scanned_legacy_log_scan.pdf" in item["source_doc"] for item in items)
    assert found is True


def test_process_file_invalid_extension(test_client):
    response = test_client.post(
        "/api/v1/documents/process-file",
        files={"file": ("report.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF documents (.pdf) are supported" in response.json()["detail"]


def test_process_file_empty_payload(test_client):
    response = test_client.post(
        "/api/v1/documents/process-file",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "empty (0 bytes)" in response.json()["detail"]


def test_process_file_corrupt_pdf(test_client):
    response = test_client.post(
        "/api/v1/documents/process-file",
        files={"file": ("corrupt.pdf", b"%PDF-1.4 garbage corrupt bytes...", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Corrupted or invalid PDF" in response.json()["detail"]


def test_incident_queries_and_correlation(test_client, setup_samples):
    # Upload both wells to populate DB
    wcr_pdf_path = os.path.join(setup_samples, "wcr_volve_15_9_f11b.pdf")
    ddr_pdf_path = os.path.join(setup_samples, "ddr_volve_15_9_f12.pdf")

    with open(wcr_pdf_path, "rb") as fh:
        test_client.post("/api/v1/documents/process-file", files={"file": ("wcr_volve_15_9_f11b.pdf", fh, "application/pdf")})
    with open(ddr_pdf_path, "rb") as fh:
        test_client.post("/api/v1/documents/process-file", files={"file": ("ddr_volve_15_9_f12.pdf", fh, "application/pdf")})

    # Test GET /api/v1/incidents/wells
    wells_resp = test_client.get("/api/v1/incidents/wells")
    assert wells_resp.status_code == 200
    well_ids = [w["well_id"] for w in wells_resp.json()]
    assert "15/9-F-11B" in well_ids
    assert "15/9-F-12" in well_ids

    # Test GET /api/v1/incidents/well/15/9-F-11B
    well_detail = test_client.get("/api/v1/incidents/well/15/9-F-11B")
    assert well_detail.status_code == 200
    assert well_detail.json()["well"]["operator"] == "Statoil ASA"
    assert len(well_detail.json()["events"]) == 2

    # Test GET /api/v1/incidents/correlate-near (look for offset events around 2500m excluding 15/9-F-12)
    corr_resp = test_client.get(
        "/api/v1/incidents/correlate-near",
        params={"well_id": "15/9-F-12", "depth_m": 2480.0, "window_m": 100.0, "formation": "Hugin Formation"},
    )
    assert corr_resp.status_code == 200
    matches = corr_resp.json()
    assert len(matches) == 1
    assert matches[0]["well_id"] == "15/9-F-11B"
    assert matches[0]["event_type"] == "mud_loss"
