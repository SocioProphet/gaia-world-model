#!/usr/bin/env python3
"""Validate the bounded OSM source adapter fixtures.

Proves that the OSM source envelope and its normalised feature-binding set
satisfy GAIA provenance, attribution, identity, geometry, and H3-coverage
requirements. This validator is fixture/proof-shaped; it does not claim
production live ingestion.

Usage:
  python3 scripts/validate_bounded_osm_source_adapter.py

Exit codes:
  0 – all checks passed
  1 – one or more checks failed (message printed to stdout with ERROR: prefix)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]

ENVELOPE_PATH = "fixtures/geospatial/osm-source-envelope.bounded-region.sample.v1.json"
ENVELOPE_SCHEMA_PATH = "schemas/geospatial/osm_source_envelope.v1.schema.json"
BINDINGS_PATH = "fixtures/geospatial/osm-bounded-feature-bindings.sample.v1.json"

REQUIRED_ENVELOPE_FIELDS: List[str] = [
    "envelope_version",
    "envelope_id",
    "source",
    "extract_ref",
    "extracted_at",
    "region",
    "element_summary",
    "h3_coverage",
    "attribution",
    "provenance",
    "classification",
]

REQUIRED_BINDING_FIELDS: List[str] = [
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

REQUIRED_OSM_ELEMENT_TYPES: Set[str] = {"node", "way", "relation"}

ODBL_LICENSE_REF = "ODbL-1.0"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected top-level JSON object in {path}")
    return value  # type: ignore[return-value]


def check_required(doc: Dict[str, Any], required: Iterable[str], scope: str) -> None:
    missing = [f for f in required if f not in doc]
    if missing:
        fail(f"{scope} missing required fields: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# Envelope checks
# ---------------------------------------------------------------------------


def check_envelope_source_metadata(envelope: Dict[str, Any], path: str) -> None:
    if envelope.get("source") != "OpenStreetMap":
        fail(f"{path} source must be 'OpenStreetMap'")
    if not envelope.get("envelope_id"):
        fail(f"{path} envelope_id must be non-empty")
    if not envelope.get("extract_ref"):
        fail(f"{path} extract_ref must be non-empty")


def check_envelope_timestamp(envelope: Dict[str, Any], path: str) -> None:
    extracted_at = envelope.get("extracted_at")
    if not isinstance(extracted_at, str) or not extracted_at:
        fail(f"{path} extracted_at must be a non-empty ISO 8601 string")


def check_envelope_attribution(envelope: Dict[str, Any], path: str) -> None:
    attr = envelope.get("attribution")
    if not isinstance(attr, dict):
        fail(f"{path} attribution must be an object")
    if attr.get("license_ref") != ODBL_LICENSE_REF:
        fail(f"{path} attribution.license_ref must be '{ODBL_LICENSE_REF}'")
    if not attr.get("attribution_text"):
        fail(f"{path} attribution.attribution_text must be non-empty")
    if not attr.get("source_name"):
        fail(f"{path} attribution.source_name must be non-empty")


def check_envelope_region(envelope: Dict[str, Any], path: str) -> None:
    region = envelope.get("region")
    if not isinstance(region, dict):
        fail(f"{path} region must be an object")
    bbox = region.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        fail(f"{path} region.bbox must be an array of 4 numbers")
    if not all(isinstance(v, (int, float)) for v in bbox):
        fail(f"{path} region.bbox values must all be numbers")
    crs = region.get("crs")
    if not isinstance(crs, str) or not crs:
        fail(f"{path} region.crs must be a non-empty string")
    if not region.get("region_name"):
        fail(f"{path} region.region_name must be non-empty")


def check_envelope_h3_coverage(envelope: Dict[str, Any], path: str) -> None:
    h3_cells = envelope.get("h3_coverage")
    if not isinstance(h3_cells, list) or not h3_cells:
        fail(f"{path} h3_coverage must be a non-empty array")


def check_envelope_element_summary(envelope: Dict[str, Any], path: str) -> None:
    summary = envelope.get("element_summary")
    if not isinstance(summary, dict):
        fail(f"{path} element_summary must be an object")
    for field in ("node_count", "way_count", "relation_count"):
        if not isinstance(summary.get(field), int):
            fail(f"{path} element_summary.{field} must be an integer")
        if summary[field] < 0:
            fail(f"{path} element_summary.{field} must be >= 0")
    total = summary["node_count"] + summary["way_count"] + summary["relation_count"]
    if total == 0:
        fail(f"{path} element_summary total element count must be > 0")


def check_envelope_provenance(envelope: Dict[str, Any], path: str) -> None:
    prov = envelope.get("provenance")
    if not isinstance(prov, dict):
        fail(f"{path} provenance must be an object")
    if not prov.get("source_refs"):
        fail(f"{path} provenance.source_refs must be a non-empty array")
    if not prov.get("created_at"):
        fail(f"{path} provenance.created_at must be non-empty")


def validate_envelope(envelope: Dict[str, Any], path: str) -> None:
    check_required(envelope, REQUIRED_ENVELOPE_FIELDS, path)
    check_envelope_source_metadata(envelope, path)
    check_envelope_timestamp(envelope, path)
    check_envelope_attribution(envelope, path)
    check_envelope_region(envelope, path)
    check_envelope_h3_coverage(envelope, path)
    check_envelope_element_summary(envelope, path)
    check_envelope_provenance(envelope, path)


# ---------------------------------------------------------------------------
# Feature binding checks
# ---------------------------------------------------------------------------


def check_binding_osm_identity(binding: Dict[str, Any], path: str) -> Tuple[str, str]:
    osm_ref = binding.get("osm_ref")
    if not isinstance(osm_ref, dict):
        fail(f"{path} osm_ref must be an object")
    osm_type = osm_ref.get("osm_type")
    if osm_type not in {"node", "way", "relation"}:
        fail(f"{path} osm_ref.osm_type must be 'node', 'way', or 'relation'; got {osm_type!r}")
    osm_id = osm_ref.get("osm_id")
    if not isinstance(osm_id, str) or not osm_id:
        fail(f"{path} osm_ref.osm_id must be a non-empty string")
    return osm_type, osm_id


def check_binding_tags(binding: Dict[str, Any], path: str) -> None:
    osm_ref = binding.get("osm_ref", {})
    tags = osm_ref.get("tags")
    if not isinstance(tags, dict) or not tags:
        fail(f"{path} osm_ref.tags must be a non-empty object")


def check_binding_geometry(binding: Dict[str, Any], path: str) -> None:
    spatial = binding.get("spatial")
    if not isinstance(spatial, dict):
        fail(f"{path} spatial must be an object")
    if not spatial.get("geometry_ref"):
        fail(f"{path} spatial.geometry_ref must be non-empty")
    bbox = spatial.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        fail(f"{path} spatial.bbox must be an array of 4 numbers")
    crs = spatial.get("crs")
    if not isinstance(crs, str) or not crs:
        fail(f"{path} spatial.crs must be a non-empty string")


def check_binding_h3(binding: Dict[str, Any], path: str) -> None:
    spatial = binding.get("spatial", {})
    h3_cells = spatial.get("h3_cells")
    if not isinstance(h3_cells, list) or not h3_cells:
        fail(f"{path} spatial.h3_cells must be a non-empty array")


def check_binding_attribution(binding: Dict[str, Any], path: str) -> None:
    attr = binding.get("attribution")
    if not isinstance(attr, dict):
        fail(f"{path} attribution must be an object")
    if attr.get("license_ref") != ODBL_LICENSE_REF:
        fail(f"{path} attribution.license_ref must be '{ODBL_LICENSE_REF}'")
    if not attr.get("attribution_text"):
        fail(f"{path} attribution.attribution_text must be non-empty")


def check_binding_provenance(binding: Dict[str, Any], path: str) -> None:
    prov = binding.get("provenance")
    if not isinstance(prov, dict):
        fail(f"{path} provenance must be an object")
    if not prov.get("source_refs"):
        fail(f"{path} provenance.source_refs must be a non-empty array")


def validate_bindings(bindings_doc: Dict[str, Any], path: str) -> None:
    if bindings_doc.get("artifact_type") != "gaia.osm_bounded_source_adapter.bindings":
        fail(f"{path} artifact_type must be 'gaia.osm_bounded_source_adapter.bindings'")

    bindings = bindings_doc.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        fail(f"{path} bindings must be a non-empty array")

    # Check that all three OSM element types are represented
    seen_types: Set[str] = set()
    # Duplicate identity guard: (osm_type, osm_id) pairs must be unique
    seen_identities: Set[Tuple[str, str]] = set()

    for idx, binding in enumerate(bindings):
        binding_path = f"{path}:bindings[{idx}]"
        if not isinstance(binding, dict):
            fail(f"{binding_path} must be an object")
        check_required(binding, REQUIRED_BINDING_FIELDS, binding_path)
        osm_type, osm_id = check_binding_osm_identity(binding, binding_path)
        seen_types.add(osm_type)
        identity = (osm_type, osm_id)
        if identity in seen_identities:
            fail(f"{path} duplicate OSM identity ({osm_type}, {osm_id}) at index {idx}")
        seen_identities.add(identity)
        check_binding_tags(binding, binding_path)
        check_binding_geometry(binding, binding_path)
        check_binding_h3(binding, binding_path)
        check_binding_attribution(binding, binding_path)
        check_binding_provenance(binding, binding_path)

    missing_types = REQUIRED_OSM_ELEMENT_TYPES - seen_types
    if missing_types:
        fail(f"{path} bindings must include all OSM element types; missing: {', '.join(sorted(missing_types))}")

    # Validate top-level attribution and provenance of the bindings document
    top_attr = bindings_doc.get("attribution")
    if not isinstance(top_attr, dict) or top_attr.get("license_ref") != ODBL_LICENSE_REF:
        fail(f"{path} top-level attribution.license_ref must be '{ODBL_LICENSE_REF}'")
    top_prov = bindings_doc.get("provenance")
    if not isinstance(top_prov, dict) or not top_prov.get("source_refs"):
        fail(f"{path} top-level provenance.source_refs must be non-empty")


# ---------------------------------------------------------------------------
# Schema sanity cross-check
# ---------------------------------------------------------------------------


def check_envelope_schema_declares_required(schema: Dict[str, Any], expected: List[str], schema_path: str) -> None:
    declared = schema.get("required")
    if not isinstance(declared, list):
        fail(f"{schema_path} schema missing 'required' array")
    for field in expected:
        if field not in declared:
            fail(f"{schema_path} does not declare expected required field '{field}'")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    checks_passed = 0

    # 1. Validate envelope schema sanity
    envelope_schema = load_json(ROOT / ENVELOPE_SCHEMA_PATH)
    check_envelope_schema_declares_required(envelope_schema, REQUIRED_ENVELOPE_FIELDS, ENVELOPE_SCHEMA_PATH)
    print(f"  OK  {ENVELOPE_SCHEMA_PATH} declares all expected required fields")
    checks_passed += 1

    # 2. Validate bounded OSM source envelope fixture
    envelope = load_json(ROOT / ENVELOPE_PATH)
    validate_envelope(envelope, ENVELOPE_PATH)
    print(f"  OK  {ENVELOPE_PATH}")
    checks_passed += 1

    # 3. Validate bounded feature bindings fixture
    bindings_doc = load_json(ROOT / BINDINGS_PATH)
    validate_bindings(bindings_doc, BINDINGS_PATH)
    print(f"  OK  {BINDINGS_PATH}")
    checks_passed += 1

    print(f"validated {checks_passed} bounded OSM source adapter checks (envelope schema, envelope fixture, bindings fixture)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
