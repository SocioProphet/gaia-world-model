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
    (
        "schemas/multidomain/telemetry_observation.v1.schema.json",
        "fixtures/multidomain/telemetry-observation.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "asset_ref", "telemetry", "source", "provenance", "governance", "classification"],
        "TelemetryObservation",
    ),
    (
        "schemas/multidomain/air_track_observation.v1.schema.json",
        "fixtures/multidomain/air-track-observation.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "aircraft", "track", "source", "provenance", "governance", "classification"],
        "AirTrackObservation",
    ),
    (
        "schemas/multidomain/sensitive_geo_policy_record.v1.schema.json",
        "fixtures/multidomain/sensitive-geo-policy.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "policy", "scope", "controls", "source", "provenance", "governance", "classification"],
        "SensitiveGeoPolicyRecord",
    ),
    (
        "schemas/multidomain/sensor_observation_envelope.v1.schema.json",
        "fixtures/multidomain/sensor-observation-envelope.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "sensor", "observation", "source", "provenance", "governance", "classification"],
        "SensorObservationEnvelope",
    ),
    (
        "schemas/multidomain/multi_domain_fusion_event.v1.schema.json",
        "fixtures/multidomain/multi-domain-fusion-event.sample.v1.json",
        ["record_version", "record_type", "record_id", "standards_refs", "fusion", "inputs", "outputs", "source", "provenance", "governance", "classification"],
        "MultiDomainFusionEvent",
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


def check_nested_required(path: str, doc: Dict[str, Any], field: str, required: Iterable[str]) -> None:
    value = doc.get(field)
    if not isinstance(value, dict):
        fail(f"{path} {field} must be object")
    check_required(f"{path}:{field}", value, required)


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
        if record_type == "TelemetryObservation":
            check_nested_required(fixture_path, fixture, "telemetry", ["observed_at", "channel_family", "measurements", "health_state"])
            measurements = fixture["telemetry"].get("measurements")
            if not isinstance(measurements, list) or not measurements:
                fail(f"{fixture_path}: telemetry.measurements must be non-empty")
        if record_type == "AirTrackObservation":
            check_nested_required(fixture_path, fixture, "aircraft", ["aircraft_ref", "identity_refs"])
            check_nested_required(fixture_path, fixture, "track", ["observed_at", "position", "motion"])
        if record_type == "SensitiveGeoPolicyRecord":
            check_nested_required(fixture_path, fixture, "policy", ["policy_id", "policy_type", "sensitivity_tier", "default_action"])
            check_nested_required(fixture_path, fixture, "scope", ["domain_lanes", "geometry_policy"])
            check_nested_required(fixture_path, fixture, "controls", ["masking", "delay", "access_control", "audit"])
            if "SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md" not in fixture.get("standards_refs", []):
                fail(f"{fixture_path} missing agent runtime standards ref")
        if record_type == "SensorObservationEnvelope":
            check_nested_required(fixture_path, fixture, "sensor", ["sensor_ref", "sensor_type", "platform_ref"])
            check_nested_required(fixture_path, fixture, "observation", ["observed_at", "geometry_ref", "measurements"])
            measurements = fixture["observation"].get("measurements")
            if not isinstance(measurements, list) or not measurements:
                fail(f"{fixture_path}: observation.measurements must be non-empty")
        if record_type == "MultiDomainFusionEvent":
            check_nested_required(fixture_path, fixture, "fusion", ["fusion_id", "fusion_type", "created_at", "confidence"])
            if not isinstance(fixture.get("inputs"), list) or len(fixture["inputs"]) < 2:
                fail(f"{fixture_path}: inputs must include at least two source records")
            if not isinstance(fixture.get("outputs"), list) or not fixture["outputs"]:
                fail(f"{fixture_path}: outputs must be non-empty")
            if "SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md" not in fixture.get("standards_refs", []):
                fail(f"{fixture_path} missing agent runtime standards ref")
        checked += 1
    print(f"validated {checked} GAIA multi-domain geospatial fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
