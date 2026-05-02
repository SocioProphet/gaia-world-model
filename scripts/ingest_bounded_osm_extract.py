#!/usr/bin/env python3
"""Bounded OSM extract ingestion runner.

Reads a local bounded OSM extract fixture (repo-native JSON format), normalises
OSM nodes/ways/relations into GAIA feature binding records, and emits
deterministic outputs under a caller-specified output directory.

This is bounded local-ingest shape only. It does NOT perform live network
ingestion, does NOT call Overpass or PBF URLs, and does NOT claim production
GAIA World Model v1 completion.

Usage:
  python3 scripts/ingest_bounded_osm_extract.py \\
      --fixture fixtures/geospatial/osm-extract.bounded-lower-manhattan.sample.osm.json \\
      --out examples/osm-bounded-ingest

Outputs written to <out>/:
  osm-feature-bindings.v1.json        – normalised GAIA feature binding set
  osm-source-receipt.v1.json          – source receipt (digest link to input)
  osm-layer-manifest-candidate.v1.json – layer manifest candidate

Exit codes:
  0 – success
  1 – validation or I/O failure (ERROR: prefix on stdout)

Route-graph output is an explicit non-goal for this runner. A future task
should wire the bounded-ingest bindings into the existing route graph schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]

ODBL_LICENSE_REF = "ODbL-1.0"
INGEST_TOOL_REF = "gaia-bounded-osm-ingest-runner@v1"

OSM_TYPE_ORDER = {"node": 0, "way": 1, "relation": 2}

# Map OSM tag keys to GAIA entity types (first matching rule wins).
_TAG_ENTITY_RULES: List[Tuple[str, str, str]] = [
    ("highway", "", "RoadSegment"),
    ("railway", "", "RailSegment"),
    ("waterway", "", "WaterwaySegment"),
    ("amenity", "", "SpatialFeature"),
    ("building", "", "SpatialFeature"),
    ("natural", "", "SpatialFeature"),
    ("landuse", "", "SpatialFeature"),
    ("type", "route", "SpatialFeature"),
]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected top-level JSON object in {path}")
    return value  # type: ignore[return-value]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def sha256_file(path: Path) -> str:
    """Return hex digest string for file at *path*, prefixed with 'sha256:'."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def sha256_object(data: Any) -> str:
    """Return deterministic SHA-256 of a JSON-serialisable object."""
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def infer_entity_type(tags: Dict[str, str]) -> str:
    for key, value, entity_type in _TAG_ENTITY_RULES:
        if key in tags:
            if value == "" or tags[key] == value:
                return entity_type
    return "SpatialFeature"


def sort_key(feature: Dict[str, Any]) -> Tuple[int, str]:
    return (
        OSM_TYPE_ORDER.get(feature.get("osm_type", ""), 99),
        feature.get("osm_id", ""),
    )


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_input_fixture(fixture: Dict[str, Any], path: str) -> None:
    required = [
        "input_version",
        "source",
        "extract_ref",
        "extracted_at",
        "region",
        "features",
        "attribution",
        "classification",
    ]
    missing = [f for f in required if f not in fixture]
    if missing:
        fail(f"{path} missing required fields: {', '.join(missing)}")
    if fixture.get("source") != "OpenStreetMap":
        fail(f"{path} source must be 'OpenStreetMap'")
    features = fixture.get("features")
    if not isinstance(features, list) or not features:
        fail(f"{path} features must be a non-empty array")
    region = fixture.get("region", {})
    bbox = region.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        fail(f"{path} region.bbox must be an array of 4 numbers")
    attr = fixture.get("attribution", {})
    if attr.get("license_ref") != ODBL_LICENSE_REF:
        fail(f"{path} attribution.license_ref must be '{ODBL_LICENSE_REF}'")
    if not attr.get("attribution_text"):
        fail(f"{path} attribution.attribution_text must be non-empty")


