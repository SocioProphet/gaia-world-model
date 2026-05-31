#!/usr/bin/env python3
"""prepare adapter – gaia.osm.normalize.v1

Normalizes bounded OSM features into GAIA feature bindings (NDJSON).
Each line of the output is a single JSON object conforming to the
gaia.osm-feature schema. Also emits a JSON bindings summary file.

Usage:
  python3 adapters/prepare.py \\
      --source fixtures/osm/demo-region.osm.json \\
      --out-ndjson build/gaia/osm/normalized-features.ndjson \\
      --out-bindings build/gaia/features/osm-feature-bindings.v1.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

ODBL_LICENSE_REF = "ODbL-1.0"
INGEST_TOOL_REF = "gaia-bounded-osm-ingest-runner@v1"

_TAG_ENTITY_RULES = [
    ("highway", "", "RoadSegment"),
    ("railway", "", "RailSegment"),
    ("waterway", "", "WaterwaySegment"),
    ("amenity", "", "SpatialFeature"),
    ("building", "", "SpatialFeature"),
    ("natural", "", "SpatialFeature"),
    ("landuse", "", "SpatialFeature"),
    ("type", "route", "SpatialFeature"),
]


def sha256_object(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"


def sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def infer_entity_type(tags: dict) -> str:
    for key, value, entity_type in _TAG_ENTITY_RULES:
        if key in tags:
            if value == "" or tags[key] == value:
                return entity_type
    return "SpatialFeature"


def normalise_binding(feature: dict, extract_ref: str, fixture_digest: str,
                      generated_at: str, attribution: dict, classification: dict) -> dict:
    osm_type = feature["osm_type"]
    osm_id = feature["osm_id"]
    tags = feature.get("tags", {})
    entity_type = infer_entity_type(tags)
    prefix = {"RoadSegment": "gaia-roadsegment", "RailSegment": "gaia-railsegment",
               "WaterwaySegment": "gaia-waterway"}.get(entity_type, "gaia-spatialfeature")

    geometry = feature.get("geometry", {})
    return {
        "binding_version": "v1",
        "binding_id": f"osm-binding-ingest-{osm_type}-{osm_id}",
        "source": "OpenStreetMap",
        "osm_ref": {
            "osm_type": osm_type,
            "osm_id": osm_id,
            "version": feature.get("version", ""),
            "timestamp": feature.get("timestamp", ""),
            "changeset": feature.get("changeset", ""),
            "tags": tags,
        },
        "gaia_ref": {
            "entity_id": f"{prefix}-osm-{osm_type}-{osm_id}",
            "entity_type": entity_type,
            "authority": "GAIA",
        },
        "spatial": {
            "geometry_ref": f"geometry://bounded/osm/{osm_type}/{osm_id}",
            "geometry_type": geometry.get("type", "Other"),
            "h3_cells": feature.get("h3_cells", []),
            "bbox": feature.get("bbox"),
            "crs": "EPSG:4326",
        },
        "attribution": {
            "source_name": attribution.get("source_name", "OpenStreetMap"),
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": attribution.get("attribution_text", "© OpenStreetMap contributors"),
            "source_url": attribution.get("source_url", "https://www.openstreetmap.org"),
        },
        "provenance": {
            "source_refs": [f"osm://{osm_type}/{osm_id}"],
            "extract_ref": extract_ref,
            "runtime_refs": [INGEST_TOOL_REF],
            "content_hash": sha256_object(feature),
            "created_at": generated_at,
            "fixture_digest": fixture_digest,
        },
        "classification": classification,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize bounded OSM features into GAIA bindings.")
    parser.add_argument("--source", required=True, help="Bounded OSM source fixture JSON.")
    parser.add_argument("--out-ndjson", required=True, help="Output NDJSON file for normalized features.")
    parser.add_argument("--out-bindings", required=True, help="Output JSON file for full bindings document.")
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = ROOT / source_path

    with source_path.open("r", encoding="utf-8") as fh:
        fixture = json.load(fh)

    fixture_digest = sha256_file(source_path)
    generated_at = args.generated_at or fixture.get("extracted_at",
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))

    extract_ref = fixture["extract_ref"]
    attribution = fixture["attribution"]
    classification = fixture["classification"]
    features = fixture["features"]

    OSM_ORDER = {"node": 0, "way": 1, "relation": 2}
    features = sorted(features, key=lambda f: (OSM_ORDER.get(f.get("osm_type", ""), 99), f.get("osm_id", "")))

    bindings = [
        normalise_binding(f, extract_ref, fixture_digest, generated_at, attribution, classification)
        for f in features
    ]

    # Write NDJSON
    ndjson_path = Path(args.out_ndjson)
    if not ndjson_path.is_absolute():
        ndjson_path = ROOT / ndjson_path
    ndjson_path.parent.mkdir(parents=True, exist_ok=True)
    with ndjson_path.open("w", encoding="utf-8") as fh:
        for b in bindings:
            fh.write(json.dumps(b, ensure_ascii=False) + "\n")

    # Write full bindings document
    region = fixture.get("region", {})
    envelope_id = (
        f"osm-source-envelope-"
        f"{region.get('region_name', 'unknown').lower().replace(' ', '-')}"
        f"-{fixture.get('extracted_at', '')[:10]}"
    )
    bindings_doc = {
        "bindings_version": "v1",
        "artifact_type": "gaia.osm_bounded_source_adapter.bindings",
        "envelope_ref": envelope_id,
        "extract_ref": extract_ref,
        "created_at": generated_at,
        "bindings": bindings,
        "attribution": {
            "source_name": attribution.get("source_name", "OpenStreetMap"),
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": attribution.get("attribution_text", "© OpenStreetMap contributors"),
            "source_url": attribution.get("source_url", "https://www.openstreetmap.org"),
        },
        "provenance": {
            "source_refs": [envelope_id, extract_ref],
            "fixture_digest": fixture_digest,
            "runtime_refs": [INGEST_TOOL_REF],
            "created_at": generated_at,
        },
        "classification": classification,
    }
    bindings_doc["provenance"]["content_hash"] = sha256_object(bindings_doc["bindings"])

    bindings_path = Path(args.out_bindings)
    if not bindings_path.is_absolute():
        bindings_path = ROOT / bindings_path
    bindings_path.parent.mkdir(parents=True, exist_ok=True)
    with bindings_path.open("w", encoding="utf-8") as fh:
        json.dump(bindings_doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"  OK  normalized {len(bindings)} features → {ndjson_path}", file=sys.stderr)
    print(f"  OK  bindings document → {bindings_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
