#!/usr/bin/env python3
"""Deterministic v0 OSM-derived tile layer export proof.

Reads an OSMFeatureBinding JSON fixture and emits a MapTileLayerManifest that
preserves source refs, attribution, H3 refs, and MapLibre-compatible tile
metadata.

Usage:
  python3 geospatial/osm_tile_export.py \
    fixtures/geospatial/osm-road-feature-binding.sample.v1.json \
    /tmp/osm-derived-map-tile-layer.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


REQUIRED_BINDING_FIELDS = [
    "binding_version",
    "binding_id",
    "source",
    "osm_ref",
    "gaia_ref",
    "spatial",
    "attribution",
    "provenance",
    "classification",
]


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


def export_layer(binding: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(binding, REQUIRED_BINDING_FIELDS, "OSMFeatureBinding")
    if binding.get("source") != "OpenStreetMap":
        fail("binding source must be OpenStreetMap")

    osm_ref = binding.get("osm_ref", {})
    gaia_ref = binding.get("gaia_ref", {})
    spatial = binding.get("spatial", {})
    attribution = binding.get("attribution", {})
    provenance = binding.get("provenance", {})
    classification = binding.get("classification", {})

    if not isinstance(osm_ref, dict) or not isinstance(gaia_ref, dict):
        fail("osm_ref and gaia_ref must be objects")
    if not isinstance(spatial, dict) or not isinstance(attribution, dict):
        fail("spatial and attribution must be objects")
    require_fields(osm_ref, ["osm_type", "osm_id"], "osm_ref")
    require_fields(gaia_ref, ["entity_id", "entity_type"], "gaia_ref")
    require_fields(attribution, ["attribution_text", "license_ref"], "attribution")

    osm_type = str(osm_ref["osm_type"])
    osm_id = str(osm_ref["osm_id"])
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    return {
        "manifest_version": "v1",
        "layer_id": f"gaia-osm-{osm_type}-{osm_id}-layer-v1",
        "layer_type": "vector",
        "title": f"GAIA OSM {osm_type} {osm_id} Layer",
        "description": "Generated fixture MapLibre-compatible vector layer manifest for an OSM-derived GAIA feature.",
        "sources": [
            {
                "source_id": provenance.get("extract_ref", "osm-extract://unknown"),
                "source_type": "OpenStreetMap extract",
                "source_refs": provenance.get("source_refs", [f"osm://{osm_type}/{osm_id}"]),
            }
        ],
        "tiles": {
            "url_template": f"https://tiles.demo.socioprophet.org/gaia/osm/{osm_type}/{osm_id}/{{z}}/{{x}}/{{y}}.mvt",
            "min_zoom": 0,
            "max_zoom": 14,
            "format": "mvt",
        },
        "style": {
            "maplibre_layer_id": f"gaia-osm-{osm_type}-{osm_id}",
            "paint_ref": "style://gaia/osm/default-road-paint-v1",
            "layout_ref": "style://gaia/osm/default-road-layout-v1",
            "style_ref": "maplibre://gaia/osm-default-style-v1",
        },
        "spatial": {
            "bbox": spatial.get("bbox", []),
            "h3_cells": spatial.get("h3_cells", []),
            "crs": spatial.get("crs", "EPSG:4326"),
        },
        "attribution": {
            "attribution_text": attribution["attribution_text"],
            "license_refs": [attribution["license_ref"]],
            "source_urls": [attribution.get("source_url", "https://www.openstreetmap.org")],
        },
        "provenance": {
            "source_refs": [binding["binding_id"], f"osm://{osm_type}/{osm_id}", gaia_ref["entity_id"]],
            "runtime_refs": ["gaia-osm-tile-export-runtime@v0.1.0"],
            "created_at": created_at,
            "content_hash": "sha256:generated-at-runtime-placeholder",
        },
        "classification": classification,
    }


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    binding = load_json(source)
    layer = export_layer(binding)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(layer, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
