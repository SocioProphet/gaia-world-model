#!/usr/bin/env python3
"""Deterministic v0 OpenStreetMap ingestion proof.

This executable reads a small OSM-like JSON fixture and emits GAIA
OSMFeatureBinding records while preserving OSM identity, attribution, routing
safety status, H3 refs, and provenance.

Usage:
  python3 geospatial/osm_ingest.py \
    fixtures/geospatial/osm-way-input.sample.v1.json \
    /tmp/osm-feature-bindings.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


REQUIRED_INPUT_FIELDS = ["input_version", "source", "extract_ref", "features", "attribution", "classification"]
REQUIRED_FEATURE_FIELDS = ["osm_type", "osm_id", "tags", "geometry", "h3_cells", "bbox", "routing"]


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


def entity_type_from_tags(tags: Dict[str, Any]) -> str:
    if "railway" in tags:
        return "RailSegment"
    if "highway" in tags:
        return "RoadSegment"
    if "building" in tags:
        return "BuildingAsset"
    if "waterway" in tags:
        return "WaterwayFeature"
    return "SpatialFeature"


def geometry_type(feature: Dict[str, Any]) -> str:
    geometry = feature.get("geometry", {})
    if isinstance(geometry, dict) and isinstance(geometry.get("type"), str):
        return geometry["type"]
    return "Other"


def build_binding(input_doc: Dict[str, Any], feature: Dict[str, Any], created_at: str) -> Dict[str, Any]:
    require_fields(feature, REQUIRED_FEATURE_FIELDS, "OSM feature")
    tags = feature.get("tags")
    if not isinstance(tags, dict):
        fail("OSM feature tags must be object")

    osm_type = str(feature["osm_type"])
    osm_id = str(feature["osm_id"])
    if osm_type not in {"node", "way", "relation"}:
        fail(f"unsupported osm_type: {osm_type}")

    entity_type = entity_type_from_tags(tags)
    entity_id = f"gaia-{entity_type.lower()}-osm-{osm_type}-{osm_id}"

    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("input attribution must be object")
    require_fields(attribution, ["source_name", "license_ref", "attribution_text"], "attribution")

    classification = input_doc["classification"]
    if not isinstance(classification, dict):
        fail("input classification must be object")

    return {
        "binding_version": "v1",
        "binding_id": f"osm-binding-demo-{osm_type}-{osm_id}",
        "source": "OpenStreetMap",
        "osm_ref": {
            "osm_type": osm_type,
            "osm_id": osm_id,
            "version": feature.get("version"),
            "timestamp": feature.get("timestamp"),
            "changeset": feature.get("changeset"),
            "tags": {str(k): str(v) for k, v in tags.items()},
        },
        "gaia_ref": {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "authority": "GAIA",
        },
        "spatial": {
            "geometry_ref": f"geometry://demo/osm/{osm_type}/{osm_id}",
            "geometry_type": geometry_type(feature),
            "h3_cells": feature.get("h3_cells", []),
            "bbox": feature.get("bbox", []),
            "crs": "EPSG:4326",
        },
        "routing": feature.get("routing", {}),
        "attribution": attribution,
        "provenance": {
            "source_refs": [f"osm://{osm_type}/{osm_id}"],
            "extract_ref": input_doc["extract_ref"],
            "runtime_refs": ["gaia-osm-ingestion-runtime@v0.1.0"],
            "content_hash": "sha256:generated-at-runtime-placeholder",
            "created_at": created_at,
        },
        "classification": classification,
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(input_doc, REQUIRED_INPUT_FIELDS, "OSM input")
    if input_doc.get("source") != "OpenStreetMap":
        fail("input source must be OpenStreetMap")
    features = input_doc.get("features")
    if not isinstance(features, list) or not features:
        fail("input features must be a non-empty array")
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    bindings = [build_binding(input_doc, feature, created_at) for feature in features]
    return {
        "artifact_version": "v1",
        "artifact_type": "gaia.osm_ingestion.output",
        "created_at": created_at,
        "source": "OpenStreetMap",
        "extract_ref": input_doc["extract_ref"],
        "bindings": bindings,
        "policy": {
            "routing_status": "advisory_by_default",
            "attribution_required": True,
            "notes": "OSM-derived outputs are advisory unless separately validated."
        },
    }


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    input_doc = load_json(source)
    output = ingest(input_doc)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
