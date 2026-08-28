"""Measured-depth and formation correlation helpers."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping, Sequence
from .survey_calculator import interpolate_depth

def correlate_depths(source: Sequence[Mapping[str, Any]], targets: Sequence[Mapping[str, Any]], tolerance_m: float = 10.0) -> List[Dict[str, Any]]:
    if tolerance_m < 0 or not __import__("math").isfinite(tolerance_m):
        raise ValueError("tolerance_m must be finite and non-negative")
    result = []
    for target in targets:
        depth = float(target["depth_m"])
        if not source: continue
        match = min(source, key=lambda x: abs(float(x["depth_m"]) - depth))
        delta = float(match["depth_m"]) - depth
        if abs(delta) <= tolerance_m:
            result.append({"target": dict(target), "match": dict(match), "offset_m": delta, "within_tolerance": True})
    return result

def correlate_formations(formation_tops: Sequence[Mapping[str, Any]], trajectory: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    output = []
    for top in formation_tops:
        md = top.get("top_depth_m", top.get("md"))
        if md is None: raise ValueError("formation top requires top_depth_m")
        location = interpolate_depth(trajectory, float(md))
        output.append({**dict(top), **location, "explanation": f"Interpolated trajectory at MD {float(md):.3f} m"})
    return output