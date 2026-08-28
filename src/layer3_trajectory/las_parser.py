"""Small, defensive LAS 2.x ASCII parser (no third-party dependency)."""
from __future__ import annotations
import math
import re
from typing import Dict, List, Union

def parse_las(text: str) -> Dict[str, object]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("LAS content is empty")
    section, curves, rows = "", [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("~"):
            section = line[1:].split()[0].upper()
            continue
        if section.startswith("C"):
            m = re.match(r"([^\s.:]+)", line)
            if m: curves.append(m.group(1).upper())
            continue
        if section.startswith("A") and curves:
            tokens = re.split(r"[,\s]+", line)
            try: values = [float(t) for t in tokens[:len(curves)]]
            except ValueError: continue
            if len(values) < len(curves) or any(not math.isfinite(v) for v in values): continue
            rows.append(dict(zip(curves, values)))
    if not curves or not rows:
        raise ValueError("LAS must contain a ~C (curve) and ~A (ASCII) section")
    aliases = {"md": ("MD", "DEPT", "DEPTH"), "inclination": ("INCL", "INC"), "azimuth": ("AZIM", "AZI")}
    stations = []
    for row in rows:
        key = next((k for k in aliases["md"] if k in row), None)
        if key is None: raise ValueError("LAS is missing a depth curve (MD/DEPT/DEPTH)")
        item = {"md": row[key]}
        for target in ("inclination", "azimuth"):
            key = next((k for k in aliases[target] if k in row), None)
            if key is not None: item[target] = row[key]
        stations.append(item)
    return {"curves": curves, "stations": stations, "row_count": len(stations)}

def parse_las_file(path: Union[str, "os.PathLike[str]"]) -> Dict[str, object]:
    from pathlib import Path
    return parse_las(Path(path).read_text(encoding="utf-8", errors="replace"))


parse_las_content = parse_las