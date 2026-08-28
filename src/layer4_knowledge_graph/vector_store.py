"""
vector_store.py
===============
Chroma vector store layer for semantic search over extracted drilling incidents.
Stores event-level embeddings with metadata for grounded retrieval and offset-well queries.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Union
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from src.api.schemas.incident_schemas import DrillingEvent

logger = logging.getLogger(__name__)

DEFAULT_CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "chroma_db",
)
COLLECTION_NAME = "drilling_events"


def normalize_metadata_value(value: Any) -> str:
    """Canonical form used for metadata matching (without changing source values)."""
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def build_event_text(event: DrillingEvent) -> str:
    """
    Constructs a standardized, self-contained embeddable text chunk from a DrillingEvent.
    Format: Well {well_id} | {event_type} at {depth_m}m in {formation}: {description} {symptom} {action_taken}
    """
    depth_str = f"{event.depth_m:.1f}m" if event.depth_m is not None else "unstated depth"
    formation_str = event.formation if event.formation else "unstated formation"
    event_type_str = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)

    parts = [f"Well {event.well_id} | {event_type_str} at {depth_str} in {formation_str}: {event.description}"]
    if event.symptom:
        parts.append(f"Symptom: {event.symptom}")
    if event.action_taken:
        parts.append(f"Action: {event.action_taken}")

    return " ".join(parts)


class VectorStore:
    """Vector database manager wrapping ChromaDB for event-level drilling incident embeddings."""

    def __init__(
        self,
        persist_directory: Optional[str] = DEFAULT_CHROMA_PATH,
        client: Optional[ClientAPI] = None,
        collection_name: str = COLLECTION_NAME,
    ):
        self.collection_name = collection_name
        if client:
            self.client = client
        elif persist_directory:
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.EphemeralClient()

        self.collection: Collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def embed_and_upsert(
        self,
        event: DrillingEvent,
        event_id: int,
        source_doc: str = "",
        source_page: Optional[int] = None,
        source_snippet: Optional[str] = None,
        source_section: Optional[str] = None,
    ) -> None:
        """
        Embeds the constructed event text and upserts it into the Chroma collection
        using event_id as the primary key for direct joining to relational SQL rows.
        """
        document_text = build_event_text(event)
        doc_id = str(event_id)

        metadata: Dict[str, Union[str, int, float]] = {
            "event_id": event_id,
            "well_id": event.well_id,
            "event_type": event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
            "depth_m": float(event.depth_m) if event.depth_m is not None else 0.0,
            "formation": str(event.formation) if event.formation else "",
            "description": str(event.description),
            "confidence": event.confidence.value if hasattr(event.confidence, "value") else str(event.confidence),
            "source_doc": str(source_doc or ""),
            "source_page": int(source_page) if source_page is not None else int(event.source_page or 0),
            "source_snippet": str(source_snippet or event.source_snippet or ""),
            "source_section": str(source_section or getattr(event, "source_section", "") or ""),
            "formation_normalized": normalize_metadata_value(event.formation),
            "well_id_normalized": normalize_metadata_value(event.well_id),
        }

        self.collection.upsert(
            ids=[doc_id],
            documents=[document_text],
            metadatas=[metadata],
        )
        logger.debug("Upserted event %d (%s) into vector store", event_id, event.well_id)

    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        formation: Optional[str] = None,
        min_similarity: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Searches for semantically similar drilling events to the given natural language query.
        Optionally filters results by formation.
        """
        if not query or not query.strip() or top_k <= 0:
            return []
        min_similarity = max(0.0, min(1.0, float(min_similarity)))

        # Chroma's equality filter is case-sensitive.  Retrieve candidates and
        # apply canonical matching below so ingestion/query formatting differs safely.
        where_filter: Optional[Dict[str, Any]] = None

        count = self.collection.count()
        if count == 0:
            return []

        n_results = min(max(top_k * 3, top_k), count)
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        matched_events: List[Dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return matched_events

        ids = results["ids"][0]
        distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0] * len(ids)
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else [{}] * len(ids)
        documents = results.get("documents", [[]])[0] if results.get("documents") else [""] * len(ids)

        for i, doc_id in enumerate(ids):
            meta = metadatas[i] if i < len(metadatas) else {}
            dist = distances[i] if i < len(distances) else 0.0
            doc_text = documents[i] if i < len(documents) else ""

            # Cosine distance to similarity conversion: similarity = 1 - distance
            similarity = max(0.0, min(1.0, 1.0 - float(dist)))
            if similarity < min_similarity:
                continue
            if formation and normalize_metadata_value(meta.get("formation")) != normalize_metadata_value(formation):
                continue

            item: Dict[str, Any] = {
                "event_id": meta.get("event_id", int(doc_id) if doc_id.isdigit() else 0),
                "well_id": meta.get("well_id", ""),
                "event_type": meta.get("event_type", ""),
                "depth_m": meta.get("depth_m", None) if meta.get("depth_m") != 0.0 else None,
                "formation": meta.get("formation", "") or None,
                "description": meta.get("description", ""),
                "confidence": meta.get("confidence", "medium"),
                "source_doc": meta.get("source_doc", ""),
                "source_page": meta.get("source_page", None) if meta.get("source_page") != 0 else None,
                "source_snippet": meta.get("source_snippet", "") or None,
                "source_section": meta.get("source_section", "") or None,
                "similarity_score": round(similarity, 4),
                "document_text": doc_text,
            }
            matched_events.append(item)

        # Stable ordering makes ties reproducible across Chroma versions.
        matched_events.sort(key=lambda x: (-x["similarity_score"], str(x.get("event_id", ""))))
        return matched_events[:top_k]


# Default singleton instance
vector_store = VectorStore()
