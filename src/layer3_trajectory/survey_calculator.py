"""Survey and trajectory calculations.

The implementation deliberately uses only the standard library.  Angles are
degrees, depths and coordinates are metres.  Minimum-curvature is the default
industry convention for converting inclination/azimuth surveys to TVD.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Sequence


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def validate_survey(points: Sequence[Mapping[str, Any]]) -> None:
    if len(points) < 1:
        raise ValueError("at least one survey station is required")
    previous = -math.inf
    for i, point in enumerate(points):
        md = _finite(point["md"], f"station {i} md")
        inc = _finite(point.get("inclination", point.get("inc", 0.0)), f"station {i} inclination")
        azi = _finite(point.get("azimuth", point.get("azi", 0.0)), f"station {i} azimuth")
        if md < 0 or md <= previous:
            raise ValueError("measured depths must be non-negative and strictly increasing")
        if not 0 <= inc <= 180:
            raise ValueError("inclination must be between 0 and 180 degrees")
        if not 0 <= azi < 360:
            raise ValueError("azimuth must be in [0, 360) degrees")
        previous = md


def minimum_curvature(points: Sequence[Mapping[str, Any]]) -> List[Dict[str, float]]:
    """Return station MD, northing, easting and TVD using minimum curvature."""
    validate_survey(points)
    result: List[Dict[str, float]] = []
    north = east = tvd = 0.0
    prev_md = prev_inc = prev_azi = None
    for point in points:
        md = float(point["md"])
        inc = float(point.get("inclination", point.get("inc", 0.0)))
        azi = float(point.get("azimuth", point.get("azi", 0.0)))
        if prev_md is not None:
            dmd = md - prev_md
            i1, i2 = math.radians(prev_inc), math.radians(inc)
            a1, a2 = math.radians(prev_azi), math.radians(azi)
            dogleg = math.acos(max(-1.0, min(1.0, math.cos(i1) * math.cos(i2) +
                math.sin(i1) * math.sin(i2) * math.cos(a2 - a1))))
            rf = 1.0 if dogleg < 1e-12 else 2.0 / dogleg * math.tan(dogleg / 2.0)
            north += dmd / 2 * (math.sin(i1) * math.cos(a1) + math.sin(i2) * math.cos(a2)) * rf
            east += dmd / 2 * (math.sin(i1) * math.sin(a1) + math.sin(i2) * math.sin(a2)) * rf
            tvd += dmd / 2 * (math.cos(i1) + math.cos(i2)) * rf
        result.append({"md": md, "inclination": inc, "azimuth": azi,
                       "northing": north, "easting": east, "tvd": tvd})
        prev_md, prev_inc, prev_azi = md, inc, azi
    return result


def interpolate_depth(stations: Sequence[Mapping[str, Any]], md: float) -> Dict[str, float]:
    """Linearly interpolate TVD and coordinates at a measured depth."""
    path = minimum_curvature(stations)
    md = _finite(md, "md")
    if md < path[0]["md"] or md > path[-1]["md"]:
        raise ValueError("md is outside the surveyed interval")
    for left, right in zip(path, path[1:]):
        if md <= right["md"]:
            fraction = (md - left["md"]) / (right["md"] - left["md"])
            return {key: left[key] + fraction * (right[key] - left[key])
                    for key in ("md", "northing", "easting", "tvd")}
    return dict(path[-1])


# Descriptive aliases kept for callers that use the common terminology.
calculate_trajectory = minimum_curvature
interpolate_trajectory = interpolate_depth