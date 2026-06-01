#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "operations" / "operational_topology_blast_radius.v0_1.schema.json"
FIXTURES = [
    ROOT / "fixtures" / "operations" / "workroom-post-merge-topology.valid.json",
]


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object: {path}")
    return data


def schema_errors(schema: dict[str, Any], data: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
        path = "/".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"schema:{path}: {error.message}")
    return errors


def semantic_errors(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_refs = {item.get("evidence_ref") for item in data.get("source_evidence", []) if isinstance(item, dict)}
    node_refs = {item.get("node_ref") for item in data.get("nodes", []) if isinstance(item, dict)}

    if data.get("blast_radius", {}).get("radius_status") == "confirmed_by_observation":
        errors.append("fixture must not use confirmed_by_observation without observational impact evidence")

    for node in data.get("nodes", []):
        for ref in node.get("evidence_refs", []):
            if ref not in evidence_refs:
                errors.append(f"node {node.get('node_ref')} references missing evidence {ref}")

    for edge in data.get("edges", []):
        if edge.get("source_node_ref") not in node_refs:
            errors.append(f"edge {edge.get('edge_ref')} source_node_ref missing from nodes")
        if edge.get("target_node_ref") not in node_refs:
            errors.append(f"edge {edge.get('edge_ref')} target_node_ref missing from nodes")
        for ref in edge.get("evidence_refs", []):
            if ref not in evidence_refs:
                errors.append(f"edge {edge.get('edge_ref')} references missing evidence {ref}")

    blast = data.get("blast_radius", {})
    for ref in blast.get("affected_node_refs", []) + blast.get("candidate_consumer_refs", []):
        if ref not in node_refs:
            errors.append(f"blast_radius references missing node {ref}")

    non_claim_text = "\n".join(str(item) for item in data.get("non_claims", [])).lower()
    for required in ("does not prove rca", "does not authorize remediation", "does not certify signadot"):
        if not all(word in non_claim_text for word in required.split()):
            errors.append(f"non_claims must include posture equivalent to {required!r}")

    return errors


def main() -> int:
    schema = load(SCHEMA)
    failed = False
    results: dict[str, Any] = {}
    for path in FIXTURES:
        data = load(path)
        errors = schema_errors(schema, data) + semantic_errors(data)
        failed = failed or bool(errors)
        results[str(path.relative_to(ROOT))] = errors

    report = {
        "validator": "gaia.operational-topology-blast-radius.validator.v1",
        "passed": not failed,
        "results": results,
        "non_claims": [
            "Validator checks operational topology fixture semantics only.",
            "Validator does not execute runtime probes.",
            "Validator does not certify RCA causality.",
            "Validator does not authorize remediation."
        ]
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    print(("PASS" if not failed else "FAIL") + ": operational topology blast radius fixtures")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
