#!/usr/bin/env python3
"""Deterministic v0 AIS ingestion proof for GAIA.

Reads a small AIS-like message fixture and emits a standards-bound
VesselTrackObservation with a runtime evidence bundle. This is a fixture proof,
not a live receiver.

Usage:
  python3 multidomain/ais_ingest.py \
    fixtures/multidomain/ais-message-input.sample.v1.json \
    /tmp/gaia-ais-ingest-output.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_TOP = ["input_version", "source", "feed_ref", "message", "attribution", "classification"]
REQUIRED_MESSAGE = ["mmsi", "observed_at", "lat", "lon", "course_over_ground", "speed_over_ground_knots", "navigation_status"]
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


def as_float(value: Any, scope: str) -> float:
    try:
        return float(value)
    except Exception:
        fail(f"{scope} must be numeric")


def build_runtime_evidence(input_doc: Dict[str, Any], output_record: Dict[str, Any]) -> Dict[str, Any]:
    input_hash = sha256_ref(input_doc)
    output_hash = sha256_ref(output_record)
    return {
        "evidence_version": "v1",
        "evidence_id": f"evidence:runtime:ais-ingest:{output_record['record_id']}",
        "runtime_id": "runtime:ais-ingest:v0",
        "runtime_class": "ingest",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "input_manifest": {
            "input_ref": input_doc["message"].get("message_id", f"ais:mmsi:{input_doc['message']['mmsi']}"),
            "input_sha256": input_hash,
            "input_schema_hint": "ais-like-message-fixture.v1"
        },
        "output_manifest": {
            "output_ref": output_record["record_id"],
            "output_sha256": output_hash,
            "output_schema_ref": "schemas/multidomain/vessel_track_observation.v1.schema.json"
        },
        "policy": {
            "approval_required": False,
            "sensitive_geo_handling": "preserve_policy_ref",
            "network_posture": "none_for_fixture_proof",
            "secret_posture": "none_for_fixture_proof"
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": "python3 multidomain/ais_ingest.py fixtures/multidomain/ais-message-input.sample.v1.json /tmp/gaia-ais-ingest-output.json"
        }
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(input_doc, REQUIRED_TOP, "AIS input")
    if input_doc.get("source") != "AIS":
        fail("input source must be AIS")
    message = input_doc["message"]
    if not isinstance(message, dict):
        fail("message must be object")
    require_fields(message, REQUIRED_MESSAGE, "AIS message")
    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("attribution must be object")
    require_fields(attribution, ["source_name", "license_ref", "attribution_text"], "attribution")
    classification = input_doc["classification"]
    if not isinstance(classification, dict):
        fail("classification must be object")

    lat = as_float(message["lat"], "AIS message lat")
    lon = as_float(message["lon"], "AIS message lon")
    if not (-90 <= lat <= 90):
        fail("AIS message lat out of range")
    if not (-180 <= lon <= 180):
        fail("AIS message lon out of range")

    mmsi = str(message["mmsi"])
    observed_at = str(message["observed_at"])
    imo = str(message.get("imo", "unknown"))
    record_id = f"gaia:vessel-track:sample:{mmsi}:{observed_at}"
    output_record = {
        "record_version": "v1",
        "record_type": "VesselTrackObservation",
        "record_id": record_id,
        "standards_refs": REQUIRED_STANDARDS,
        "vessel": {
            "vessel_ref": f"vessel:sample:imo-{imo}",
            "identity_refs": [f"mmsi:{mmsi}", f"imo:{imo}"],
            "vessel_type": message.get("vessel_type", "unknown"),
            "vessel_name": message.get("vessel_name", "unknown")
        },
        "track": {
            "observed_at": observed_at,
            "position": {
                "crs": "EPSG:4326",
                "lat": lat,
                "lon": lon,
                "geometry_encoding": "wgs84"
            },
            "motion": {
                "course_over_ground": as_float(message["course_over_ground"], "course_over_ground"),
                "speed_over_ground_knots": as_float(message["speed_over_ground_knots"], "speed_over_ground_knots")
            },
            "navigation_status": message["navigation_status"]
        },
        "source": {
            "source_id": input_doc["feed_ref"],
            "source_type": "AIS",
            "license_ref": attribution["license_ref"],
            "access_tier": input_doc.get("access_tier", "open"),
            "attribution": attribution["attribution_text"]
        },
        "provenance": {
            "chain": ["runtime:ais-ingest:v0"],
            "derived_from": [message.get("message_id", f"ais:mmsi:{mmsi}:{observed_at}")],
            "runtime_boundary_id": "runtime:ais-ingest:v0"
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
