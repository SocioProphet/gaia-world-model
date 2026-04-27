#!/usr/bin/env python3
"""Deterministic v0 navigation LiDAR feature extraction proof.

Reads a LidarCorridorObservation fixture and emits GAIA
TransportInfrastructureAsset records for observed corridor assets. This proof
preserves source observation refs, point-cloud refs, spatial refs, confidence,
risk tags, and advisory/non-safety-critical posture.

Usage:
  python3 navigation/lidar_feature_extract.py \
    fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json \
    /tmp/lidar-derived-infrastructure-assets.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REQUIRED_OBSERVATION_FIELDS = [
    "observation_version",
    "observation_id",
    "observed_at",
    "platform",
    "sensor",
    "spatial",
    "point_cloud",
    "assets_observed",
    "provenance",
    "classification",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected object: {path}")
    return value


def require_fields(doc: dict[str, Any], fields: Iterable[str], scope: str) -> None:
    missing = [field for field in fields if field not in doc]
    if missing:
        fail(f"{scope} missing fields: {', '.join(missing)}")


def build_asset(observation: dict[str, Any], observed: dict[str, Any], created_at: str) -> dict[str, Any]:
    require_fields(observed, ["asset_type", "asset_ref", "condition_class", "confidence"], "observed asset")
    spatial = observation["spatial"]
    provenance = observation["provenance"]
    point_cloud = observation["point_cloud"]
    asset_type = str(observed["asset_type"])
    asset_ref = str(observed["asset_ref"])

    return {
        "asset_version": "v1",
        "asset_id": asset_ref,
        "asset_type": asset_type,
        "authority_ref": "GAIA",
        "name": asset_ref.replace("-", " ").title(),
        "description": "LiDAR-derived transport infrastructure asset fixture. Not safety-critical.",
        "spatial": {
            "geometry_ref": spatial.get("geometry_ref", "geometry://unknown"),
            "geometry_type": "PointCloud" if asset_type == "ClearanceEnvelope" else "Corridor",
            "h3_cells": spatial.get("h3_cells", []),
            "bbox": spatial.get("bbox", []),
            "crs": spatial.get("crs", "EPSG:4326"),
            "linear_reference": spatial.get("linear_reference", {}),
        },
        "network": {
            "mode": "rail",
            "network_id": spatial.get("corridor_ref", "unknown-corridor"),
            "route_refs": [spatial.get("linear_reference", {}).get("route_id", "unknown-route")],
        },
        "condition": {
            "condition_class": observed.get("condition_class", "unknown"),
            "confidence": observed.get("confidence", 0.0),
            "observed_at": observation["observed_at"],
            "risk_tags": observed.get("risk_tags", []),
            "evidence_refs": [observation["observation_id"], point_cloud.get("asset_uri", "point-cloud://unknown")],
        },
        "provenance": {
            "source_refs": [observation["observation_id"], point_cloud.get("asset_uri", "point-cloud://unknown")],
            "runtime_refs": ["gaia-navigation-lidar-feature-runtime@v0.1.0"],
            "model_refs": provenance.get("model_refs", []),
            "derived_from": provenance.get("source_refs", []),
            "content_hash": "sha256:generated-at-runtime-placeholder",
            "created_at": created_at,
        },
        "classification": observation.get("classification", {"data_class": "internal", "handling_tags": []}),
    }


def extract(observation: dict[str, Any]) -> dict[str, Any]:
    require_fields(observation, REQUIRED_OBSERVATION_FIELDS, "LiDAR observation")
    assets = observation.get("assets_observed")
    if not isinstance(assets, list) or not assets:
        fail("assets_observed must be a non-empty array")
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    derived_assets = [build_asset(observation, observed, created_at) for observed in assets]
    return {
        "artifact_version": "v1",
        "artifact_type": "gaia.navigation.lidar_feature_extract.output",
        "created_at": created_at,
        "source_observation_id": observation["observation_id"],
        "runtime_ref": "gaia-navigation-lidar-feature-runtime@v0.1.0",
        "safety_status": "advisory",
        "safety_note": "LiDAR-derived fixture output is not safety-critical route validation.",
        "assets": derived_assets,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    output = extract(load_json(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
