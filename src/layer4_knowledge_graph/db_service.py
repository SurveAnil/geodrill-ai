"""
db_service.py
=============
Persistence service for well headers, drilling events, formation tops,
casing programs, cementing records, mud programs, and document status tracking.
Provides relational storage, offset-well spatial radius queries, and geological correlation queries.
"""

from __future__ import annotations

import logging
import math
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Optional, Dict, Any, Tuple, Sequence

from src.api.schemas.document_schemas import ExtractionResult, DocumentReviewItem, ExtractionMethod
from src.api.schemas.incident_schemas import Confidence, WellHeader, DrillingEvent, EventType
from src.api.schemas.well_program_schemas import (
    FormationTop,
    CasingProgram,
    CementingRecord,
    MudProgramEntry,
)

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "geodrill.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS wells (
    well_id         TEXT PRIMARY KEY,
    operator        TEXT,
    field_name      TEXT,
    spud_date       TEXT,
    completion_date TEXT,
    latitude        REAL,
    longitude       REAL,
    total_depth_m   REAL
);

CREATE TABLE IF NOT EXISTS events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id         TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    depth_m         REAL,
    formation       TEXT,
    event_date      TEXT,
    description     TEXT NOT NULL,
    symptom         TEXT,
    action_taken    TEXT,
    confidence      TEXT NOT NULL,
    source_doc      TEXT,
    source_page     INTEGER,
    source_snippet  TEXT,
    FOREIGN KEY (well_id) REFERENCES wells(well_id)
);

CREATE TABLE IF NOT EXISTS documents (
    source_doc          TEXT PRIMARY KEY,
    extraction_method   TEXT,
    overall_confidence  TEXT,
    processing_notes    TEXT,
    needs_review        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS formation_tops (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id         TEXT NOT NULL,
    formation_name  TEXT NOT NULL,
    top_depth_m     REAL NOT NULL,
    base_depth_m    REAL,
    lithology_notes TEXT,
    source_doc      TEXT,
    source_page     INTEGER,
    source_snippet  TEXT,
    FOREIGN KEY (well_id) REFERENCES wells(well_id)
);

CREATE TABLE IF NOT EXISTS casing_program (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id         TEXT NOT NULL,
    casing_type     TEXT NOT NULL,
    depth_set_m     REAL NOT NULL,
    size_inches     REAL,
    weight_ppf      REAL,
    source_doc      TEXT,
    source_page     INTEGER,
    source_snippet  TEXT,
    FOREIGN KEY (well_id) REFERENCES wells(well_id)
);

CREATE TABLE IF NOT EXISTS cementing_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id         TEXT NOT NULL,
    casing_stage    TEXT,
    cement_type     TEXT,
    volume_bbl      REAL,
    top_of_cement_m REAL,
    issues_noted    TEXT,
    source_doc      TEXT,
    source_page     INTEGER,
    source_snippet  TEXT,
    FOREIGN KEY (well_id) REFERENCES wells(well_id)
);

CREATE TABLE IF NOT EXISTS mud_program (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id                 TEXT NOT NULL,
    depth_interval_start_m  REAL NOT NULL,
    depth_interval_end_m    REAL,
    mud_type                TEXT,
    mud_weight_sg           REAL,
    losses_observed         TEXT,
    source_doc              TEXT,
    source_page             INTEGER,
    source_snippet          TEXT,
    FOREIGN KEY (well_id) REFERENCES wells(well_id)
);

