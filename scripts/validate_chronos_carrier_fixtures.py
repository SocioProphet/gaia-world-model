#!/usr/bin/env python3
"""Validate the CHRONOS-carrier-compatible extension to WorldClaim/FusionExplanation.

SocioProphet/gaia-world-model#38 (per sociosphere's
docs/integration/neurosymbolic-chronos-alignment.md "neuro-symbolic carrier
boundary") extends WorldClaim and FusionExplanation with additive, optional
fields so a claim can also be expressed as a CHRONOS carrier:

  - FusionExplanation.fusion_rule.chronos_method_family
  - FusionExplanation.fusion_rule.chronos_method_output_type
  - FusionExplanation.chronos_non_authority_declaration
  - WorldClaim.chronos_grounding_status
  - WorldClaim.chronos_owning_authority_plane

This validator mirrors the dependency-light structural style of
scripts/validate_contract_fixtures.py and scripts/validate_economy_fixtures.py
and proves, without requiring an installed `jsonschema`:

  - the two schemas declare the new properties (and keep them optional, so the
    extension is additive/non-breaking for every existing fixture);
  - positive fixtures (including classical, non-neuro-symbolic fusions that
    don't use the new fields at all, and the new LTN-style neuro-symbolic
    fixture that uses all of them) satisfy the CHRONOS carrier invariant;
  - the bundled negative fixture (a fuzzy satisfaction score promoted to
    policy_status=admitted with no non-authority declaration) is correctly
    rejected — this is CHRONOS's "Required negative rules" #1: "a fuzzy
    satisfaction score is promoted as truth."

If `jsonschema` is installed, the claim/trace payloads are additionally
validated against the full world_claim.v1 / fusion_explanation.v1 schemas.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

WORLD_CLAIM_SCHEMA = "schemas/geospatial/world_claim.v1.schema.json"
FUSION_EXPLANATION_SCHEMA = "schemas/geospatial/fusion_explanation.v1.schema.json"

# Fixtures may be a single hand-authored bundle ({"claim": {...}, "explanation_trace": {...}})
# or a world_claim_ingest.py-style script output ({"claims": [...], "explanation_traces": [...]}).
POSITIVE_FIXTURES = [
    "fixtures/geospatial/osm-feature-world-claim.sample.v1.json",
    "fixtures/geospatial/eo-osm-dem-fusion-world-claim.sample.v1.json",
    "fixtures/geospatial/ltn-fuzzy-vegetation-dryness-risk-world-claim.sample.v1.json",
]
NEGATIVE_FIXTURES = [
    "fixtures/geospatial/negative/world-claim-fuzzy-score-admitted-without-non-authority-declaration.invalid.v1.json",
]

# chronos_method_output_type values that are soft/candidate signals per the CHRONOS
# alignment doc's method-family table (never hard sensor/deterministic values).
SOFT_OUTPUT_TYPES = {
    "fuzzy_satisfaction_score",
    "truth_bound",
    "symbolic_derivation",
    "learned_rule_candidate",
    "ontology_delta_candidate",
    "policy_proposal",
    "event_schema_candidate",
}
# chronos_method_family values that name an actual neuro-symbolic technique
# (as opposed to GAIA's own classical/deterministic default or not_applicable).
NEURO_SYMBOLIC_FAMILIES = {
    "logic_review_formal_substrate",
    "kautz_nsr_taxonomy_label",
    "ltn_differentiable_fuzzy_logic",
    "lnn_truth_bound_propagation",
    "neurasp_neural_to_asp",
    "satnet_differentiable_constraint",
    "dilp_differentiable_rule_learning",
    "deep_ontological_network_rrn",
    "dsr_dsp_symbolic_policy",
    "kairos_event_schema_induction",
}


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


def extract_claim_trace_pairs(path: str, doc: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any], Dict[str, Any]]]:
    """Return (label, claim, trace) tuples from either bundle shape this repo uses."""
    pairs: List[Tuple[str, Dict[str, Any], Dict[str, Any]]] = []
    if "claim" in doc and "explanation_trace" in doc:
        pairs.append((path, doc["claim"], doc["explanation_trace"]))
        return pairs
    if "claims" in doc and "explanation_traces" in doc:
        traces_by_id = {t["trace_id"]: t for t in doc["explanation_traces"]}
        for claim in doc["claims"]:
            trace_ref = claim.get("explanation_trace_ref")
            trace = traces_by_id.get(trace_ref)
            if trace is None:
                raise CheckError(f"{path}: claim {claim.get('claim_id')} references missing trace {trace_ref!r}")
            pairs.append((f"{path}:{claim.get('claim_id')}", claim, trace))
        return pairs
    raise CheckError(f"{path}: expected a 'claim'/'explanation_trace' bundle or 'claims'/'explanation_traces' lists")


def check_chronos_carrier(label: str, claim: Dict[str, Any], trace: Dict[str, Any]) -> None:
    fusion_rule = trace.get("fusion_rule", {})
    method_family = fusion_rule.get("chronos_method_family", "classical_deterministic")
    output_type = fusion_rule.get("chronos_method_output_type", "hard_value")

    is_neuro_symbolic = method_family in NEURO_SYMBOLIC_FAMILIES
    is_soft_output = output_type in SOFT_OUTPUT_TYPES
    requires_declaration = is_neuro_symbolic or is_soft_output

    declaration = trace.get("chronos_non_authority_declaration")

    if requires_declaration:
        if not declaration:
            raise CheckError(
                f"{label}: chronos_method_family={method_family!r}/chronos_method_output_type={output_type!r} "
                "requires a chronos_non_authority_declaration on the explanation trace, but none is present "
                "(CHRONOS negative rule: 'a fuzzy satisfaction score is promoted as truth')"
            )
        if declaration.get("is_candidate_only") is not True:
            raise CheckError(
                f"{label}: chronos_non_authority_declaration.is_candidate_only must be true when "
                f"chronos_method_family={method_family!r}/chronos_method_output_type={output_type!r}"
            )
        if not declaration.get("declaration"):
            raise CheckError(f"{label}: chronos_non_authority_declaration.declaration must be a non-empty string")
        status = claim.get("policy_status", {}).get("status")
        if status == "admitted":
            raise CheckError(
                f"{label}: a candidate-only carrier (chronos_non_authority_declaration.is_candidate_only=true) "
                f"must not have policy_status.status=admitted, got {status!r}"
            )
    else:
        # Classical/deterministic path: existing GAIA behavior must keep working
        # unchanged whether or not a declaration happens to be present.
        if declaration is not None and declaration.get("is_candidate_only") is False:
            # Explicitly declaring "not candidate-only" is only meaningful alongside
            # a neuro-symbolic method/output; on the classical path it's inert, so
            # this is not an error — just nothing further to check.
            pass


def validate(path: str) -> None:
    doc = load_json(ROOT / path)
    for label, claim, trace in extract_claim_trace_pairs(path, doc):
        check_chronos_carrier(label, claim, trace)


def check_schemas_declare_new_properties() -> None:
    world_claim_schema = load_json(ROOT / WORLD_CLAIM_SCHEMA)
    fusion_schema = load_json(ROOT / FUSION_EXPLANATION_SCHEMA)

    wc_props = world_claim_schema.get("properties", {})
    for prop in ("chronos_grounding_status", "chronos_owning_authority_plane"):
        if prop not in wc_props:
            fail(f"{WORLD_CLAIM_SCHEMA}: expected additive property {prop!r} not declared")
        if prop in world_claim_schema.get("required", []):
            fail(f"{WORLD_CLAIM_SCHEMA}: {prop!r} must stay optional (additive extension) but is in 'required'")

    fusion_rule_props = fusion_schema.get("properties", {}).get("fusion_rule", {}).get("properties", {})
    for prop in ("chronos_method_family", "chronos_method_output_type"):
        if prop not in fusion_rule_props:
            fail(f"{FUSION_EXPLANATION_SCHEMA}: expected additive fusion_rule property {prop!r} not declared")
        if prop in fusion_schema["properties"]["fusion_rule"].get("required", []):
            fail(f"{FUSION_EXPLANATION_SCHEMA}: fusion_rule.{prop} must stay optional but is in fusion_rule 'required'")

    if "chronos_non_authority_declaration" not in fusion_schema.get("properties", {}):
        fail(f"{FUSION_EXPLANATION_SCHEMA}: expected additive property 'chronos_non_authority_declaration' not declared")
    if "chronos_non_authority_declaration" in fusion_schema.get("required", []):
        fail(f"{FUSION_EXPLANATION_SCHEMA}: 'chronos_non_authority_declaration' must stay optional but is in 'required'")


def cross_validate_with_jsonschema() -> str:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return "skipped (jsonschema not installed)"

    world_claim_validator = jsonschema.Draft202012Validator(load_json(ROOT / WORLD_CLAIM_SCHEMA))
    fusion_validator = jsonschema.Draft202012Validator(load_json(ROOT / FUSION_EXPLANATION_SCHEMA))

    checked = 0
    for path in POSITIVE_FIXTURES:
        doc = load_json(ROOT / path)
        for label, claim, trace in extract_claim_trace_pairs(path, doc):
            world_claim_validator.validate(claim)
            fusion_validator.validate(trace)
            checked += 1
    return f"ok (validated {checked} claim/trace pairs against full v1 schemas)"


def main() -> int:
    check_schemas_declare_new_properties()

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
        fail(f"negative fixture {fixture} unexpectedly passed CHRONOS carrier validation")

    cross = cross_validate_with_jsonschema()
    print(f"validated {checked} CHRONOS carrier fixture(s) (positive + negative) for WorldClaim/FusionExplanation")
    print(f"jsonschema cross-validation: {cross}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
