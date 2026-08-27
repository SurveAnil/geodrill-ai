"""
risk_scorer.py
==============
Transparent, rule-based risk scoring for drilling incident correlation.

DESIGN NOTE — READ THIS BEFORE EVALUATING:
This is a deterministic, rule-based heuristic — NOT a trained ML model. This is
a deliberate design choice, not a shortcut. A real predictive model requires:
  (a) a labeled outcome dataset (did the offset incident actually recur?),
  (b) enough training samples across diverse formations/operators/rig types, and
  (c) proper train/test splits with statistical validation.
None of these are available in a hackathon setting with a handful of sample wells.
A rule-based scorer that is transparent, explainable, and honest about its
limitations is more defensible than an overclaimed "AI model" that falls apart
under a follow-up question about validation methodology.

If this moves past hackathon stage, the severity weights should be reviewed and
adjusted by an actual drilling engineer, and a proper statistical model should be
considered once a sufficient labeled dataset is available.
"""

from __future__ import annotations

from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Severity weight table
# ---------------------------------------------------------------------------
# These weights reflect general drilling operational severity / cost impact,
# NOT statistical derivation from this dataset. They are a starting heuristic:
#   - kick (10):            highest severity — potential well control event
#   - stuck_pipe (9):       major NPT driver, can escalate to sidetrack
#   - overpressure (8):     well control precursor, requires immediate response
#   - cementing_issue (6):  zonal isolation failure, costly remediation
#   - fishing (6):          significant NPT and cost
#   - mud_loss (5):         common but can escalate (total losses → kick risk)
#   - torque_spike (4):     operational indicator, often manageable
#   - npt_other (3):        generic non-productive time
#   - other (2):            catch-all
#
# A drilling engineer should review and adjust these if this moves past
# hackathon stage — e.g., in some basins, mud losses may warrant higher weight
# than stuck pipe depending on formation characteristics.
EVENT_SEVERITY_WEIGHTS: Dict[str, int] = {
    "kick": 10,
    "stuck_pipe": 9,
    "overpressure": 8,
    "cementing_issue": 6,
    "fishing": 6,
    "mud_loss": 5,
    "torque_spike": 4,
    "npt_other": 3,
    "other": 2,
}

# ---------------------------------------------------------------------------
# Risk level thresholds
# ---------------------------------------------------------------------------
# Bounded score 0–100, mapped to categorical levels:
#   score < 30   → "low"    — few/minor historical incidents
#   30 ≤ score ≤ 65 → "medium" — notable pattern, increased vigilance warranted
#   score > 65   → "high"   — multiple severe incidents, proactive mitigation needed
#
# These thresholds are heuristic starting points. In a production system they
# would be calibrated against actual incident recurrence rates.
RISK_THRESHOLD_LOW = 30
RISK_THRESHOLD_HIGH = 65

# Scaling factors for combining frequency and severity into a 0–100 score.
# frequency_score = count * FREQUENCY_SCALE (each incident adds signal)
# severity_score  = sum of severity weights * SEVERITY_SCALE
FREQUENCY_SCALE = 8
SEVERITY_SCALE = 3


def score_risk(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes a transparent, rule-based risk score from a list of correlated
    historical drilling events.

    This function is deterministic and pure — no LLM call, no randomness, no
    external API. It runs on structured data using plain arithmetic, which means
    it is fast, free, and fully testable without mocking anything.

    Args:
        events: List of event dicts (output of correlate_ahead() or
                correlate_at_depth()). Each dict must contain at minimum:
                event_type, well_id, depth_m, source_doc, source_page.

    Returns:
        dict with keys:
            risk_score (float): Bounded 0–100.
            risk_level (str): "low" | "medium" | "high".
            explanation (str): Plain-language summary of what drove the score.
            contributing_events (list[dict]): The events that contributed,
                each retaining full citation fields.
    """
    if not events:
        return {
            "risk_score": 0,
            "risk_level": "low",
            "explanation": (
                "No historical incidents found in offset wells within this "
                "depth interval. Risk assessment: low."
            ),
            "contributing_events": [],
        }

    # --- Frequency component ---
    count = len(events)
    frequency_score = count * FREQUENCY_SCALE

    # --- Severity component ---
    total_severity = 0
    type_counts: Dict[str, int] = {}
    for ev in events:
        et = ev.get("event_type", "other")
        weight = EVENT_SEVERITY_WEIGHTS.get(et, EVENT_SEVERITY_WEIGHTS["other"])
        total_severity += weight
        type_counts[et] = type_counts.get(et, 0) + 1

    severity_score = total_severity * SEVERITY_SCALE

    # --- Combined bounded score ---
    raw_score = frequency_score + severity_score
    risk_score = min(100.0, round(raw_score, 1))

    # --- Categorical level ---
    if risk_score >= RISK_THRESHOLD_HIGH:
        risk_level = "high"
    elif risk_score >= RISK_THRESHOLD_LOW:
        risk_level = "medium"
    else:
        risk_level = "low"

    # --- Plain-language explanation ---
    explanation_parts: List[str] = []
    for et, cnt in sorted(type_counts.items(), key=lambda x: -EVENT_SEVERITY_WEIGHTS.get(x[0], 0)):
        label = et.replace("_", " ")
        if cnt == 1:
            explanation_parts.append(f"{cnt} {label} incident")
        else:
            explanation_parts.append(f"{cnt} {label} incidents")

    # Collect unique well IDs for context
    offset_wells = sorted(set(ev.get("well_id", "unknown") for ev in events))
    wells_str = ", ".join(offset_wells)

    explanation = (
        f"{count} historical incident(s) recorded in offset well(s) ({wells_str}) "
        f"within this depth interval: {', '.join(explanation_parts)}. "
        f"Risk assessment: {risk_level} (score {risk_score}/100). "
        f"Note: this is a rule-based heuristic score, not a trained predictive model."
    )

    # --- Contributing events with citation fields ---
    contributing = []
    for ev in events:
        contributing.append({
            "event_id": ev.get("event_id"),
            "well_id": ev.get("well_id"),
            "event_type": ev.get("event_type"),
            "depth_m": ev.get("depth_m"),
            "formation": ev.get("formation"),
            "event_date": ev.get("event_date"),
            "description": ev.get("description"),
            "confidence": ev.get("confidence"),
            "source_doc": ev.get("source_doc"),
            "source_page": ev.get("source_page"),
            "source_snippet": ev.get("source_snippet"),
        })

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "contributing_events": contributing,
    }