CREATE INDEX IF NOT EXISTS idx_events_well_depth ON events(well_id, depth_m);
CREATE INDEX IF NOT EXISTS idx_events_formation ON events(formation);
CREATE INDEX IF NOT EXISTS idx_wells_location ON wells(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_formation_tops_well ON formation_tops(well_id);
CREATE INDEX IF NOT EXISTS idx_formation_tops_name ON formation_tops(formation_name);
CREATE INDEX IF NOT EXISTS idx_casing_well ON casing_program(well_id);
CREATE INDEX IF NOT EXISTS idx_cementing_well ON cementing_records(well_id);
CREATE INDEX IF NOT EXISTS idx_mud_well ON mud_program(well_id);
"""


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance in kilometres between two geographic coordinates
    using the Haversine formula on a spherical Earth (mean radius ≈ 6371.0 km).
    """
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


class DatabaseService:
    """Database management service supporting SQLite storage for GeoDrill AI."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Yields an active database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initializes database tables and indexes if they do not already exist."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)

    def store_extraction_result(self, result: ExtractionResult) -> List[Tuple[int, DrillingEvent]]:
        """
        Persists a complete ExtractionResult to the database.
        Upserts well header and document status, appends drilling events,
        and optionally persists well program data (formation tops, casing, cementing, mud).
        Returns list of (event_id, DrillingEvent) tuples for downstream vector embedding.
        """
        wh = result.well_header
        persisted_events: List[Tuple[int, DrillingEvent]] = []

        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO wells (
                    well_id, operator, field_name, spud_date,
                    completion_date, latitude, longitude, total_depth_m
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(well_id) DO UPDATE SET
                    operator=COALESCE(excluded.operator, wells.operator),
                    field_name=COALESCE(excluded.field_name, wells.field_name),
                    spud_date=COALESCE(excluded.spud_date, wells.spud_date),
                    completion_date=COALESCE(excluded.completion_date, wells.completion_date),
                    latitude=COALESCE(excluded.latitude, wells.latitude),
                    longitude=COALESCE(excluded.longitude, wells.longitude),
                    total_depth_m=COALESCE(excluded.total_depth_m, wells.total_depth_m)
                """,
                (
                    wh.well_id,
                    wh.operator,
                    wh.field_name,
                    wh.spud_date.isoformat() if wh.spud_date else None,
                    wh.completion_date.isoformat() if wh.completion_date else None,
                    wh.latitude,
                    wh.longitude,
                    wh.total_depth_m,
                ),
            )

            for ev in result.events:
                cursor = conn.execute(
                    """
                    INSERT INTO events (
                        well_id, event_type, depth_m, formation, event_date,
                        description, symptom, action_taken, confidence,
                        source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ev.well_id,
                        ev.event_type.value,
                        ev.depth_m,
                        ev.formation,
                        ev.event_date.isoformat() if ev.event_date else None,
                        ev.description,
                        ev.symptom,
                        ev.action_taken,
                        ev.confidence.value,
                        result.source_doc,
                        ev.source_page,
                        ev.source_snippet,
                    ),
                )
                event_id = cursor.lastrowid or 0
                persisted_events.append((event_id, ev))

            # Store formation tops if present
            for ft in getattr(result, "formation_tops", []):
                conn.execute(
                    """
                    INSERT INTO formation_tops (
                        well_id, formation_name, top_depth_m, base_depth_m,
                        lithology_notes, source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ft.well_id,
                        ft.formation_name,
                        ft.top_depth_m,
                        ft.base_depth_m,
                        ft.lithology_notes,
                        result.source_doc,
                        ft.source_page,
                        ft.source_snippet,
                    ),
                )

            # Store casing program if present
            for cp in getattr(result, "casing_program", []):
                conn.execute(
                    """
                    INSERT INTO casing_program (
                        well_id, casing_type, depth_set_m, size_inches,
                        weight_ppf, source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cp.well_id,
                        cp.casing_type.value if hasattr(cp.casing_type, "value") else str(cp.casing_type),
                        cp.depth_set_m,
                        cp.size_inches,
                        cp.weight_ppf,
                        result.source_doc,
                        cp.source_page,
                        cp.source_snippet,
                    ),
                )

            # Store cementing records if present
            for cr in getattr(result, "cementing_records", []):
                conn.execute(
                    """
                    INSERT INTO cementing_records (
                        well_id, casing_stage, cement_type, volume_bbl,
                        top_of_cement_m, issues_noted, source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cr.well_id,
                        cr.casing_stage,
                        cr.cement_type,
                        cr.volume_bbl,
                        cr.top_of_cement_m,
                        cr.issues_noted,
                        result.source_doc,
                        cr.source_page,
                        cr.source_snippet,
                    ),
                )

            # Store mud program if present
            for mp in getattr(result, "mud_program", []):
                conn.execute(
                    """
                    INSERT INTO mud_program (
                        well_id, depth_interval_start_m, depth_interval_end_m,
                        mud_type, mud_weight_sg, losses_observed,
                        source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mp.well_id,
                        mp.depth_interval_start_m,
                        mp.depth_interval_end_m,
                        mp.mud_type,
                        mp.mud_weight_sg,
                        mp.losses_observed,
                        result.source_doc,
                        mp.source_page,
                        mp.source_snippet,
                    ),
                )

            needs_review = 1 if result.overall_confidence == Confidence.LOW or result.extraction_method == ExtractionMethod.MANUAL_FLAG else 0
            conn.execute(
                """
                INSERT INTO documents (
                    source_doc, extraction_method, overall_confidence,
                    processing_notes, needs_review
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_doc) DO UPDATE SET
                    extraction_method=excluded.extraction_method,
                    overall_confidence=excluded.overall_confidence,
                    processing_notes=excluded.processing_notes,
                    needs_review=excluded.needs_review
                """,
                (
                    result.source_doc,
                    result.extraction_method.value,
                    result.overall_confidence.value,
                    result.processing_notes,
                    needs_review,
                ),
            )

        return persisted_events

    def store_program_data(
        self,
        source_doc: str,
        formation_tops: Sequence[FormationTop] = (),
        casing_program: Sequence[CasingProgram] = (),
        cementing_records: Sequence[CementingRecord] = (),
        mud_program: Sequence[MudProgramEntry] = (),
    ) -> None:
        """
        Persists well program data (formation tops, casing, cementing, mud program)
        in an independent transaction to ensure failure isolation.
        """
        with self.get_connection() as conn:
            for ft in formation_tops:
                conn.execute(
                    """
                    INSERT INTO formation_tops (
                        well_id, formation_name, top_depth_m, base_depth_m,
                        lithology_notes, source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ft.well_id,
                        ft.formation_name,
                        ft.top_depth_m,
                        ft.base_depth_m,
                        ft.lithology_notes,
                        source_doc,
                        ft.source_page,
                        ft.source_snippet,
                    ),
                )

            for cp in casing_program:
                conn.execute(
                    """
                    INSERT INTO casing_program (
                        well_id, casing_type, depth_set_m, size_inches,
                        weight_ppf, source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cp.well_id,
                        cp.casing_type.value if hasattr(cp.casing_type, "value") else str(cp.casing_type),
                        cp.depth_set_m,
                        cp.size_inches,
                        cp.weight_ppf,
                        source_doc,
                        cp.source_page,
                        cp.source_snippet,
                    ),
                )

            for cr in cementing_records:
                conn.execute(
                    """
                    INSERT INTO cementing_records (
                        well_id, casing_stage, cement_type, volume_bbl,
                        top_of_cement_m, issues_noted, source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cr.well_id,
                        cr.casing_stage,
                        cr.cement_type,
                        cr.volume_bbl,
                        cr.top_of_cement_m,
                        cr.issues_noted,
                        source_doc,
                        cr.source_page,
                        cr.source_snippet,
                    ),
                )

            for mp in mud_program:
                conn.execute(
                    """
                    INSERT INTO mud_program (
                        well_id, depth_interval_start_m, depth_interval_end_m,
                        mud_type, mud_weight_sg, losses_observed,
                        source_doc, source_page, source_snippet
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mp.well_id,
                        mp.depth_interval_start_m,
                        mp.depth_interval_end_m,
                        mp.mud_type,
                        mp.mud_weight_sg,
                        mp.losses_observed,
                        source_doc,
                        mp.source_page,
                        mp.source_snippet,
                    ),
                )

    def query_wells_within_radius(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        exclude_well_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Finds wells located within a great-circle radius from a geographic center point.
        Uses pure-Python Haversine distance computation. Wells with null coordinates
        are safely skipped and logged.

        Args:
            center_lat: Latitude of query centre point in decimal degrees.
            center_lon: Longitude of query centre point in decimal degrees.
            radius_km: Maximum radius in kilometres.
            exclude_well_id: Optional well ID to exclude from results (e.g. active reference well).

        Returns:
            List of well dicts within radius_km, sorted nearest-first with 'distance_km'.
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM wells ORDER BY well_id").fetchall()

        nearby_wells: List[Dict[str, Any]] = []
        for row in rows:
            w_dict = dict(row)
            well_id = w_dict.get("well_id")

            if exclude_well_id and well_id == exclude_well_id:
                continue

            lat = w_dict.get("latitude")
            lon = w_dict.get("longitude")

            if lat is None or lon is None:
                logger.debug("Excluded well %s: missing coordinates (latitude=%s, longitude=%s)", well_id, lat, lon)
                continue

            dist_km = haversine_distance(center_lat, center_lon, float(lat), float(lon))
            if dist_km <= radius_km:
                w_dict["distance_km"] = round(dist_km, 4)
                nearby_wells.append(w_dict)

        # Sort nearest-first
        nearby_wells.sort(key=lambda item: item["distance_km"])
        return nearby_wells

    def query_casing_by_formation(self, formation_name: str) -> List[Dict[str, Any]]:
        """
        Cross-well correlation query: finds casing programs and cementing practices used
        across all wells that have drilled through a specified geological formation.

        Args:
            formation_name: Target formation name (case-insensitive search).

        Returns:
            List of dicts representing casing/cementing practices for wells penetrating this formation.
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT 
                    ft.formation_name,
                    ft.top_depth_m AS formation_top_depth_m,
                    ft.base_depth_m AS formation_base_depth_m,
                    ft.lithology_notes,
                    w.well_id,
                    w.operator,
                    w.field_name,
                    w.total_depth_m,
                    c.casing_type,
                    c.depth_set_m AS casing_depth_set_m,
                    c.size_inches AS casing_size_inches,
                    c.weight_ppf AS casing_weight_ppf,
                    cm.casing_stage AS cement_casing_stage,
                    cm.cement_type,
                    cm.volume_bbl AS cement_volume_bbl,
                    cm.top_of_cement_m,
                    cm.issues_noted AS cement_issues
                FROM formation_tops ft
                JOIN wells w ON w.well_id = ft.well_id
                LEFT JOIN casing_program c ON c.well_id = ft.well_id
                LEFT JOIN cementing_records cm ON cm.well_id = ft.well_id AND (cm.casing_stage = c.casing_type OR cm.casing_stage IS NULL)
                WHERE ft.formation_name LIKE ?
                ORDER BY w.well_id, c.depth_set_m
            """
            rows = conn.execute(query, (f"%{formation_name.strip()}%",)).fetchall()
            return [dict(r) for r in rows]

    def query_events_near(
        self,
        well_id: str,
        depth_m: float,
        window_m: float = 100.0,
        formation: Optional[str] = None,
        direction: str = "both",
    ) -> List[Dict[str, Any]]:
        """
        Finds drilling events in offset wells around a specified depth window,
        optionally filtered by geological formation.
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row

            if direction == "ahead":
                depth_min = depth_m
                depth_max = depth_m + window_m
            else:  # "both"
                depth_min = depth_m - window_m
                depth_max = depth_m + window_m

            query = """
                SELECT e.*, w.latitude, w.longitude, w.operator, w.field_name
                FROM events e
                JOIN wells w ON w.well_id = e.well_id
                WHERE e.well_id != ? AND e.depth_m BETWEEN ? AND ?
            """
            params: list[Any] = [well_id, depth_min, depth_max]
            if formation:
                query += " AND e.formation = ?"
                params.append(formation)

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def well_exists(self, well_id: str) -> bool:
        """Lightweight existence check for a well — avoids fetching the full row."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM wells WHERE well_id = ? LIMIT 1", (well_id,)
            ).fetchone()
            return row is not None

    def get_well(self, well_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a well header record by well_id."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM wells WHERE well_id = ?", (well_id,)).fetchone()
            return dict(row) if row else None

    def list_wells(self) -> List[Dict[str, Any]]:
        """Lists all registered wells in the database."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM wells ORDER BY well_id").fetchall()
            return [dict(r) for r in rows]

    def get_well_events(self, well_id: str) -> List[Dict[str, Any]]:
        """Retrieves all drilling events recorded for a given well."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM events WHERE well_id = ? ORDER BY depth_m ASC",
                (well_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_documents_needing_review(self) -> List[DocumentReviewItem]:
        """Retrieves all documents marked as requiring engineer review."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM documents WHERE needs_review = 1 ORDER BY source_doc ASC"
            ).fetchall()
            return [
                DocumentReviewItem(
                    source_doc=r["source_doc"],
                    extraction_method=ExtractionMethod(r["extraction_method"]),
                    overall_confidence=Confidence(r["overall_confidence"]),
                    processing_notes=r["processing_notes"],
                    needs_review=bool(r["needs_review"]),
                )
                for r in rows
            ]


# Default singleton service instance
db_service = DatabaseService()
