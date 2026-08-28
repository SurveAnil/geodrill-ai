"""Bounded, process-local telemetry history for the Phase 3 foundation."""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict, List

from src.api.schemas.telemetry_schemas import TelemetryPoint


class TelemetryStore:
    """Thread-safe bounded history; no disk or unbounded growth is incurred."""

    def __init__(self, max_points_per_well: int = 3600, retention_seconds: int = 600) -> None:
        self._points: Dict[str, deque[TelemetryPoint]] = defaultdict(
            lambda: deque(maxlen=max_points_per_well)
        )
        self._retention = timedelta(seconds=retention_seconds)
        self._lock = Lock()

    def append(self, points: List[TelemetryPoint]) -> int:
        with self._lock:
            for point in points:
                self._points[point.well_id].append(point)
            return len(points)

    def recent(self, well_id: str, limit: int) -> List[TelemetryPoint]:
        cutoff = datetime.now(timezone.utc) - self._retention
        with self._lock:
            values = [p for p in self._points.get(well_id, ()) if p.timestamp >= cutoff]
            return sorted(values, key=lambda point: point.timestamp)[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._points.clear()


telemetry_store = TelemetryStore()
