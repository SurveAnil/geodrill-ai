"""
table_extractor.py
==================
Extraction and formatting helpers for table structures in PDF documents.
"""

from __future__ import annotations

from typing import List, Optional
from src.api.schemas.document_schemas import PageContent


def format_tables_as_text(page: PageContent) -> str:
    """
    Flattens a page's extracted tables into clean markdown-formatted text
    suitable for LLM prompt ingestion.
    """
    if not page.tables:
        return ""

    out: List[str] = []
    for t_idx, table in enumerate(page.tables, start=1):
        out.append(f"  [Table {t_idx} on page {page.page_number}]")
        for row in table:
            clean_row = [str(c).strip() if c else "" for c in row]
            out.append("    | " + " | ".join(clean_row) + " |")
    return "\n".join(out)


def format_document_tables_as_text(pages: List[PageContent]) -> str:
    """Format every extracted table while retaining page/table provenance."""
    return "\n\n".join(
        formatted for page in pages if (formatted := format_tables_as_text(page))
    )


def extract_key_value_pairs(tables: List[List[List[Optional[str]]]]) -> dict[str, str]:
    """
    Heuristic helper to extract two-column key-value attribute tables commonly
    found on Well Completion Report header pages.
    """
    attributes: dict[str, str] = {}
    for table in tables:
        for row in table:
            if len(row) == 2 and row[0] and row[1]:
                key = row[0].strip().rstrip(":")
                val = row[1].strip()
                if key and val:
                    attributes[key] = val
    return attributes
