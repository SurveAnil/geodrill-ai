"""
hybrid_retriever.py
===================
Retrieval orchestrator for GeoDrill AI.
Executes domain acronym expansion via GlossaryNormalizer followed by semantic vector search
over embedded drilling events in ChromaDB.

Architectural Note:
-------------------
In Stage 2 (MVP), this module implements the Vector Retrieval pathway.
Hybrid blending (BM25 keyword search + Neo4j knowledge graph traversal) is designed to plug
directly into this module as follow-up stages without changing API call contracts.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.layer4_knowledge_graph.glossary_normalizer import normalize_query
from src.layer4_knowledge_graph.vector_store import VectorStore, vector_store

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Orchestrates query normalization and semantic retrieval over historical drilling events."""

    def __init__(self, v_store: Optional[VectorStore] = None):
        self.vector_store = v_store or vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        formation: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant drilling event records for a natural language query.
        1. Expands drilling abbreviations (e.g. 'NPT' -> 'non-productive time (NPT)').
        2. Performs cosine similarity search over event chunks in ChromaDB.
        3. Applies optional formation metadata filtering.
        """
        if not query or not query.strip():
            return []

        # Step 1: Glossary Abbreviation Expansion
        normalized_query = normalize_query(query.strip())
        logger.debug("Normalized query: '%s' -> '%s'", query, normalized_query)

        # Step 2: Vector Similarity Search
        vector_results = self.vector_store.similarity_search(
            query=normalized_query,
            top_k=top_k,
            formation=formation,
        )

        # -------------------------------------------------------------------------
        # TODO: hybrid retrieval (BM25 + graph) — follow-up, not Stage 2 MVP
        # Future extension: blend BM25 sparse keyword scores with dense vector cosine
        # similarities using Reciprocal Rank Fusion (RRF).
        # -------------------------------------------------------------------------

        # -------------------------------------------------------------------------
        # TODO: graph entity expansion (Neo4j) — follow-up, not Stage 2 MVP
        # Future extension: traverse neighboring well nodes, lithology formations,
        # and causal failure links in Neo4j knowledge graph.
        # -------------------------------------------------------------------------

        return vector_results


# Default singleton instance
retriever = HybridRetriever()


def retrieve_events(
    query: str,
    top_k: int = 5,
    formation: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Functional wrapper for hybrid event retrieval."""
    return retriever.retrieve(query=query, top_k=top_k, formation=formation)
