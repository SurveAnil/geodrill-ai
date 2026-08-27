"""
copilot_routes.py
=================
FastAPI routes for Copilot semantic search and citation-grounded Q&A.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.layer4_knowledge_graph.hybrid_retriever import retriever
from src.layer4_knowledge_graph.glossary_normalizer import normalize_query
from src.layer5_copilot.tools import answer_with_citations

router = APIRouter(prefix="/copilot", tags=["Copilot & Knowledge Retrieval"])


class CopilotSearchRequest(BaseModel):
    """Natural language search request payload."""
    query: str = Field(..., description="Natural language drilling question or search term")
    formation: Optional[str] = Field(None, description="Optional geological formation filter")
    top_k: int = Field(5, ge=1, le=20, description="Number of most relevant events to retrieve")


class CopilotSearchResponse(BaseModel):
    """Grounded search response with source citations."""
    query: str
    normalized_query: str
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)


@router.post(
    "/search",
    response_model=CopilotSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic search over drilling knowledge base with grounded citations",
)
async def copilot_search(request: CopilotSearchRequest) -> CopilotSearchResponse:
    """
    Takes a natural-language drilling engineering question, expands domain abbreviations,
    retrieves semantically matching drilling incident chunks from ChromaDB, and returns
    a grounded answer with explicit citations (well_id, source_doc, source_page).
    """
    clean_query = request.query.strip()
    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )

    normalized_q = normalize_query(clean_query)
    retrieved_events = retriever.retrieve(
        query=clean_query,
        top_k=request.top_k,
        formation=request.formation,
    )

    synthesis_result = answer_with_citations(
        query=clean_query,
        retrieved_events=retrieved_events,
    )

    return CopilotSearchResponse(
        query=clean_query,
        normalized_query=normalized_q,
        answer=synthesis_result["answer"],
        sources=synthesis_result["sources"],
    )
