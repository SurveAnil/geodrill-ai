"""
test_copilot_retrieval.py
=========================
Integration tests for Stage 2 Knowledge Retrieval Layer:
  1. Inline ingestion -> SQL + Chroma vector store.
  2. HybridRetriever with glossary acronym normalization.
  3. Grounded LLM answer synthesis with strict citations.
  4. Out-of-scope query handling (zero-hallucination guarantee).
  5. FastAPI endpoint POST /api/v1/copilot/search.
"""

import os
import tempfile
import pytest
import chromadb
from fastapi.testclient import TestClient

from src.api.main import app
from src.layer4_knowledge_graph.db_service import DatabaseService, db_service
from src.layer4_knowledge_graph.vector_store import VectorStore, vector_store
from src.layer4_knowledge_graph.hybrid_retriever import HybridRetriever, retriever
from src.layer1_ingestion.document_pipeline import DocumentPipeline, pipeline
from src.layer5_copilot.tools import answer_with_citations, validate_citations
from tests.generate_test_reports import generate_all_samples


@pytest.fixture(scope="module")
def sample_reports():
    sample_dir = tempfile.mkdtemp(prefix="geodrill_copilot_samples_")
    generate_all_samples(base_dir=sample_dir)
    yield sample_dir


@pytest.fixture
def integrated_environment(sample_reports):
    # 1. Temporary SQLite database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    test_db = DatabaseService(db_path=db_path)
    test_db.init_db()

    # 2. Ephemeral Chroma vector store
    chroma_client = chromadb.EphemeralClient()
    test_vstore = VectorStore(client=chroma_client)

    # 3. Test Retriever and Pipeline
    test_retriever = HybridRetriever(v_store=test_vstore)
    test_pipeline = DocumentPipeline(
        db=test_db,
        v_store=test_vstore,
    )

    # Patch singletons for the test
    orig_db_path = db_service.db_path
    db_service.db_path = db_path

    orig_vstore = vector_store.collection
    vector_store.collection = test_vstore.collection

    orig_retriever_vstore = retriever.vector_store
    retriever.vector_store = test_vstore

    pipeline.db = test_db
    pipeline.vector_store = test_vstore

    # Ingest test reports inline
    wcr_path = os.path.join(sample_reports, "wcr_volve_15_9_f11b.pdf")
    ddr_path = os.path.join(sample_reports, "ddr_volve_15_9_f12.pdf")

    test_pipeline.process_document(wcr_path, persist=True)
    test_pipeline.process_document(ddr_path, persist=True)

    yield {
        "db": test_db,
        "vstore": test_vstore,
        "retriever": test_retriever,
        "pipeline": test_pipeline,
    }

    # Restore singletons
    db_service.db_path = orig_db_path
    vector_store.collection = orig_vstore
    retriever.vector_store = orig_retriever_vstore
    if os.path.exists(db_path):
        os.remove(db_path)


def test_inline_embedding_and_semantic_retrieval(integrated_environment):
    env = integrated_environment
    retriever = env["retriever"]

    # Search for mud loss in Hugin Formation
    results = retriever.retrieve("What mud loss events occurred in the Hugin formation?", top_k=3)
    assert len(results) >= 1
    top_match = results[0]
    assert top_match["well_id"] == "15/9-F-11B"
    assert top_match["event_type"] == "mud_loss"
    assert top_match["source_page"] == 3
    assert "Hugin" in (top_match["formation"] or "")
    assert top_match["similarity_score"] > 0.0


def test_glossary_abbreviation_expansion_in_search(integrated_environment):
    env = integrated_environment
    retriever = env["retriever"]

    # Search using LCM acronym
    results = retriever.retrieve("Did any well pump LCM pill?", top_k=2)
    assert len(results) >= 1
    found_lcm = any("LCM" in r["document_text"] or "mud_loss" in r["event_type"] for r in results)
    assert found_lcm is True


def test_grounded_answer_with_citations(integrated_environment):
    env = integrated_environment
    retriever = env["retriever"]

    query = "What mud losses were encountered in the Hugin formation and how were they mitigated?"
    events = retriever.retrieve(query=query, top_k=3)

    synthesis = answer_with_citations(query=query, retrieved_events=events)
    answer = synthesis["answer"]

    # Verify claim grounding and explicit citations
    assert "15/9-F-11B" in answer
    assert "wcr_volve_15_9_f11b.pdf" in answer or "p. 3" in answer
    assert "LCM pill" in answer or "losses" in answer
    assert len(synthesis["sources"]) >= 1


def test_stuck_pipe_citation_grounding(integrated_environment):
    env = integrated_environment
    retriever = env["retriever"]

    query = "Tell me about stuck pipe incidents in Skagerrak formation"
    events = retriever.retrieve(query=query, top_k=3)

    synthesis = answer_with_citations(query=query, retrieved_events=events)
    answer = synthesis["answer"]

    assert "15/9-F-11B" in answer
    assert "Skagerrak" in answer
    assert "p. 5" in answer or "wcr_volve_15_9_f11b.pdf" in answer


def test_out_of_scope_query_returns_insufficient_information(integrated_environment):
    query = "What cementing issues occurred in the North Sea Forties field?"
    # No matching events in knowledge base
    synthesis = answer_with_citations(query=query, retrieved_events=[])
    assert "Insufficient information" in synthesis["answer"]
    assert len(synthesis["sources"]) == 0


def test_citation_validation_rejects_unretrieved_source():
    event = {"well_id": "W-1", "source_doc": "report.pdf", "source_page": 2}
    assert validate_citations("[Well W-1, report.pdf, p. 2]", [event])
    assert not validate_citations("[Well W-2, report.pdf, p. 2]", [event])


def test_copilot_search_api_endpoint(integrated_environment):
    with TestClient(app) as client:
        # Valid search request
        response = client.post(
            "/api/v1/copilot/search",
            json={
                "query": "What gas kick happened in well 15/9-F-12?",
                "top_k": 3,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "kick" in data["query"].lower()
        assert "15/9-F-12" in data["answer"]
        assert len(data["sources"]) >= 1
        assert data["sources"][0]["well_id"] == "15/9-F-12"

        # Empty query returns 400 Bad Request
        empty_resp = client.post(
            "/api/v1/copilot/search",
            json={"query": "   "},
        )
        assert empty_resp.status_code == 400
        assert "cannot be empty" in empty_resp.json()["detail"]
