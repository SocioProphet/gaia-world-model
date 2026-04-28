#!/usr/bin/env python3
"""Deterministic v0 sensitive-geospatial policy evaluation proof for GAIA.

Reads a SensitiveGeoPolicyRecord fixture and a target GAIA multidomain record,
then emits an advisory policy evaluation artifact with runtime evidence.

This runtime evaluates governance posture only. It does not unmask locations,
restore precision, task operations, or authorize effects.

Usage:
  python3 multidomain/sensitive_geo_policy_eval.py \
    fixtures/multidomain/sensitive-geo-policy.sample.v1.json \
    fixtures/multidomain/multi-domain-fusion-event.sample.v1.json \
    /tmp/gaia-sensitive-geo-policy-eval-output.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

REQUIRED_POLICY_TOP = ["record_version", "record_type", "record_id", "standards_refs", "policy", "scope", "controls", "source", "provenance", "governance", "classification"]
REQUIRED_POLICY = ["policy_id", "policy_type", "sensitivity_tier", "default_action"]
REQUIRED_SCOPE = ["domain_lanes", "geometry_policy"]
REQUIRED_CONTROLS = ["masking", "delay", "access_control", "audit"]
REQUIRED_SUBJECT_TOP = ["record_version", "record_type", "record_id", "standards_refs", "provenance", "governance", "classification"]
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


def validate_policy(policy_doc: Dict[str, Any]) -> None:
    require_fields(policy_doc, REQUIRED_POLICY_TOP, "SensitiveGeoPolicyRecord")
    if policy_doc.get("record_type") != "SensitiveGeoPolicyRecord":
        fail("policy record_type must be SensitiveGeoPolicyRecord")
    policy = policy_doc.get("policy")
    scope = policy_doc.get("scope")
    controls = policy_doc.get("controls")
    if not isinstance(policy, dict):
        fail("policy must be object")
    if not isinstance(scope, dict):
        fail("scope must be object")
    if not isinstance(controls, dict):
        fail("controls must be object")
    require_fields(policy, REQUIRED_POLICY, "policy")
    require_fields(scope, REQUIRED_SCOPE, "scope")
    require_fields(controls, REQUIRED_CONTROLS, "controls")


def validate_subject(subject: Dict[str, Any]) -> None:
    require_fields(subject, REQUIRED_SUBJECT_TOP, "subject")
    if subject.get("record_type") == "SensitiveGeoPolicyRecord":
        fail("subject must be an evaluated data record, not the policy itself")
    classification = subject.get("classification")
    governance = subject.get("governance")
    if not isinstance(classification, dict):
        fail("subject.classification must be object")
    if not isinstance(governance, dict):
        fail("subject.governance must be object")
    if "sensitive_geo_policy_ref" not in classification:
        fail("subject.classification missing sensitive_geo_policy_ref")


def infer_subject_domain(subject: Dict[str, Any]) -> str:
    record_type = subject.get("record_type")
    mapping = {
        "TelemetryObservation": "space-telemetry",
        "SpaceAssetRecord": "space-telemetry",
        "VesselTrackObservation": "maritime-domain-awareness",
        "AirTrackObservation": "air-domain-awareness",
        "SensorObservationEnvelope": "sensor-fusion",
        "EarthObservationProductRecord": "earth-observation",
        "MultiDomainFusionEvent": "multi-domain-fusion",
    }
    return mapping.get(str(record_type), "unknown")


def evaluate(policy_doc: Dict[str, Any], subject: Dict[str, Any]) -> Dict[str, Any]:
    validate_policy(policy_doc)
    validate_subject(subject)

    policy = policy_doc["policy"]
    scope = policy_doc["scope"]
    controls = policy_doc["controls"]
    governance = subject["governance"]
    classification = subject["classification"]
    subject_domain = infer_subject_domain(subject)
    domain_lanes = scope.get("domain_lanes", [])
    if not isinstance(domain_lanes, list):
        fail("scope.domain_lanes must be array")

    matched_policy_ref = classification.get("sensitive_geo_policy_ref") == policy.get("policy_id")
    sensitive_tier = governance.get("safety_tier") in {"sensitive_geo", "defense_authorized", "public_safety", "export_controlled"}
    domain_in_scope = subject_domain in domain_lanes or subject_domain == "multi-domain-fusion"

    if matched_policy_ref or sensitive_tier or domain_in_scope:
        effective_action = policy["default_action"]
        approval_required = True
        disposition = "restricted_advisory_output"
    else:
        effective_action = "allow_with_standard_attribution"
        approval_required = False
        disposition = "standard_governed_output"

    output = {
        "artifact_version": "v1",
        "artifact_type": "gaia.sensitive_geo_policy_eval.output",
        "evaluation_id": f"policy-eval:{policy['policy_id']}:{subject['record_id']}",
        "runtime_id": "runtime:sensitive-geo-policy-eval:v0",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "policy_ref": policy["policy_id"],
        "subject_ref": subject["record_id"],
        "subject_record_type": subject["record_type"],
        "subject_domain": subject_domain,
        "matched_policy_ref": matched_policy_ref,
        "domain_in_scope": domain_in_scope,
        "sensitive_tier": sensitive_tier,
        "effective_action": effective_action,
        "approval_required": approval_required,
        "disposition": disposition,
        "controls": {
            "masking": controls["masking"],
            "delay": controls["delay"],
            "access_control": controls["access_control"],
            "audit": controls["audit"]
        },
        "accountability": {
            "ledger_required": approval_required,
            "authority_required": approval_required,
            "human_approval_required": approval_required,
            "notes": "Policy evaluation is advisory governance output. It does not unmask, target, engage, or authorize effects."
        },
        "provenance": {
            "chain": ["runtime:sensitive-geo-policy-eval:v0"],
            "derived_from": [policy_doc["record_id"], subject["record_id"]],
            "runtime_boundary_id": "runtime:sensitive-geo-policy-eval:v0"
        },
        "classification": {
            "security_marking": subject.get("classification", {}).get("security_marking", "unknown"),
            "sensitive_geo_policy_ref": policy["policy_id"]
        }
    }
    output["runtime_evidence"] = build_runtime_evidence(policy_doc, subject, output)
    return output


def build_runtime_evidence(policy_doc: Dict[str, Any], subject: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    input_bundle = {
        "policy": policy_doc,
        "subject": subject,
    }
    return {
        "evidence_version": "v1",
        "evidence_id": f"evidence:runtime:sensitive-geo-policy-eval:{output['evaluation_id']}",
        "runtime_id": "runtime:sensitive-geo-policy-eval:v0",
        "runtime_class": "analytics",
        "standards_refs": [*REQUIRED_STANDARDS, AGENT_STANDARD_REF],
        "input_manifest": {
            "input_ref": f"{policy_doc['record_id']}::{subject['record_id']}",
            "input_sha256": sha256_ref(input_bundle),
            "input_schema_hint": "sensitive-geo-policy-plus-subject-record.v1"
        },
        "output_manifest": {
            "output_ref": output["evaluation_id"],
            "output_sha256": sha256_ref(output),
            "output_schema_ref": "gaia.sensitive_geo_policy_eval.output.v1"
        },
        "policy": {
            "approval_required": output["approval_required"],
            "sensitive_geo_handling": output["effective_action"],
            "network_posture": "none_for_fixture_proof",
            "secret_posture": "none_for_fixture_proof"
        },
        "replay": {
            "mode": "deterministic_fixture",
            "command": "python3 multidomain/sensitive_geo_policy_eval.py fixtures/multidomain/sensitive-geo-policy.sample.v1.json fixtures/multidomain/multi-domain-fusion-event.sample.v1.json /tmp/gaia-sensitive-geo-policy-eval-output.json"
        }
    }


def main(argv: List[str]) -> int:
    if len(argv) != 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    policy_path = Path(argv[1])
    subject_path = Path(argv[2])
    target_path = Path(argv[3])
    output = evaluate(load_json(policy_path), load_json(subject_path))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
