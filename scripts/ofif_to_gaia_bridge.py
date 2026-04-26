#!/usr/bin/env python3
"""Convert an OFIF ObservationEvent envelope into a GAIA world-state artifact.

This is a deliberately dependency-free v0 bridge proof. It performs structural
checks for the fields required by the current OFIF event envelope and
ObservationEvent schema, then emits a GAIA evidence/world-state artifact.

Usage:
  python3 scripts/ofif_to_gaia_bridge.py \
    fixtures/ofif/observation-event.sample.v1.json \
    /tmp/gaia-ofif-output.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


REQUIRED_ENVELOPE_FIELDS = [
    "envelope_version",
    "event_type",
    "event_id",
    "observed_at",
    "producer",
    "payload",
]

REQUIRED_PAYLOAD_FIELDS = ["sensor_id", "location", "media", "detections"]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_keys(obj: Dict[str, Any], keys: Iterable[str], scope: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        fail(f"{scope} missing required keys: {', '.join(missing)}")


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


def max_detection_confidence(detections: List[Dict[str, Any]]) -> float:
    values = []
    for detection in detections:
        confidence = detection.get("confidence")
        if isinstance(confidence, (int, float)):
            values.append(float(confidence))
    return max(values) if values else 0.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def convert(envelope: Dict[str, Any]) -> Dict[str, Any]:
    require_keys(envelope, REQUIRED_ENVELOPE_FIELDS, "OFIF envelope")
    if envelope.get("envelope_version") != "v1":
        fail("only OFIF envelope_version v1 is supported")

    payload = envelope["payload"]
    if not isinstance(payload, dict):
        fail("payload must be an object")
    require_keys(payload, REQUIRED_PAYLOAD_FIELDS, "OFIF ObservationEvent payload")

    location = payload.get("location", {})
    if not isinstance(location, dict):
        fail("payload.location must be an object")
    if "h3_cell" not in location:
        fail("payload.location.h3_cell is required")

    detections = payload.get("detections", [])
    if not isinstance(detections, list):
        fail("payload.detections must be an array")

    lon = location.get("lon")
    lat = location.get("lat")
    geometry = None
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        geometry = {"type": "Point", "coordinates": [lon, lat]}

    raw_confidence = max_detection_confidence(detections)
    adversarial = envelope.get("adversarial", {}) if isinstance(envelope.get("adversarial", {}), dict) else {}
    confidence_impact = adversarial.get("confidence_impact", 0.0)
    if not isinstance(confidence_impact, (int, float)):
        confidence_impact = 0.0
    bridge_confidence = clamp(raw_confidence + float(confidence_impact))

    artifact_id = f"gaia-feature-{envelope['event_id']}"
    feature_id = f"gaia-observation-{envelope['event_id']}"

    world_state_feature: Dict[str, Any] = {
        "feature_id": feature_id,
        "feature_type": "EvidenceObservation",
        "ontology_bindings": [
            "gaia:EvidenceObservation",
            "gaia:EnvironmentalContextObservation",
            "gaia:CommunicationsAvailabilityObservation",
            "gaia:AssetCustodyObservation",
            "gaia:DetectedEntityObservation",
        ],
        "spatial": {
            "primary_index": {"scheme": "h3", "value": location["h3_cell"]},
            "zone_id": location.get("zone_id"),
            "property_id": location.get("property_id"),
        },
        "temporal": {
            "observed_at": envelope["observed_at"],
            "ingested_at": envelope.get("ingested_at"),
            "valid_time_basis": "field_observation",
        },
        "observed_environment": payload.get("environment", {}),
        "detections": detections,
        "link_state": payload.get("link_state", {}),
        "custody_state": payload.get("custody_state", {}),
    }
    if geometry is not None:
        world_state_feature["spatial"]["geometry"] = geometry

    return {
        "gaia_artifact_version": "v1",
        "artifact_type": "gaia.world_state_feature.from_ofif_observation",
        "artifact_id": artifact_id,
        "source_system": "OFIF",
        "source_event_ids": [envelope["event_id"]],
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "world_state_feature": world_state_feature,
        "evidence": {
            "producer": envelope.get("producer", {}),
            "provenance": envelope.get("provenance", {}),
            "integrity": envelope.get("integrity", {}),
            "classification": envelope.get("classification", {}),
            "adversarial": adversarial,
        },
        "derived_confidence": {
            "raw_detection_confidence_max": raw_confidence,
            "adversarial_confidence_impact": float(confidence_impact),
            "bridge_confidence": bridge_confidence,
            "rule": "max_detection_confidence + adversarial_confidence_impact; clamped to [0,1]",
        },
        "invariants": [
            "Raw OFIF event was not mutated.",
            "Source event ID was preserved.",
            "Observed and ingested times remain distinct.",
            "Adversarial metadata remains attached to derived artifact.",
        ],
    }


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    source = Path(argv[1])
    target = Path(argv[2])
    envelope = load_json(source)
    artifact = convert(envelope)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
