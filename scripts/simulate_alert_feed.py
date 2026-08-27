"""
simulate_alert_feed.py
======================
Simulates a real-time depth feed (e.g., eRTMAC / WITSML stream) stepping through
drilling depths for an active well and calling the proactive risk assessment
service at each step.

Generates real-time alerts whenever upcoming historical incidents from offset
wells cross into MEDIUM or HIGH risk levels.

Usage:
    python scripts/simulate_alert_feed.py [--well-id 15/9-F-13] [--start 2300] [--stop 2900] [--step 20]
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Optional

# Ensure project root is in python path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.layer4_knowledge_graph.db_service import db_service
from src.layer5_copilot.incident_correlator import correlate_ahead
from src.layer5_copilot.risk_scorer import score_risk


def simulate_drilling_run(
    active_well_id: str = "15/9-F-13",
    start_depth_m: float = 2300.0,
    stop_depth_m: float = 2900.0,
    step_m: float = 20.0,
    lookahead_m: float = 50.0,
    formation: Optional[str] = None,
    delay_sec: float = 0.1,
) -> None:
    """
    Steps an active well through depth readings and evaluates upcoming hazards.
    """
    print("=" * 80)
    print(" GeoDrill AI -- Real-Time Proactive Alert Feed Simulation")
    print(f" Active Well: {active_well_id} | Depth Range: {start_depth_m:.0f}m - {stop_depth_m:.0f}m | Lookahead: {lookahead_m:.0f}m")
    print("=" * 80)

    db_service.init_db()

    # Check if active well exists, or register placeholder if demoing
    if not db_service.well_exists(active_well_id):
        print(f"[*] Active well '{active_well_id}' not found in DB. Available wells:")
        for w in db_service.list_wells():
            print(f"    - {w['well_id']} ({w.get('field_name', 'Unknown Field')})")
        print("[*] Proceeding with simulation using registered offset wells...")

    current_depth = start_depth_m
    alert_count = 0

    while current_depth <= stop_depth_m:
        events_ahead = correlate_ahead(
            active_well_id=active_well_id,
            current_depth_m=current_depth,
            formation=formation,
            lookahead_m=lookahead_m,
        )

        risk = score_risk(events_ahead)
        level = risk["risk_level"].upper()
        score = risk["risk_score"]

        status_tag = "[INFO]"
        if level == "HIGH":
            status_tag = "[HIGH RISK ALERT]"
            alert_count += 1
        elif level == "MEDIUM":
            status_tag = "[MEDIUM RISK ALERT]"
            alert_count += 1

        if level in ("MEDIUM", "HIGH"):
            print(f"\n! {status_tag} @ {current_depth:.1f}m MD (Score: {score}/100)")
            print(f"   Lookahead: Scanning {current_depth:.1f}m -> {current_depth + lookahead_m:.1f}m")
            print(f"   Summary: {risk['explanation']}")
            print("   Contributing Historical Offset Incidents:")
            for ev in risk["contributing_events"]:
                print(
                    f"     - Well {ev['well_id']} @ {ev['depth_m']}m [{ev['event_type']}]: "
                    f"{ev['description']} (Source: {ev['source_doc']}, p.{ev['source_page']})"
                )
        else:
            print(f". [NORMAL @ {current_depth:.1f}m MD] Score: {score}/100 -- Clear interval", end="\r")

        current_depth += step_m
        if delay_sec > 0:
            time.sleep(delay_sec)

    print("\n" + "=" * 80)
    print(f"Simulation completed. Total proactive warnings generated: {alert_count}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate real-time depth alert feed.")
    parser.add_argument("--well-id", default="15/9-F-13", help="Active well identifier")
    parser.add_argument("--start", type=float, default=2300.0, help="Starting depth in metres")
    parser.add_argument("--stop", type=float, default=2900.0, help="Ending depth in metres")
    parser.add_argument("--step", type=float, default=20.0, help="Depth step in metres")
    parser.add_argument("--lookahead", type=float, default=50.0, help="Lookahead distance in metres")
    parser.add_argument("--formation", default=None, help="Target formation filter")
    parser.add_argument("--delay", type=float, default=0.05, help="Simulation delay in seconds")

    args = parser.parse_args()
    simulate_drilling_run(
        active_well_id=args.well_id,
        start_depth_m=args.start,
        stop_depth_m=args.stop,
        step_m=args.step,
        lookahead_m=args.lookahead,
        formation=args.formation,
        delay_sec=args.delay,
    )
