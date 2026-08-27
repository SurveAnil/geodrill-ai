"""
test_geospatial.py
==================
Unit and API integration tests for great-circle Haversine distance calculations,
spatial radius queries across registered wells, null-coordinate handling,
and the GET /api/v1/wells/nearby endpoint.
"""

import math
import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.layer4_knowledge_graph.db_service import DatabaseService, haversine_distance


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_geospatial.db")
    service = DatabaseService(db_path=db_file)
    service.init_db()
    return service


def test_haversine_formula_known_coordinates():
    # London (51.5074 N, 0.1278 W) to Paris (48.8566 N, 2.3522 E) is ~343-344 km
    london_lat, london_lon = 51.5074, -0.1278
    paris_lat, paris_lon = 48.8566, 2.3522
    dist = haversine_distance(london_lat, london_lon, paris_lat, paris_lon)
    assert 340.0 < dist < 350.0

    # Same coordinate distance must be 0
    assert haversine_distance(58.4394, 1.8875, 58.4394, 1.8875) == 0.0

    # 1 degree latitude difference is ~111.2 km
    dist_1deg_lat = haversine_distance(0.0, 0.0, 1.0, 0.0)
    assert 110.0 < dist_1deg_lat < 112.0


def test_query_wells_within_radius(temp_db):
    # Insert test wells:
    # Reference: Well-A at (58.4394, 1.8875)
    # Well-B: ~4.5 km away (58.4800, 1.8875)
    # Well-C: ~51.2 km away (58.9000, 1.8875)
    # Well-Null: missing coordinates (None, None)
    with temp_db.get_connection() as conn:
        conn.execute(
            "INSERT INTO wells (well_id, operator, field_name, latitude, longitude, total_depth_m) VALUES (?, ?, ?, ?, ?, ?)",
            ("15/9-F-11B", "Statoil", "Volve", 58.4394, 1.8875, 3200.0),
        )
        conn.execute(
            "INSERT INTO wells (well_id, operator, field_name, latitude, longitude, total_depth_m) VALUES (?, ?, ?, ?, ?, ?)",
            ("15/9-F-12", "Statoil", "Volve", 58.4800, 1.8875, 3350.0),
        )
        conn.execute(
            "INSERT INTO wells (well_id, operator, field_name, latitude, longitude, total_depth_m) VALUES (?, ?, ?, ?, ?, ?)",
            ("16/1-1", "Aker BP", "Ivar Aasen", 58.9000, 1.8875, 2900.0),
        )
        conn.execute(
            "INSERT INTO wells (well_id, operator, field_name, latitude, longitude, total_depth_m) VALUES (?, ?, ?, ?, ?, ?)",
            ("15/9-LEGACY", "Statoil", "Volve", None, None, 2500.0),
        )

    # 1. Radius 10 km: should return 15/9-F-11B and 15/9-F-12 only
    nearby_10k = temp_db.query_wells_within_radius(
        center_lat=58.4394,
        center_lon=1.8875,
        radius_km=10.0,
    )
    well_ids_10k = [w["well_id"] for w in nearby_10k]
    assert "15/9-F-11B" in well_ids_10k
    assert "15/9-F-12" in well_ids_10k
    assert "16/1-1" not in well_ids_10k
    assert "15/9-LEGACY" not in well_ids_10k
    assert len(nearby_10k) == 2

    # Verify nearest-first sorting
    assert nearby_10k[0]["well_id"] == "15/9-F-11B"
    assert nearby_10k[0]["distance_km"] == 0.0
    assert nearby_10k[1]["well_id"] == "15/9-F-12"
    assert nearby_10k[1]["distance_km"] > 4.0

    # 2. Exclude reference well
    nearby_excluded = temp_db.query_wells_within_radius(
        center_lat=58.4394,
        center_lon=1.8875,
        radius_km=10.0,
        exclude_well_id="15/9-F-11B",
    )
    assert len(nearby_excluded) == 1
    assert nearby_excluded[0]["well_id"] == "15/9-F-12"

    # 3. Radius 60 km: should return all 3 non-null wells sorted nearest-first
    nearby_60k = temp_db.query_wells_within_radius(
        center_lat=58.4394,
        center_lon=1.8875,
        radius_km=60.0,
    )
    assert len(nearby_60k) == 3
    assert [w["well_id"] for w in nearby_60k] == ["15/9-F-11B", "15/9-F-12", "16/1-1"]
    assert nearby_60k[0]["distance_km"] < nearby_60k[1]["distance_km"] < nearby_60k[2]["distance_km"]


def test_api_wells_nearby_endpoint(monkeypatch, temp_db):
    from src.layer4_knowledge_graph import db_service as db_mod

    monkeypatch.setattr(db_mod, "db_service", temp_db)
    from src.api.routes import wells_routes
    monkeypatch.setattr(wells_routes, "db_service", temp_db)

    with temp_db.get_connection() as conn:
        conn.execute(
            "INSERT INTO wells (well_id, operator, field_name, latitude, longitude, total_depth_m) VALUES (?, ?, ?, ?, ?, ?)",
            ("15/9-F-11B", "Statoil", "Volve", 58.4394, 1.8875, 3200.0),
        )
        conn.execute(
            "INSERT INTO wells (well_id, operator, field_name, latitude, longitude, total_depth_m) VALUES (?, ?, ?, ?, ?, ?)",
            ("15/9-F-12", "Statoil", "Volve", 58.4800, 1.8875, 3350.0),
        )

    client = TestClient(app)

    # Valid query
    resp = client.get("/api/v1/wells/nearby", params={"lat": 58.4394, "lon": 1.8875, "radius_km": 10.0})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert "distance_km" in data[0]
    assert data[0]["well_id"] == "15/9-F-11B"

    # Query with exclude_well_id
    resp = client.get("/api/v1/wells/nearby", params={"lat": 58.4394, "lon": 1.8875, "radius_km": 10.0, "exclude_well_id": "15/9-F-11B"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["well_id"] == "15/9-F-12"

    # Validation errors: invalid lat
    resp_bad_lat = client.get("/api/v1/wells/nearby", params={"lat": 95.0, "lon": 1.8875})
    assert resp_bad_lat.status_code == 400
    assert "latitude" in resp_bad_lat.json()["detail"].lower()

    # Validation errors: invalid lon
    resp_bad_lon = client.get("/api/v1/wells/nearby", params={"lat": 58.0, "lon": -195.0})
    assert resp_bad_lon.status_code == 400
    assert "longitude" in resp_bad_lon.json()["detail"].lower()

    # Validation errors: negative radius
    resp_bad_radius = client.get("/api/v1/wells/nearby", params={"lat": 58.0, "lon": 1.0, "radius_km": -5.0})
    assert resp_bad_radius.status_code == 400
    assert "radius_km" in resp_bad_radius.json()["detail"]
