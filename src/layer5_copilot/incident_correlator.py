"""
incident_correlator.py
======================
Given an active well's current position (depth + formation), finds relevant
historical incidents from OTHER wells — both at the current depth and in the
upcoming interval the well is about to drill into.

This is the "proactive alerting" layer from GeoDrill AI's problem statement:
it answers "given a live depth/formation right now, is there a historical
pattern I should know about" — deliberately separate from Stage 2's semantic
search, which answers "what happened, described in words."
"""

from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from src.layer4_knowledge_graph.db_service import DatabaseService, db_service

logger = logging.getLogger(__name__)


def _group_and_sort_by_proximity(
    events: List[Dict[str, Any]],
    reference_depth_m: float,
) -> List[Dict[str, Any]]:
    """
    Groups events by event_type (preserving order of first occurrence),
    then sorts each group by proximity to reference_depth_m (closest first).
    Returns a flat list with the grouped/sorted ordering.
    """
    groups: OrderedDict[str, List[Dict[str, Any]]] = OrderedDict()
    for ev in events:
        et = ev.get("event_type", "other")
        if et not in groups:
            groups[et] = []
        groups[et].append(ev)

    result: List[Dict[str, Any]] = []
    for _event_type, group in groups.items():
        group.sort(key=lambda e: abs((e.get("depth_m") or 0.0) - reference_depth_m))
        result.extend(group)

    return result


def correlate_at_depth(
    active_well_id: str,
    current_depth_m: float,
    formation: Optional[str] = None,
    window_m: float = 100.0,
    db: Optional[DatabaseService] = None,
) -> List[Dict[str, Any]]:
    """
    Finds historical incidents from offset wells at a symmetric depth window
    around the current depth.

    Thin wrapper around query_events_near(direction="both") with grouping
    by event_type and sorting by proximity to current_depth_m.

    Args:
        active_well_id: The well currently being drilled (excluded from results).
        current_depth_m: Current measured depth in metres.
        formation: Optional geological formation filter.
        window_m: Search radius (+/- metres). Default 100m.
        db: Optional DatabaseService instance (defaults to the module singleton).

    Returns:
        List of event dicts, grouped by event_type and sorted by proximity.
        Each event retains full citation fields (well_id, source_doc, source_page,
        source_snippet).
    """
    service = db or db_service
    events = service.query_events_near(
        well_id=active_well_id,
        depth_m=current_depth_m,
        window_m=window_m,
        formation=formation,
        direction="both",
    )
    return _group_and_sort_by_proximity(events, current_depth_m)


def correlate_ahead(
    active_well_id: str,
    current_depth_m: float,
    formation: Optional[str] = None,
    lookahead_m: float = 50.0,
    db: Optional[DatabaseService] = None,
) -> List[Dict[str, Any]]:
    """
    Proactive alert: finds historical incidents from offset wells in the
    UPCOMING depth interval [current_depth_m, current_depth_m + lookahead_m].

    This is the core "warn the engineer BEFORE reaching a historically risky
    zone" function — the key differentiator from correlate_at_depth(), which
    looks in both directions.

    Args:
        active_well_id: The well currently being drilled (excluded from results).
        current_depth_m: Current measured depth in metres.
        formation: Optional geological formation filter.
        lookahead_m: How far ahead to scan (metres). Default 50m.
        db: Optional DatabaseService instance (defaults to the module singleton).

    Returns:
        List of event dicts in the upcoming interval, grouped by event_type
        and sorted by proximity. Each event retains full citation fields.
    """
    service = db or db_service
    events = service.query_events_near(
        well_id=active_well_id,
        depth_m=current_depth_m,
        window_m=lookahead_m,
        formation=formation,
        direction="ahead",
    )
    return _group_and_sort_by_proximity(events, current_depth_m)
