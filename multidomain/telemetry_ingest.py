#!/usr/bin/env python3
"""Deterministic v0 space telemetry ingestion proof for GAIA.

Reads a small telemetry packet fixture and emits a standards-bound
TelemetryObservation with a runtime evidence bundle. This is a fixture proof,
not a live telemetry receiver or command path.

Usage:
  python3 multidomain/telemetry_ingest.py \
    fixtures/multidomain/telemetry-packet-input.sample.v1.json \
    /tmp/gaia-telemetry-ingest-output.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_TOP = ["input_version", "source", "stream_ref", "asset_ref", "packet", "attribution", "classification"]
REQUIRED_PACKET = ["packet_id", "observed_at", "channel_family", "health_state", "measurements"]
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


def validate_measurements(measurements: Any) -> None:
    if not isinstance(measurements, list) or not measurements:
        fail("packet.measurements must be a non-empty array")
    for idx, measurement in enumerate(measurements):
        if not isinstance(measurement, dict):
            fail(f"packet.measurements[{idx}] must be object")
        require_fields(measurement, ["name", "value", "unit", "quality"], f"packet.measurements[{idx}]")
        if not isinstance(measurement["name"], str) or not measurement["name"]:
            fail(f"packet.measurements[{idx}].name must be non-empty string")
        try:
            float(measurement["value"])
        except Exception:
            fail(f"packet.measurements[{idx}].value must be numeric")


def build_runtime_evidence(input_doc: Dict[str, Any], output_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "evidence_version": "v1",
        "evidence_id": f"evidence:runtime:telemetry-ingest:{output_record['record_id']}",
        "runtime_id": "runtime:telemetry-ingest:v0",
        "runtime_class": "ingest",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "input_manifest": {
            "input_ref": input_doc["packet"].get("packet_id", "telemetry-packet:unknown"),
            "input_sha256": sha256_ref(input_doc),
            "input_schema_hint": "space-telemetry-packet-fixture.v1"
        },
        "output_manifest": {
            "output_ref": output_record["record_id"],
            "output_sha256": sha256_ref(output_record),
            "output_schema_ref": "schemas/multidomain/telemetry_observation.v1.schema.json"
        },
        "policy": {
            "approval_required": False,
            "sensitive_geo_handling": "preserve_policy_ref",
            "network_posture": "none_for_fixture_proof",
            "secret_posture": "none_for_fixture_proof"
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": "python3 multidomain/telemetry_ingest.py fixtures/multidomain/telemetry-packet-input.sample.v1.json /tmp/gaia-telemetry-ingest-output.json"
        }
    }


def ingest(input_doc: Dict[str, Any]) -> Dict[str, Any]:
    require_fields(input_doc, REQUIRED_TOP, "Telemetry input")
    if input_doc.get("source") != "SpaceTelemetry":
        fail("input source must be SpaceTelemetry")
    packet = input_doc["packet"]
    if not isinstance(packet, dict):
        fail("packet must be object")
    require_fields(packet, REQUIRED_PACKET, "packet")
    validate_measurements(packet["measurements"])
    attribution = input_doc["attribution"]
    if not isinstance(attribution, dict):
        fail("attribution must be object")
    require_fields(attribution, ["source_name", "license_ref", "attribution_text"], "attribution")
    classification = input_doc["classification"]
    if not isinstance(classification, dict):
        fail("classification must be object")

    asset_ref = str(input_doc["asset_ref"])
    observed_at = str(packet["observed_at"])
    output_record = {
        "record_version": "v1",
        "record_type": "TelemetryObservation",
        "record_id": f"gaia:telemetry:{asset_ref.split(':')[-1]}:{observed_at}",
        "standards_refs": REQUIRED_STANDARDS,
        "asset_ref": asset_ref,
        "telemetry": {
            "observed_at": observed_at,
            "channel_family": packet["channel_family"],
            "health_state": packet["health_state"],
            "link_session_ref": packet.get("link_session_ref"),
            "ground_station_ref": packet.get("ground_station_ref"),
            "measurements": packet["measurements"],
        },
        "source": {
            "source_id": input_doc["stream_ref"],
            "source_type": "synthetic_space_telemetry",
            "license_ref": attribution["license_ref"],
            "access_tier": input_doc.get("access_tier", "open"),
            "attribution": attribution["attribution_text"],
        },
        "provenance": {
            "chain": ["runtime:telemetry-ingest:v0"],
            "derived_from": [packet["packet_id"]],
            "runtime_boundary_id": "runtime:telemetry-ingest:v0",
        },
        "governance": {
            "privacy_tier": input_doc.get("privacy_tier", "public"),
            "safety_tier": input_doc.get("safety_tier", "standard"),
            "retention_tier": input_doc.get("retention_tier", "sample"),
            "redistribution": input_doc.get("redistribution", "allowed"),
        },
        "classification": classification,
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
