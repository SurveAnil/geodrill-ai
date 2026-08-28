"""
test_vector_store.py
====================
Unit tests for Chroma vector store, event text chunking, and similarity search.
"""

from datetime import date
import uuid
import pytest
import chromadb

from src.api.schemas.incident_schemas import DrillingEvent, EventType, Confidence
from src.layer4_knowledge_graph.vector_store import (
    VectorStore,
    build_event_text,
)


@pytest.fixture
def ephemeral_vector_store():
    client = chromadb.EphemeralClient()
    unique_name = f"test_events_{uuid.uuid4().hex}"
    store = VectorStore(client=client, collection_name=unique_name)
    return store


def test_build_event_text():
    event = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.MUD_LOSS,
        depth_m=2450.0,
        formation="Hugin Formation",
        event_date=date(2007, 9, 12),
        description="Partial mud losses of 15 bbl/hr.",
        symptom="Pit level dropped steadily",
        action_taken="Pumped LCM pill",
        confidence=Confidence.HIGH,
    )
    chunk = build_event_text(event)
    assert "Well 15/9-F-11B" in chunk
    assert "mud_loss" in chunk
    assert "2450.0m" in chunk
    assert "Hugin Formation" in chunk
    assert "Partial mud losses of 15 bbl/hr." in chunk
    assert "Symptom: Pit level dropped steadily" in chunk
    assert "Action: Pumped LCM pill" in chunk


def test_embed_and_similarity_search(ephemeral_vector_store):
    store = ephemeral_vector_store

    event1 = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.MUD_LOSS,
        depth_m=2450.0,
        formation="Hugin Formation",
        description="Lost 15 bbl/hr mud in Hugin sandstone reservoir.",
        action_taken="Pumped 50 bbl LCM pill.",
        confidence=Confidence.HIGH,
    )
    event2 = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.STUCK_PIPE,
        depth_m=2810.0,
        formation="Skagerrak Formation",
        description="Mechanical stuck pipe while tripping in tight hole.",
        action_taken="Worked pipe free with jarring.",
        confidence=Confidence.MEDIUM,
    )

    store.embed_and_upsert(event1, event_id=1, source_doc="wcr_f11b.pdf", source_page=3)
    store.embed_and_upsert(event2, event_id=2, source_doc="wcr_f11b.pdf", source_page=5)

    # Search for mud losses
    results = store.similarity_search("mud losses and LCM pill", top_k=2)
    assert len(results) == 2
    assert results[0]["event_id"] == 1
    assert results[0]["well_id"] == "15/9-F-11B"
    assert results[0]["event_type"] == "mud_loss"
    assert results[0]["source_page"] == 3
    assert results[0]["similarity_score"] > 0.0


def test_formation_metadata_filtering(ephemeral_vector_store):
    store = ephemeral_vector_store

    event1 = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.MUD_LOSS,
        depth_m=2450.0,
        formation="Hugin Formation",
        description="Mud loss event in Hugin.",
    )
    event2 = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.STUCK_PIPE,
        depth_m=2810.0,
        formation="Skagerrak Formation",
        description="Stuck pipe in Skagerrak.",
    )

    store.embed_and_upsert(event1, event_id=1)
    store.embed_and_upsert(event2, event_id=2)

    # Filter strictly for Skagerrak Formation
    results = store.similarity_search("drilling incidents", top_k=5, formation="Skagerrak Formation")
    assert len(results) == 1
    assert results[0]["event_id"] == 2
    assert results[0]["formation"] == "Skagerrak Formation"


def test_similarity_search_empty_query_and_empty_store(ephemeral_vector_store):
    store = ephemeral_vector_store
    assert store.similarity_search("") == []
    assert store.similarity_search("any incident") == []


def test_similarity_threshold_and_normalized_formation_filter(ephemeral_vector_store):
    event = DrillingEvent(
        well_id="W-1", event_type=EventType.MUD_LOSS, formation="Hugin Formation",
        description="Mud loss recorded.",
    )
    ephemeral_vector_store.embed_and_upsert(event, event_id=1)
    assert ephemeral_vector_store.similarity_search(
        "mud loss", formation=        " hugin   formation ", min_similarity=1.1
    ) == []
    results = ephemeral_vector_store.similarity_search(
        "mud loss", formation=" hugin   formation "
    )
    assert results and results[0]["source_section"] is None