def validate_feature(feature: Dict[str, Any], idx: int, path: str) -> None:
    osm_type = feature.get("osm_type")
    if osm_type not in {"node", "way", "relation"}:
        fail(f"{path}:features[{idx}] osm_type must be 'node', 'way', or 'relation'; got {osm_type!r}")
    if not feature.get("osm_id"):
        fail(f"{path}:features[{idx}] osm_id must be non-empty")
    bbox = feature.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        fail(f"{path}:features[{idx}] bbox must be an array of 4 numbers")
    h3_cells = feature.get("h3_cells")
    if not isinstance(h3_cells, list) or not h3_cells:
        fail(f"{path}:features[{idx}] h3_cells must be a non-empty array")
    tags = feature.get("tags")
    if not isinstance(tags, dict) or not tags:
        fail(f"{path}:features[{idx}] tags must be a non-empty object")


def validate_no_duplicate_identities(features: List[Dict[str, Any]], path: str) -> None:
    seen: Set[Tuple[str, str]] = set()
    for idx, feature in enumerate(features):
        identity = (feature.get("osm_type", ""), feature.get("osm_id", ""))
        if identity in seen:
            fail(f"{path}:features duplicate OSM identity {identity} at index {idx}")
        seen.add(identity)


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------


def normalise_binding(
    feature: Dict[str, Any],
    extract_ref: str,
    fixture_digest: str,
    generated_at: str,
    attribution: Dict[str, Any],
    classification: Dict[str, Any],
) -> Dict[str, Any]:
    osm_type = feature["osm_type"]
    osm_id = feature["osm_id"]
    tags = feature.get("tags", {})
    entity_type = infer_entity_type(tags)
    entity_id_prefix = {
        "RoadSegment": "gaia-roadsegment",
        "RailSegment": "gaia-railsegment",
        "WaterwaySegment": "gaia-waterway",
    }.get(entity_type, "gaia-spatialfeature")

    binding_id = f"osm-binding-ingest-{osm_type}-{osm_id}"
    entity_id = f"{entity_id_prefix}-osm-{osm_type}-{osm_id}"
    geometry_ref = f"geometry://bounded/osm/{osm_type}/{osm_id}"

    geometry = feature.get("geometry", {})
    geometry_type = geometry.get("type", "Other")

    binding: Dict[str, Any] = {
        "binding_version": "v1",
        "binding_id": binding_id,
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
            "entity_id": entity_id,
            "entity_type": entity_type,
            "authority": "GAIA",
        },
        "spatial": {
            "geometry_ref": geometry_ref,
            "geometry_type": geometry_type,
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
        },
        "classification": classification,
    }

    # Preserve fixture_digest as a link to the input
    binding["provenance"]["fixture_digest"] = fixture_digest

    return binding


