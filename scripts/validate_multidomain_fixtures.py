#!/usr/bin/env python3
"""Validate GAIA multi-domain geospatial fixtures.

This validator intentionally mirrors the dependency-light contract checks used by
scripts/validate_contract_fixtures.py. It proves the current GAIA implementation
records are valid JSON, carry standards references, and satisfy core required
fields for the first multi-domain record families.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

CHECKS: List[Tuple[str, str, Iterable[str], str]] = [
    (
        "schemas/multidomain/space_asset_record.v1.schema.json",
        "fixtures/multidomain/space-asset.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "asset", "orbit", "operator", "source", "provenance", "governance", "classification"],
        "SpaceAssetRecord",
    ),
    (
        "schemas/multidomain/earth_observation_product_record.v1.schema.json",
        "fixtures/multidomain/earth-observation-product.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "product", "spatial", "temporal", "source", "provenance", "governance", "classification"],
        "EarthObservationProductRecord",
    ),
    (
        "schemas/multidomain/vessel_track_observation.v1.schema.json",
        "fixtures/multidomain/vessel-track-observation.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "vessel", "track", "source", "provenance", "governance", "classification"],
        "VesselTrackObservation",
    ),
]

REQUIRED_STANDARDS = [
    "SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md",
    "SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md",
]


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
        fail(f"expected top-level object in {path}")
    return value


def check_required(path: str, doc: Dict[str, Any], required: Iterable[str]) -> None:
    missing = [field for field in required if field not in doc]
    if missing:
        fail(f"{path} missing required fields: {', '.join(missing)}")


def check_standards(path: str, doc: Dict[str, Any]) -> None:
    refs = doc.get("standards_refs")
    if not isinstance(refs, list):
        fail(f"{path} standards_refs must be an array")
    for required in REQUIRED_STANDARDS:
        if required not in refs:
            fail(f"{path} missing standards ref: {required}")


def check_governance(path: str, doc: Dict[str, Any]) -> None:
    governance = doc.get("governance")
    if not isinstance(governance, dict):
        fail(f"{path} governance must be object")
    for field in ["privacy_tier", "safety_tier", "retention_tier", "redistribution"]:
        if field not in governance:
            fail(f"{path} governance missing {field}")
    classification = doc.get("classification")
    if not isinstance(classification, dict):
        fail(f"{path} classification must be object")
    if "sensitive_geo_policy_ref" not in classification:
        fail(f"{path} classification missing sensitive_geo_policy_ref")


def main() -> int:
    checked = 0
    for schema_path, fixture_path, required, record_type in CHECKS:
        schema = load_json(ROOT / schema_path)
        fixture = load_json(ROOT / fixture_path)
        schema_required = schema.get("required")
        if isinstance(schema_required, list):
            for field in required:
                if field not in schema_required:
                    fail(f"{schema_path} does not declare expected required field {field}")
        check_required(fixture_path, fixture, required)
        if fixture.get("record_type") != record_type:
            fail(f"{fixture_path} expected record_type={record_type}, got {fixture.get('record_type')!r}")
        check_standards(fixture_path, fixture)
        check_governance(fixture_path, fixture)
        if not fixture.get("provenance", {}).get("derived_from"):
            fail(f"{fixture_path} missing provenance.derived_from")
        checked += 1
    print(f"validated {checked} GAIA multi-domain geospatial fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
