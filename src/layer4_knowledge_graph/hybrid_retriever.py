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
import math
import re
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
        min_similarity: float = 0.0,
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
        try:
            vector_results = self.vector_store.similarity_search(
                query=normalized_query, top_k=max(top_k * 3, top_k),
                formation=formation, min_similarity=min_similarity,
            )
        except TypeError:  # compatibility with older/custom VectorStore adapters
            vector_results = self.vector_store.similarity_search(
                query=normalized_query, top_k=max(top_k * 3, top_k), formation=formation
            )
        # Lightweight sparse lexical retrieval.  It deliberately uses only the
        # standard library, and is fused with dense evidence rather than
        # allowing a keyword hit to bypass the similarity threshold.
        tokens = set(re.findall(r"[a-z0-9]+", normalized_query.casefold()))
        lexical: Dict[str, float] = {}
        collection = getattr(self.vector_store, "collection", None)
        if collection is not None and tokens:
            try:
                raw = collection.get(include=["documents", "metadatas"])
                docs = raw.get("documents") or []
                metas = raw.get("metadatas") or []
                for idx, doc in enumerate(docs):
                    meta = metas[idx] if idx < len(metas) else {}
                    if formation and str(meta.get("formation", "")).strip().casefold() != formation.strip().casefold():
                        continue
                    words = re.findall(r"[a-z0-9]+", str(doc).casefold())
                    if not words:
                        continue
                    counts = {word: words.count(word) for word in set(words)}
                    score = sum((1.0 + math.log1p(counts[t])) for t in tokens if t in counts)
                    if score:
                        lexical[str(meta.get("event_id", raw.get("ids", [""])[idx] if idx < len(raw.get("ids", [])) else ""))] = score / math.sqrt(len(words))
            except Exception:
                logger.debug("Sparse retrieval unavailable", exc_info=True)

        dense_max = max((float(item.get("similarity_score", 0.0)) for item in vector_results), default=1.0) or 1.0
        ranked = []
        seen = set()
        for rank, item in enumerate(vector_results):
            key = str(item.get("event_id") or item.get("source_doc") or item.get("document_text", ""))
            if key in seen:
                continue
            seen.add(key)
            dense = float(item.get("similarity_score", 0.0)) / dense_max
            sparse = lexical.get(key, 0.0)
            item["lexical_score"] = round(sparse, 4)
            item["retrieval_score"] = round(0.7 * dense + 0.3 * sparse, 4)
            ranked.append(item)
        ranked.sort(key=lambda x: (-x["retrieval_score"], -float(x.get("similarity_score", 0.0)), str(x.get("event_id", ""))))
        return ranked[:top_k]


# Default singleton instance
retriever = HybridRetriever()


def retrieve_events(
    query: str,
    top_k: int = 5,
    formation: Optional[str] = None,
    min_similarity: float = 0.0,
) -> List[Dict[str, Any]]:
    """Functional wrapper for hybrid event retrieval."""
    return retriever.retrieve(query=query, top_k=top_k, formation=formation, min_similarity=min_similarity)
