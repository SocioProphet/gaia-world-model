#!/usr/bin/env python3
"""Deterministic v0 SensorThings ingestion proof for GAIA.

Reads a small SensorThings-like observation fixture and emits a standards-bound
SensorObservationEnvelope with a runtime evidence bundle. This is a fixture
proof, not a live SensorThings client.

Usage:
  python3 multidomain/sensorthings_ingest.py \
    fixtures/multidomain/sensorthings-observation-input.sample.v1.json \
    /tmp/gaia-sensorthings-ingest-output.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_TOP = ["input_version", "source", "feed_ref", "sensor", "observation", "attribution", "classification"]
REQUIRED_SENSOR = ["sensor_ref", "sensor_type", "platform_ref"]
REQUIRED_OBSERVATION = ["observation_id", "observed_at", "geometry_ref", "measurements"]
REQUIRED_STANDARDS = [
    "SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md",
    "SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md",
]
AGENT_STANDARD_REF = "SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def canonical_bytes(value: Dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_ref(value: Dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


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


def validate_geometry(geometry: Dict[str, Any]) -> None:
    require_fields(geometry, ["crs", "lat", "lon", "encoding"], "geometry_ref")
    lat = float(geometry["lat"])
    lon = float(geometry["lon"])
    if not (-90 <= lat <= 90):
        fail("geometry_ref.lat out of range")
    if not (-180 <= lon <= 180):
        fail("geometry_ref.lon out of range")


def build_runtime_evidence(input_doc: Dict[str, Any], output_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "evidence_version": "v1",
        "evidence_id": f"evidence:runtime:sensorthings-ingest:{output_record['record_id']}",
        "runtime_id": "runtime:sensorthings-ingest:v0",
        "runtime_class": "ingest",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "input_manifest": {
            "input_ref": input_doc["observation"].get("observation_id", "sensorthings:observation:unknown"),
            "input_sha256": sha256_ref(input_doc),
            "input_schema_hint": "sensorthings-like-observation-fixture.v1"
        },
        "output_manifest": {
            "output_ref": output_record["record_id"],
            "output_sha256": sha256_ref(output_record),
            "output_schema_ref": "schemas/multidomain/sensor_observation_envelope.v1.schema.json"
        },
        "policy": {
            "approval_required": False,
            "sensitive_geo_handling": "preserve_policy_ref",
            "network_posture": "none_for_fixture_proof",
            "secret_posture": "none_for_fixture_proof"
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": "python3 multidomain/sensorthings_ingest.py fixtures/multidomain/sensorthings-observation-input.sample.v1.json /tmp/gaia-sensorthings-ingest-output.json"
        }
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(input_doc, REQUIRED_TOP, "SensorThings input")
    if input_doc.get("source") != "SensorThings":
        fail("input source must be SensorThings")
    sensor = input_doc["sensor"]
    if not isinstance(sensor, dict):
        fail("sensor must be object")
    require_fields(sensor, REQUIRED_SENSOR, "sensor")
    observation = input_doc["observation"]
    if not isinstance(observation, dict):
        fail("observation must be object")
    require_fields(observation, REQUIRED_OBSERVATION, "observation")
    geometry = observation["geometry_ref"]
    if not isinstance(geometry, dict):
        fail("observation.geometry_ref must be object")
    validate_geometry(geometry)
    measurements = observation["measurements"]
    if not isinstance(measurements, list) or not measurements:
        fail("observation.measurements must be non-empty array")
    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("attribution must be object")
    require_fields(attribution, ["source_name", "license_ref", "attribution_text"], "attribution")
    classification = input_doc["classification"]
    if not isinstance(classification, dict):
        fail("classification must be object")

    observation_id = str(observation["observation_id"])
    output_record = {
        "record_version": "v1",
        "record_type": "SensorObservationEnvelope",
        "record_id": f"gaia:sensor-observation:{sensor['sensor_ref'].split(':')[-1]}:{observation['observed_at']}",
        "standards_refs": REQUIRED_STANDARDS,
        "sensor": {
            "sensor_ref": sensor["sensor_ref"],
            "sensor_type": sensor["sensor_type"],
            "platform_ref": sensor["platform_ref"],
            "observed_property_refs": sensor.get("observed_property_refs", [])
        },
        "observation": {
            "observed_at": observation["observed_at"],
            "geometry_ref": geometry,
            "measurements": measurements,
            "quality": observation.get("quality", "unknown")
        },
        "source": {
            "source_id": input_doc["feed_ref"],
            "source_type": "SensorThings",
            "license_ref": attribution["license_ref"],
            "access_tier": input_doc.get("access_tier", "open"),
            "attribution": attribution["attribution_text"]
        },
        "provenance": {
            "chain": ["runtime:sensorthings-ingest:v0"],
            "derived_from": [observation_id],
            "runtime_boundary_id": "runtime:sensorthings-ingest:v0"
        },
        "governance": {
            "privacy_tier": input_doc.get("privacy_tier", "public"),
            "safety_tier": input_doc.get("safety_tier", "standard"),
            "retention_tier": input_doc.get("retention_tier", "sample"),
            "redistribution": input_doc.get("redistribution", "allowed")
        },
        "classification": classification
    }
    output_record["runtime_evidence"] = build_runtime_evidence(input_doc, output_record)
    return output_record


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    output = ingest(load_json(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