def build_feature_bindings(
    features: List[Dict[str, Any]],
    fixture: Dict[str, Any],
    fixture_digest: str,
    generated_at: str,
    envelope_id: str,
) -> Dict[str, Any]:
    extract_ref = fixture["extract_ref"]
    attribution = fixture["attribution"]
    classification = fixture["classification"]

    bindings = [
        normalise_binding(
            feature=f,
            extract_ref=extract_ref,
            fixture_digest=fixture_digest,
            generated_at=generated_at,
            attribution=attribution,
            classification=classification,
        )
        for f in sorted(features, key=sort_key)
    ]

    doc: Dict[str, Any] = {
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
    doc["provenance"]["content_hash"] = sha256_object(doc["bindings"])
    return doc


def build_source_receipt(
    fixture_path: str,
    fixture_digest: str,
    fixture: Dict[str, Any],
    generated_at: str,
    envelope_id: str,
    bindings_filename: str,
    layer_manifest_filename: str,
) -> Dict[str, Any]:
    region = fixture.get("region", {})
    features = fixture.get("features", [])
    node_count = sum(1 for f in features if f.get("osm_type") == "node")
    way_count = sum(1 for f in features if f.get("osm_type") == "way")
    relation_count = sum(1 for f in features if f.get("osm_type") == "relation")
    attribution = fixture["attribution"]

    receipt: Dict[str, Any] = {
        "receipt_version": "v1",
        "receipt_id": envelope_id.replace("osm-source-envelope", "osm-source-receipt"),
        "artifact_type": "gaia.osm_bounded_ingest.source_receipt",
        "fixture_path": fixture_path,
        "fixture_digest": fixture_digest,
        "extract_ref": fixture["extract_ref"],
        "extracted_at": fixture["extracted_at"],
        "generated_at": generated_at,
        "region": region,
        "element_summary": {
            "node_count": node_count,
            "way_count": way_count,
            "relation_count": relation_count,
            "total_count": node_count + way_count + relation_count,
        },
        "output_refs": [bindings_filename, layer_manifest_filename],
        "route_graph_status": "non-goal: route graph generation is deferred to a future task",
        "attribution": {
            "source_name": attribution.get("source_name", "OpenStreetMap"),
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": attribution.get("attribution_text", "© OpenStreetMap contributors"),
            "source_url": attribution.get("source_url", "https://www.openstreetmap.org"),
        },
        "classification": fixture["classification"],
    }
    return receipt


def build_layer_manifest(
    fixture: Dict[str, Any],
    fixture_digest: str,
    generated_at: str,
    envelope_id: str,
    receipt_filename: str,
    bindings_filename: str,
) -> Dict[str, Any]:
    region = fixture.get("region", {})
    bbox = region.get("bbox", [])
    extract_ref = fixture["extract_ref"]
    attribution = fixture["attribution"]

    h3_cells: Set[str] = set()
    for feature in fixture.get("features", []):
        h3_cells.update(feature.get("h3_cells", []))

    layer_id = envelope_id.replace("osm-source-envelope", "osm-layer-manifest-candidate")

    manifest: Dict[str, Any] = {
        "manifest_version": "v1",
        "layer_id": layer_id,
        "layer_type": "vector",
        "title": f"GAIA OSM Bounded Ingest Layer – {region.get('region_name', 'Unknown Region')}",
        "description": (
            "Bounded OSM ingest layer manifest candidate. "
            "Generated by ingest_bounded_osm_extract.py. "
            "Not production tile-serving. Advisory only."
        ),
        "sources": [
            {
                "source_id": envelope_id,
                "source_type": "OpenStreetMap extract",
                "source_refs": [extract_ref, receipt_filename, bindings_filename],
            }
        ],
        "tiles": {
            "url_template": "placeholder://tiles/gaia/osm-bounded/{z}/{x}/{y}.mvt",
            "min_zoom": 0,
            "max_zoom": 14,
            "format": "mvt",
        },
        "spatial": {
            "bbox": bbox,
            "h3_cells": sorted(h3_cells),
            "crs": "EPSG:4326",
        },
        "attribution": {
            "attribution_text": attribution.get("attribution_text", "© OpenStreetMap contributors"),
            "license_refs": [ODBL_LICENSE_REF],
            "source_urls": [attribution.get("source_url", "https://www.openstreetmap.org")],
        },
        "provenance": {
            "source_refs": [receipt_filename, bindings_filename, extract_ref],
            "fixture_digest": fixture_digest,
            "runtime_refs": [INGEST_TOOL_REF],
            "created_at": generated_at,
        },
        "classification": fixture["classification"],
    }
    manifest["provenance"]["content_hash"] = sha256_object(manifest["spatial"])
    return manifest


# ---------------------------------------------------------------------------
# Output validation
# ---------------------------------------------------------------------------


def validate_bindings_output(doc: Dict[str, Any], path: str) -> None:
    if doc.get("artifact_type") != "gaia.osm_bounded_source_adapter.bindings":
        fail(f"{path} artifact_type must be 'gaia.osm_bounded_source_adapter.bindings'")
    bindings = doc.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        fail(f"{path} bindings must be a non-empty array")
    seen_types: Set[str] = set()
    seen_identities: Set[Tuple[str, str]] = set()
    for idx, b in enumerate(bindings):
        bp = f"{path}:bindings[{idx}]"
        for field in ("binding_version", "binding_id", "source", "osm_ref", "gaia_ref", "spatial", "attribution", "provenance", "classification"):
            if field not in b:
                fail(f"{bp} missing required field '{field}'")
        osm_ref = b.get("osm_ref", {})
        osm_type = osm_ref.get("osm_type")
        osm_id = osm_ref.get("osm_id")
        if osm_type not in {"node", "way", "relation"}:
            fail(f"{bp} invalid osm_type {osm_type!r}")
        seen_types.add(osm_type)
        identity = (osm_type, osm_id)
        if identity in seen_identities:
            fail(f"{path} duplicate OSM identity {identity} at index {idx}")
        seen_identities.add(identity)
        spatial = b.get("spatial", {})
        if not spatial.get("geometry_ref"):
            fail(f"{bp} spatial.geometry_ref must be non-empty")
        if not isinstance(spatial.get("bbox"), list) or len(spatial["bbox"]) != 4:
            fail(f"{bp} spatial.bbox must be a 4-element array")
        if not isinstance(spatial.get("h3_cells"), list) or not spatial["h3_cells"]:
            fail(f"{bp} spatial.h3_cells must be non-empty")
        attr = b.get("attribution", {})
        if attr.get("license_ref") != ODBL_LICENSE_REF:
            fail(f"{bp} attribution.license_ref must be '{ODBL_LICENSE_REF}'")
        prov = b.get("provenance", {})
        if not prov.get("source_refs"):
            fail(f"{bp} provenance.source_refs must be non-empty")
        if not prov.get("fixture_digest"):
            fail(f"{bp} provenance.fixture_digest must link to input fixture digest")
    missing_types = {"node", "way", "relation"} - seen_types
    if missing_types:
        fail(f"{path} bindings missing OSM element types: {', '.join(sorted(missing_types))}")
    top_attr = doc.get("attribution", {})
    if top_attr.get("license_ref") != ODBL_LICENSE_REF:
        fail(f"{path} top-level attribution.license_ref must be '{ODBL_LICENSE_REF}'")
    top_prov = doc.get("provenance", {})
    if not top_prov.get("source_refs"):
        fail(f"{path} top-level provenance.source_refs must be non-empty")
    if not top_prov.get("fixture_digest"):
        fail(f"{path} top-level provenance.fixture_digest must be present")


def validate_source_receipt_output(doc: Dict[str, Any], path: str, expected_digest: str) -> None:
    for field in ("receipt_version", "receipt_id", "artifact_type", "fixture_path", "fixture_digest", "extract_ref", "extracted_at", "generated_at", "element_summary", "output_refs", "attribution", "classification"):
        if field not in doc:
            fail(f"{path} missing required field '{field}'")
    if doc.get("fixture_digest") != expected_digest:
        fail(f"{path} fixture_digest mismatch: expected {expected_digest!r}")
    attr = doc.get("attribution", {})
    if attr.get("license_ref") != ODBL_LICENSE_REF:
        fail(f"{path} attribution.license_ref must be '{ODBL_LICENSE_REF}'")
    summary = doc.get("element_summary", {})
    for count_field in ("node_count", "way_count", "relation_count", "total_count"):
        if not isinstance(summary.get(count_field), int):
            fail(f"{path} element_summary.{count_field} must be an integer")


def validate_layer_manifest_output(doc: Dict[str, Any], path: str) -> None:
    for field in ("manifest_version", "layer_id", "layer_type", "title", "sources", "tiles", "spatial", "attribution", "provenance", "classification"):
        if field not in doc:
            fail(f"{path} missing required field '{field}'")
    spatial = doc.get("spatial", {})
    if not isinstance(spatial.get("bbox"), list) or len(spatial["bbox"]) != 4:
        fail(f"{path} spatial.bbox must be a 4-element array")
    if not isinstance(spatial.get("h3_cells"), list) or not spatial["h3_cells"]:
        fail(f"{path} spatial.h3_cells must be non-empty")
    attr = doc.get("attribution", {})
    if not attr.get("attribution_text"):
        fail(f"{path} attribution.attribution_text must be non-empty")
    if ODBL_LICENSE_REF not in attr.get("license_refs", []):
        fail(f"{path} attribution.license_refs must include '{ODBL_LICENSE_REF}'")
    prov = doc.get("provenance", {})
    if not prov.get("source_refs"):
        fail(f"{path} provenance.source_refs must be non-empty")
    if not prov.get("fixture_digest"):
        fail(f"{path} provenance.fixture_digest must be present")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bounded OSM extract ingestion runner (local fixture only, no network)."
    )
    parser.add_argument(
        "--fixture",
        required=True,
        help="Path to the bounded OSM extract fixture (.osm.json). "
             "Relative paths are resolved from the repository root.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for generated artifacts. Created if absent.",
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help="Override generated_at timestamp (ISO 8601). "
             "Uses extracted_at from fixture if not provided. "
             "Pass an explicit value for fully deterministic CI runs.",
    )
    args = parser.parse_args(argv)

    fixture_path = Path(args.fixture)
    if not fixture_path.is_absolute():
        fixture_path = ROOT / fixture_path
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    # 1. Load and validate input fixture
    fixture = load_json(fixture_path)
    validate_input_fixture(fixture, str(fixture_path))
    features: List[Dict[str, Any]] = fixture["features"]
    for idx, feature in enumerate(features):
        validate_feature(feature, idx, str(fixture_path))
    validate_no_duplicate_identities(features, str(fixture_path))
    print(f"  OK  input fixture validated: {fixture_path}")

    # 2. Compute input fixture digest (deterministic from bytes on disk)
    fixture_digest = sha256_file(fixture_path)
    print(f"  OK  fixture digest: {fixture_digest}")

    # 3. Determine stable generated_at timestamp
    generated_at: str = args.generated_at or fixture["extracted_at"]

    # 4. Build stable envelope ID
    envelope_id = (
        f"osm-source-envelope-"
        f"{fixture['region']['region_name'].lower().replace(' ', '-')}"
        f"-{fixture['extracted_at'][:10]}"
    )

    # 5. Define output filenames
    bindings_filename = "osm-feature-bindings.v1.json"
    receipt_filename = "osm-source-receipt.v1.json"
    layer_manifest_filename = "osm-layer-manifest-candidate.v1.json"

    # 6. Build outputs
    bindings_doc = build_feature_bindings(
        features=features,
        fixture=fixture,
        fixture_digest=fixture_digest,
        generated_at=generated_at,
        envelope_id=envelope_id,
    )
    receipt_doc = build_source_receipt(
        fixture_path=str(fixture_path.relative_to(ROOT)),
        fixture_digest=fixture_digest,
        fixture=fixture,
        generated_at=generated_at,
        envelope_id=envelope_id,
        bindings_filename=bindings_filename,
        layer_manifest_filename=layer_manifest_filename,
    )
    layer_manifest_doc = build_layer_manifest(
        fixture=fixture,
        fixture_digest=fixture_digest,
        generated_at=generated_at,
        envelope_id=envelope_id,
        receipt_filename=receipt_filename,
        bindings_filename=bindings_filename,
    )

    # 7. Validate outputs
    validate_bindings_output(bindings_doc, bindings_filename)
    print(f"  OK  bindings output validated")
    validate_source_receipt_output(receipt_doc, receipt_filename, fixture_digest)
    print(f"  OK  source receipt validated")
    validate_layer_manifest_output(layer_manifest_doc, layer_manifest_filename)
    print(f"  OK  layer manifest validated")

    # 8. Write outputs
    write_json(out_dir / bindings_filename, bindings_doc)
    write_json(out_dir / receipt_filename, receipt_doc)
    write_json(out_dir / layer_manifest_filename, layer_manifest_doc)

    print(f"  OK  outputs written to {out_dir}/")
    print(f"       {bindings_filename}")
    print(f"       {receipt_filename}")
    print(f"       {layer_manifest_filename}")
    print(f"  NOTE route-graph output: non-goal – deferred to a future task")
    print(f"ingest complete: {len(features)} OSM features → {out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
