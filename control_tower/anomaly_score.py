#!/usr/bin/env python3
"""Deterministic v0 control-tower anomaly scorer.

This executable is intentionally small and dependency-free. It proves the first
runtime boundary for GAIA control-tower work without claiming operational
maturity. The command reads a ControlTowerDecisionCard fixture and emits a
RiskExposureRecord plus WorkOrderCandidate in one bundle.

Usage:
  python3 control_tower/anomaly_score.py \
    fixtures/control-tower/navigation-asset-health-card.sample.v1.json \
    /tmp/control-tower-anomaly-output.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected JSON object in {path}")
    return value


def require_fields(obj: Dict[str, Any], fields: Iterable[str], scope: str) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        fail(f"{scope} missing required fields: {', '.join(missing)}")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def risk_class(score: float) -> str:
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


def build_output(card: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(
        card,
        ["card_id", "created_at", "situation_type", "scope", "evidence_refs", "recommendations", "policy", "provenance"],
        "control tower decision card",
    )

    scope = card.get("scope", {})
    if not isinstance(scope, dict):
        fail("card.scope must be an object")

    recommendations = card.get("recommendations", [])
    if not isinstance(recommendations, list) or not recommendations:
        fail("card.recommendations must be a non-empty array")

    confidence = card.get("confidence", {}) if isinstance(card.get("confidence", {}), dict) else {}
    decision_confidence = confidence.get("decision_confidence", 0.5)
    if not isinstance(decision_confidence, (int, float)):
        decision_confidence = 0.5

    priority_weight = {
        "low": 0.25,
        "medium": 0.45,
        "high": 0.7,
        "critical": 0.9,
    }
    max_priority = 0.25
    for recommendation in recommendations:
        if isinstance(recommendation, dict):
            max_priority = max(max_priority, priority_weight.get(str(recommendation.get("priority", "low")), 0.25))

    evidence_refs = card.get("evidence_refs", [])
    if not isinstance(evidence_refs, list):
        evidence_refs = []
    evidence_factor = min(1.0, 0.25 + 0.1 * len(evidence_refs))

    likelihood = clamp(0.35 + 0.25 * max_priority)
    impact = clamp(max_priority + 0.1)
    overall = clamp((likelihood * 0.45) + (impact * 0.45) + (evidence_factor * 0.10))

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    asset_refs = scope.get("asset_refs", []) if isinstance(scope.get("asset_refs", []), list) else []
    route_refs = scope.get("route_refs", []) if isinstance(scope.get("route_refs", []), list) else []
    spatial_refs = scope.get("spatial_refs", []) if isinstance(scope.get("spatial_refs", []), list) else []

    risk = {
        "record_version": "v1",
        "risk_id": "risk-exposure-generated-from-" + card["card_id"],
        "risk_type": "route_disruption" if card.get("situation_type") == "asset_health" else "other",
        "created_at": now,
        "scope": {
            "asset_refs": asset_refs,
            "route_refs": route_refs,
            "spatial_refs": spatial_refs,
            "temporal_scope": scope.get("temporal_scope", {}),
        },
        "score": {
            "likelihood": round(likelihood, 3),
            "impact": round(impact, 3),
            "overall": round(overall, 3),
            "confidence": round(float(decision_confidence), 3),
            "risk_class": risk_class(overall),
        },
        "business_impact": {
            "downtime_cost_estimate": 0,
            "currency": "USD",
            "service_level_impact": "not asserted by v0 deterministic fixture scorer",
            "customer_impact": "not asserted by v0 deterministic fixture scorer",
            "insurance_exposure_ref": "none",
        },
        "mitigations": [
            {
                "mitigation_id": "mitigation-generated-review-" + card["card_id"],
                "description": "Review highest-priority recommendation and preserve evidence trail before operational action.",
                "policy_ref": "policy://gaia/control-tower/human-review-v1",
            }
        ],
        "evidence_refs": evidence_refs,
        "model_refs": card.get("model_refs", []),
        "provenance": {
            "source_refs": [card["card_id"]],
            "runtime_refs": ["gaia-control-tower-anomaly-runtime@v0.1.0"],
            "generated_by": "control_tower/anomaly_score.py",
            "content_hash": "sha256:generated-at-runtime-placeholder",
        },
        "classification": {
            "data_class": "internal",
            "retention_class": "standard",
            "handling_tags": ["generated", "control-tower", "risk"],
        },
    }

    first_recommendation = recommendations[0] if isinstance(recommendations[0], dict) else {}
    work_order = {
        "candidate_version": "v1",
        "candidate_id": "work-order-candidate-generated-from-" + card["card_id"],
        "created_at": now,
        "asset_refs": asset_refs or ["unknown-asset"],
        "issue_summary": card.get("summary", "Generated control-tower candidate"),
        "issue_type": "inspection",
        "priority": first_recommendation.get("priority", "medium"),
        "recommended_task": first_recommendation.get("description", "Review control-tower recommendation."),
        "required_skills": ["operator-review"],
        "required_material_refs": [],
        "evidence_refs": evidence_refs,
        "risk_refs": [risk["risk_id"]],
        "decision_card_refs": [card["card_id"]],
        "approval_state": {"status": "approval_required"},
        "policy_constraints": first_recommendation.get("policy_constraints", ["Human approval required"]),
        "provenance": {
            "source_refs": [card["card_id"]],
            "runtime_refs": ["gaia-control-tower-anomaly-runtime@v0.1.0"],
            "model_refs": card.get("model_refs", []),
            "generated_by": "control_tower/anomaly_score.py",
            "content_hash": "sha256:generated-at-runtime-placeholder",
        },
        "classification": {
            "data_class": "internal",
            "retention_class": "standard",
            "handling_tags": ["generated", "control-tower", "work-order-candidate"],
        },
    }

    return {
        "artifact_version": "v1",
        "artifact_type": "gaia.control_tower.anomaly_score.output",
        "created_at": now,
        "source_card_id": card["card_id"],
        "risk_exposure": risk,
        "work_order_candidate": work_order,
        "policy": {
            "action_status": "approval_required",
            "notes": "Generated output is advisory and non-actuating until approved by policy-bound workflow.",
        },
    }


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    card = load_json(source)
    output = build_output(card)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
