#!/usr/bin/env python3
"""Deterministic v0 ADS-B ingestion proof for GAIA.

Reads a small ADS-B-like message fixture and emits a standards-bound
AirTrackObservation with a runtime evidence bundle. This is a fixture proof,
not a live receiver.

Usage:
  python3 multidomain/adsb_ingest.py \
    fixtures/multidomain/adsb-message-input.sample.v1.json \
    /tmp/gaia-adsb-ingest-output.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_TOP = ["input_version", "source", "feed_ref", "message", "attribution", "classification"]
REQUIRED_MESSAGE = ["icao24", "observed_at", "lat", "lon", "altitude_ft", "track_degrees", "ground_speed_knots", "vertical_rate_fpm", "flight_status"]
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
        "evidence_id": f"evidence:runtime:adsb-ingest:{output_record['record_id']}",
        "runtime_id": "runtime:adsb-ingest:v0",
        "runtime_class": "ingest",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "input_manifest": {
            "input_ref": input_doc["message"].get("message_id", f"adsb:icao24:{input_doc['message']['icao24']}"),
            "input_sha256": input_hash,
            "input_schema_hint": "adsb-like-message-fixture.v1"
        },
        "output_manifest": {
            "output_ref": output_record["record_id"],
            "output_sha256": output_hash,
            "output_schema_ref": "schemas/multidomain/air_track_observation.v1.schema.json"
        },
        "policy": {
            "approval_required": False,
            "sensitive_geo_handling": "preserve_policy_ref",
            "network_posture": "none_for_fixture_proof",
            "secret_posture": "none_for_fixture_proof"
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": "python3 multidomain/adsb_ingest.py fixtures/multidomain/adsb-message-input.sample.v1.json /tmp/gaia-adsb-ingest-output.json"
        }
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(input_doc, REQUIRED_TOP, "ADS-B input")
    if input_doc.get("source") != "ADS-B":
        fail("input source must be ADS-B")
    message = input_doc["message"]
    if not isinstance(message, dict):
        fail("message must be object")
    require_fields(message, REQUIRED_MESSAGE, "ADS-B message")
    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("attribution must be object")
    require_fields(attribution, ["source_name", "license_ref", "attribution_text"], "attribution")
    classification = input_doc["classification"]
    if not isinstance(classification, dict):
        fail("classification must be object")

    lat = as_float(message["lat"], "ADS-B message lat")
    lon = as_float(message["lon"], "ADS-B message lon")
    altitude_ft = as_float(message["altitude_ft"], "ADS-B message altitude_ft")
    if not (-90 <= lat <= 90):
        fail("ADS-B message lat out of range")
    if not (-180 <= lon <= 180):
        fail("ADS-B message lon out of range")
    if not (-2000 <= altitude_ft <= 100000):
        fail("ADS-B message altitude_ft out of expected range")

    icao24 = str(message["icao24"])
    observed_at = str(message["observed_at"])
    callsign = str(message.get("callsign", "unknown"))
    record_id = f"gaia:air-track:sample:{icao24}:{observed_at}"
    output_record = {
        "record_version": "v1",
        "record_type": "AirTrackObservation",
        "record_id": record_id,
        "standards_refs": REQUIRED_STANDARDS,
        "aircraft": {
            "aircraft_ref": f"aircraft:sample:{icao24.lower()}",
            "identity_refs": [f"icao24:{icao24}", f"callsign:{callsign}"],
            "aircraft_type": message.get("aircraft_type", "unknown")
        },
        "track": {
            "observed_at": observed_at,
            "position": {
                "crs": "EPSG:4326",
                "lat": lat,
                "lon": lon,
                "altitude_ft": altitude_ft,
                "geometry_encoding": "wgs84"
            },
            "motion": {
                "track_degrees": as_float(message["track_degrees"], "track_degrees"),
                "ground_speed_knots": as_float(message["ground_speed_knots"], "ground_speed_knots"),
                "vertical_rate_fpm": as_float(message["vertical_rate_fpm"], "vertical_rate_fpm")
            },
            "flight_status": message["flight_status"]
        },
        "source": {
            "source_id": input_doc["feed_ref"],
            "source_type": "ADS-B",
            "license_ref": attribution["license_ref"],
            "access_tier": input_doc.get("access_tier", "open"),
            "attribution": attribution["attribution_text"]
        },
        "provenance": {
            "chain": ["runtime:adsb-ingest:v0"],
            "derived_from": [message.get("message_id", f"adsb:icao24:{icao24}:{observed_at}")],
            "runtime_boundary_id": "runtime:adsb-ingest:v0"
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
