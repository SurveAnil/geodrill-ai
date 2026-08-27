"""
glossary_normalizer.py
======================
Query abbreviation expansion for oil & gas drilling terminology.
Normalizes common acronyms (e.g., NPT -> non-productive time, LCM -> lost circulation material)
prior to vector embedding to boost semantic recall.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict

DEFAULT_GLOSSARY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "glossary",
    "drilling_terms.json",
)

# Hardcoded fallback dictionary in case file is absent
FALLBACK_GLOSSARY: Dict[str, str] = {
    "ROP": "rate of penetration",
    "LCM": "lost circulation material",
    "NPT": "non-productive time",
    "BOP": "blowout preventer",
    "WOB": "weight on bit",
    "MD": "measured depth",
    "TVD": "true vertical depth",
    "WCR": "well completion report",
    "DDR": "daily drilling report",
    "ECD": "equivalent circulating density",
    "TD": "total depth",
    "LOT": "leak-off test",
    "FIT": "formation integrity test",
    "MWD": "measurement while drilling",
    "LWD": "logging while drilling",
    "BHA": "bottom hole assembly",
    "POOH": "pull out of hole",
    "RIH": "run in hole",
}


class GlossaryNormalizer:
    """Expands domain abbreviations in queries and narrative texts."""

    def __init__(self, glossary_path: str = DEFAULT_GLOSSARY_PATH):
        self.glossary: Dict[str, str] = self._load_glossary(glossary_path)

    def _load_glossary(self, path: str) -> Dict[str, str]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    if isinstance(data, dict):
                        return {k.upper(): v for k, v in data.items()}
            except Exception:
                pass
        return {k.upper(): v for k, v in FALLBACK_GLOSSARY.items()}

    def normalize_query(self, query: str) -> str:
        """
        Expands abbreviations in a query string using case-insensitive word boundary matching.
        Example: 'any NPT near 2400m' -> 'any non-productive time (NPT) near 2400m'
        """
        if not query or not query.strip():
            return query

        normalized = query
        for term, expansion in self.glossary.items():
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            if pattern.search(normalized):
                # Expand term with both the expansion and the original acronym for comprehensive retrieval
                normalized = pattern.sub(f"{expansion} ({term.upper()})", normalized)

        return normalized


# Default singleton instance
glossary_normalizer = GlossaryNormalizer()


def normalize_query(query: str) -> str:
    """Convenience functional wrapper."""
    return glossary_normalizer.normalize_query(query)
