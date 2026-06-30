#!/usr/bin/env python3
"""Validate GAIA smart-economy domain fixtures.

The smart-economy domain binds GAIA to the Economic Prophet framework
(SocioProphet/economic-prophet). This validator mirrors the dependency-light
style of scripts/validate_multidomain_fixtures.py and proves that:

- records carry the GAIA envelope (record_type, standards_refs, provenance, governance);
- the embedded ep_output carries Economic Prophet's required EP components;
- the EP additive identity holds:
      economic_profit = revenue - expected_loss - expense
                        - funding_costs + funding_credits - taxes - capital_charge
  (Economic Profit is UVMC's canonical additive value measure);
- the embedded UVMC measurement_context carries its required fields + lineage;
- the bundled negative fixture (broken EP identity) is correctly rejected.

If a sibling economic-prophet checkout is found, the embedded ep_output and
measurement_context are additionally validated against that repo's canonical
JSON schemas (when `jsonschema` is installed).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "schemas/economy/economy_observation.v1.schema.json"
RECORD_TYPE = "EconomyObservation"
REQUIRED = [
    "record_version", "record_type", "record_id", "standards_refs",
    "economic_prophet", "source", "provenance", "governance", "classification",
]
EP_COMPONENTS = [
    "revenue", "expected_loss", "expense",
    "funding_costs", "funding_credits", "taxes", "capital_charge",
]
UVMC_REQUIRED = [
    "measurement_context_id", "object_id", "object_type", "as_of", "period_id",
    "horizon", "scenario_id", "model_version", "parameter_set", "formula_version",
    "cadence", "source_system", "lineage",
]

POSITIVE_FIXTURES = ["fixtures/economy/economy-observation.sample.v1.json"]
NEGATIVE_FIXTURES = ["fixtures/economy/negative/economy-observation.broken-ep-identity.v1.json"]

TOPOLOGY_SCHEMA = "schemas/economy/economy_network_topology.v1.schema.json"
TOPOLOGY_FIXTURE = "fixtures/economy/economy-network-topology.sample.v1.json"

ACTION_INTENT_SCHEMA = "schemas/actions/action-intent.schema.json"
POLICY_DECISION_SCHEMA = "schemas/policy/policy-decision.schema.json"
POLICY_AUDIT_ACTION = "fixtures/economy/action-intent.policy-audit.v1.json"
POLICY_AUDIT_DECISION = "fixtures/economy/policy-decision.policy-audit.v1.json"

EP_REPO_CANDIDATES = [
    ROOT.parent / "economic-prophet",
    ROOT.parent / "SocioProphet__economic-prophet",
]


class CheckError(Exception):
    pass


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
        raise CheckError(f"{path} missing required fields: {', '.join(missing)}")


def ep_additive_value(components: Dict[str, float]) -> float:
    return (
        components["revenue"]
        - components["expected_loss"]
        - components["expense"]
        - components["funding_costs"]
        + components["funding_credits"]
        - components["taxes"]
        - components["capital_charge"]
    )


def validate(path: str) -> None:
    doc = load_json(ROOT / path)
    check_required(path, doc, REQUIRED)
    if doc.get("record_type") != RECORD_TYPE:
        raise CheckError(f"{path} expected record_type={RECORD_TYPE}, got {doc.get('record_type')!r}")
    if not doc.get("provenance", {}).get("derived_from"):
        raise CheckError(f"{path} missing provenance.derived_from")
    governance = doc.get("governance", {})
    for field in ["privacy_tier", "safety_tier", "retention_tier", "redistribution"]:
        if field not in governance:
            raise CheckError(f"{path} governance missing {field}")

    ep = doc["economic_prophet"]
    check_required(f"{path}:economic_prophet", ep, ["framework_ref", "ep_output", "measurement_context"])

    ep_output = ep["ep_output"]
    check_required(f"{path}:ep_output", ep_output, ["object_id", "as_of", "horizon", "economic_profit", "components"])
    components = ep_output["components"]
    check_required(f"{path}:ep_output.components", components, EP_COMPONENTS)
    expected = ep_additive_value(components)
    if abs(expected - ep_output["economic_profit"]) > 1e-6:
        raise CheckError(
            f"{path}: EP additive identity violated — components imply {round(expected, 6)}, "
            f"economic_profit is {ep_output['economic_profit']}"
        )

    ctx = ep["measurement_context"]
    check_required(f"{path}:measurement_context", ctx, UVMC_REQUIRED)
    check_required(f"{path}:measurement_context.lineage", ctx["lineage"], ["parent_chain", "type_chain"])


def cross_validate_against_economic_prophet() -> str:
    repo = next((p for p in EP_REPO_CANDIDATES if p.exists()), None)
    if repo is None:
        return "skipped (no sibling economic-prophet checkout)"
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return f"skipped (jsonschema not installed; found {repo.name})"
    ep_schema = load_json(repo / "schemas" / "ep_output.schema.json")
    ctx_schema = load_json(repo / "schemas" / "uvmc_measurement_context.schema.json")
    doc = load_json(ROOT / POSITIVE_FIXTURES[0])
    ep = doc["economic_prophet"]
    jsonschema.Draft202012Validator(ep_schema).validate(ep["ep_output"])
    # measurement_context schema forbids additionalProperties; validate the shared subset.
    ctx = {k: ep["measurement_context"][k] for k in ep["measurement_context"] if k in ctx_schema["properties"]}
    jsonschema.Draft202012Validator(ctx_schema).validate(ctx)
    return f"ok (validated against {repo.name} canonical schemas)"


def validate_topology() -> None:
    doc = load_json(ROOT / TOPOLOGY_FIXTURE)
    try:
        import jsonschema  # type: ignore
        jsonschema.Draft202012Validator(load_json(ROOT / TOPOLOGY_SCHEMA)).validate(doc)
    except ImportError:
        check_required(TOPOLOGY_FIXTURE, doc, ["networks", "nodes", "edges"])
    network_ids = {n["network_id"] for n in doc["networks"]}
    node_ids = {n["node_id"] for n in doc["nodes"]}
    for node in doc["nodes"]:
        if node["network_id"] not in network_ids:
            raise CheckError(f"{TOPOLOGY_FIXTURE}: node {node['node_id']} references unknown network {node['network_id']}")
    for edge in doc["edges"]:
        for endpoint in ("from_node", "to_node"):
            if edge[endpoint] not in node_ids:
                raise CheckError(f"{TOPOLOGY_FIXTURE}: edge {edge['edge_id']} {endpoint} references unknown node {edge[endpoint]}")
        if edge["network_id"] not in network_ids:
            raise CheckError(f"{TOPOLOGY_FIXTURE}: edge {edge['edge_id']} references unknown network {edge['network_id']}")


def validate_policy_audit() -> None:
    action = load_json(ROOT / POLICY_AUDIT_ACTION)
    decision = load_json(ROOT / POLICY_AUDIT_DECISION)
    try:
        import jsonschema  # type: ignore
        jsonschema.Draft202012Validator(load_json(ROOT / ACTION_INTENT_SCHEMA)).validate(action)
        jsonschema.Draft202012Validator(load_json(ROOT / POLICY_DECISION_SCHEMA)).validate(decision)
    except ImportError:
        check_required(POLICY_AUDIT_ACTION, action, ["id", "actor", "verb"])
        check_required(POLICY_AUDIT_DECISION, decision, ["id", "decision"])
    if action.get("verb") != "audit":
        raise CheckError(f"{POLICY_AUDIT_ACTION}: expected verb=audit, got {action.get('verb')!r}")
    if decision.get("decision") not in {"allow", "deny", "constrain", "review"}:
        raise CheckError(f"{POLICY_AUDIT_DECISION}: invalid decision {decision.get('decision')!r}")
    refs = decision.get("evidence_refs", [])
    if action["id"] not in refs:
        raise CheckError(f"{POLICY_AUDIT_DECISION}: evidence_refs must cite the audit action {action['id']}")
    if action["target"] not in refs:
        raise CheckError(f"{POLICY_AUDIT_DECISION}: evidence_refs must cite the audited target {action['target']}")


def main() -> int:
    schema = load_json(ROOT / SCHEMA)
    schema_required = schema.get("required")
    if isinstance(schema_required, list):
        for field in REQUIRED:
            if field not in schema_required:
                fail(f"{SCHEMA} does not declare expected required field {field}")

    checked = 0
    for fixture in POSITIVE_FIXTURES:
        try:
            validate(fixture)
        except CheckError as exc:
            fail(str(exc))
        checked += 1

    for fixture in NEGATIVE_FIXTURES:
        try:
            validate(fixture)
        except CheckError:
            checked += 1
            continue
        fail(f"negative fixture {fixture} unexpectedly passed validation")

    try:
        validate_topology()
    except CheckError as exc:
        fail(str(exc))
    checked += 1

    try:
        validate_policy_audit()
    except CheckError as exc:
        fail(str(exc))
    checked += 1

    cross = cross_validate_against_economic_prophet()
    print(f"validated {checked} GAIA smart-economy fixture(s) (observation, topology, policy-audit; incl. negative cases)")
    print(f"economic-prophet cross-validation: {cross}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
