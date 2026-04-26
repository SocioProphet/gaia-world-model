#!/usr/bin/env python3
"""Check structural invariants for the GAIA OFIF bridge output.

This intentionally avoids third-party dependencies so the proof path can run in
minimal CI and bootstrap environments.

Usage:
  python3 scripts/check_ofif_bridge_invariants.py \
    fixtures/ofif/observation-event.sample.v1.json \
    /tmp/gaia-ofif-output.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


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


def assert_equal(left: Any, right: Any, label: str) -> None:
    if left != right:
        fail(f"{label} mismatch: {left!r} != {right!r}")


def assert_present(obj: Dict[str, Any], key: str, scope: str) -> Any:
    if key not in obj:
        fail(f"{scope} missing {key}")
    return obj[key]


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    source = load_json(Path(argv[1]))
    artifact = load_json(Path(argv[2]))

    payload = assert_present(source, "payload", "source envelope")
    if not isinstance(payload, dict):
        fail("source payload must be object")
    location = assert_present(payload, "location", "source payload")
    if not isinstance(location, dict):
        fail("source payload.location must be object")

    feature = assert_present(artifact, "world_state_feature", "artifact")
    if not isinstance(feature, dict):
        fail("artifact.world_state_feature must be object")

    spatial = assert_present(feature, "spatial", "world_state_feature")
    temporal = assert_present(feature, "temporal", "world_state_feature")
    evidence = assert_present(artifact, "evidence", "artifact")
    derived_confidence = assert_present(artifact, "derived_confidence", "artifact")

    source_event_id = assert_present(source, "event_id", "source envelope")
    assert_equal(artifact.get("source_event_ids"), [source_event_id], "source_event_ids")

    primary_index = assert_present(spatial, "primary_index", "world_state_feature.spatial")
    assert_equal(primary_index.get("scheme"), "h3", "primary spatial index scheme")
    assert_equal(primary_index.get("value"), location.get("h3_cell"), "H3 cell")

    if "lat" in location and "lon" in location:
        geometry = assert_present(spatial, "geometry", "world_state_feature.spatial")
        assert_equal(geometry.get("type"), "Point", "geometry type")
        assert_equal(geometry.get("coordinates"), [location.get("lon"), location.get("lat")], "geometry coordinates")

    assert_equal(temporal.get("observed_at"), source.get("observed_at"), "observed_at")
    assert_equal(temporal.get("ingested_at"), source.get("ingested_at"), "ingested_at")
    if temporal.get("observed_at") == temporal.get("ingested_at"):
        fail("observed_at and ingested_at must remain distinct when source provided both")

    for key in ["producer", "provenance", "integrity", "classification", "adversarial"]:
        if key in source:
            assert_equal(evidence.get(key), source.get(key), f"evidence.{key}")

    raw = derived_confidence.get("raw_detection_confidence_max")
    impact = derived_confidence.get("adversarial_confidence_impact")
    bridge = derived_confidence.get("bridge_confidence")
    if not isinstance(raw, (int, float)) or not isinstance(impact, (int, float)) or not isinstance(bridge, (int, float)):
        fail("derived confidence fields must be numeric")
    expected = max(0.0, min(1.0, float(raw) + float(impact)))
    if abs(float(bridge) - expected) > 1e-9:
        fail(f"bridge confidence mismatch: {bridge} != {expected}")

    print("OFIF bridge invariants passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
