#!/usr/bin/env python3
"""Validate the GAIA value-flow subsystem contract -- with teeth in BOTH directions.

This binds the estate's economic spine (Economic Prophet omnirisk/EP + the in-flight
welfare-annealing dynamics) UPWARD into the GAIA world model and the digital-twin
hierarchy. The economic spine is the *value-flow subsystem* of the world model: its
carrying-capacity term and natural-capital base are READS of the world-model biosphere
state, its QoL objective AGGREGATES from human-digital-twin state, and value flows are
the exchange dynamics across the galactic <-> world-economic <-> human twin stack.

A control that never fires is suspect (feedback: control-that-cannot-fail). So this
checker asserts BOTH that valid fixtures are admitted AND that every invalid fixture is
rejected/flagged for its *specific* tooth, and it FAILS if any tooth is never exercised
in the firing direction (no dead teeth).

Teeth:

  T1-CONST    (Binding 1, carrying-capacity <-> biosphere): a binding whose
              carrying_capacity.source.kind == "constant" (a hardcoded free parameter
              instead of a world-model read) is REJECTED -- the free-parameter smell.

  T1-RESERVE  (Binding 1/4): a value-flow that draws a non-renewable stock below the
              world-model's declared reserve floor is FLAGGED -- a planetary-boundary
              breach (the paper-inductance false-growth analog). Admitted-with-flag, not
              rejected: the run is real, the flag is the receipt.

  T2-CONSERVE (Binding 2, twin-hierarchy value conservation, IC-1): a cross-scale value
              flow where parent.value != sum(children) + sum(sinks) - sum(sources), i.e.
              value is created out of nothing, is REJECTED.

  T3-QOL      (Binding 3, QoL <-> human digital twin): a population QoL index with any
              dimension not derivable from constituent human-twin dimensions
              (derivation.kind != "twin_aggregate", or a twin_aggregate lacking its
              from_twin_dimension) is REJECTED -- the exogenous-QoL smell.

  T4-REGEN    (Binding 4, ecosystem <-> biosphere): a renewable_harvest rung whose
              regeneration rate is a constant instead of a world-model read is REJECTED.

  T5-RESOLVE  (Bindings 1/4, resolution): a world_model_read whose read_ref does NOT
              resolve to a declared biosphere-state entry (examples/biosphere/**) is
              REJECTED -- a read pointing at nothing. This is what makes T1-CONST,
              T1-RESERVE and T4-REGEN load-bearing: a source may not merely *claim* to be
              a world-model read, it must resolve to declared substrate-W state.

  T6-COMPOSE  (Binding 2, composition): a TwinScaleValueTransfer whose scale_stack is not
              the declared ordered stack, or whose parent->child scales are not an
              adjacent parent->child edge in the twin-hierarchy composition record
              (gaia/twins/composition.v1.json), is REJECTED.

Consume-by-reference: the carrying-capacity discount and welfare objective from
economic-prophet@feat/welfare-annealing; the Jacob's-ladder rung ontology
(natural_capital / extractive_nonrenewable / renewable_harvest) from
economic-prophet asset_ladder (ALC-1); the human-twin state dimensions from
gaia/twins/human/twin-schema.json. Nothing is vendored.

Deterministic, stdlib only (json, sys, pathlib). No third-party dependency, so CI is
bulletproof. Self-validating: fixtures carry an `_expected` verdict this checker asserts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples" / "economy" / "value_flow"
BIOSPHERE_STATES = ROOT / "examples" / "biosphere"
COMPOSITION_RECORD = ROOT / "gaia" / "twins" / "composition.v1.json"

# Every tooth the contract declares. Each MUST fire on at least one fixture (no dead
# teeth) and MUST NOT fire on the admitted fixtures.
DECLARED_TEETH = {
    "T1-CONST", "T1-RESERVE", "T2-CONSERVE", "T3-QOL", "T4-REGEN",
    "T5-RESOLVE", "T6-COMPOSE",
}

# Bootstrap structural requirements (dependency-light, mirrors the GAIA contract-fixture
# validator). The full JSON Schema lives alongside each record in schemas/economy/.
REQUIRED_BINDING = [
    "binding_version", "binding_type", "binding_id", "world_model_ref",
    "economic_spine_ref", "carrying_capacity", "ecosystem_assets", "qol_index",
    "provenance", "classification",
]
REQUIRED_TRANSFER = [
    "transfer_version", "transfer_type", "transfer_id", "scale_stack", "parent",
    "children", "conservation", "provenance", "classification",
]
CANONICAL_SCALE_STACK = ["galactic_space_twin", "world_economic_twin", "human_digital_twin"]


class Verdict:
    """Outcome of judging one record: an admit/reject decision plus any flags fired."""

    def __init__(self) -> None:
        self.rejected_by: List[str] = []
        self.flagged_by: List[str] = []

    @property
    def decision(self) -> str:
        if self.rejected_by:
            return "reject"
        if self.flagged_by:
            return "admit_with_flag"
        return "admit"

    @property
    def teeth(self) -> List[str]:
        return self.rejected_by + self.flagged_by


def _missing(record: Dict[str, Any], required: List[str]) -> List[str]:
    return [k for k in required if k not in record]


def load_biosphere_refs() -> set[str]:
    """Every read_ref declared by the biosphere/resource state (the resolution target)."""
    refs: set[str] = set()
    if not BIOSPHERE_STATES.is_dir():
        return refs
    for path in sorted(BIOSPHERE_STATES.glob("*.json")):
        state = json.loads(path.read_text(encoding="utf-8"))
        cc = state.get("carrying_capacity", {}).get("read_ref")
        if cc:
            refs.add(cc)
        for entry in state.get("reserves", []) + state.get("regeneration_rates", []):
            if entry.get("read_ref"):
                refs.add(entry["read_ref"])
    return refs


def load_composition() -> Dict[str, Any]:
    """The declared twin-hierarchy composition record, or {} if absent."""
    if not COMPOSITION_RECORD.exists():
        return {}
    return json.loads(COMPOSITION_RECORD.read_text(encoding="utf-8"))


def _binding_read_refs(rec: Dict[str, Any]) -> List[str]:
    """Every read_ref a binding claims as a world_model_read (carrying-capacity,
    renewable regeneration, and reserve floors)."""
    refs: List[str] = []
    cc = rec.get("carrying_capacity", {}).get("source", {})
    if cc.get("kind") == "world_model_read":
        refs.append(cc.get("read_ref"))
    for asset in rec.get("ecosystem_assets", []):
        regen = asset.get("regeneration", {}).get("source", {})
        if regen.get("kind") == "world_model_read":
            refs.append(regen.get("read_ref"))
        reserve = asset.get("stock", {}).get("reserve", {}).get("source", {})
        if reserve.get("kind") == "world_model_read":
            refs.append(reserve.get("read_ref"))
    return refs


def judge_binding(rec: Dict[str, Any], biosphere_refs: set[str]) -> Verdict:
    v = Verdict()

    # T1-CONST -- carrying capacity must be a world-model read, not a free constant.
    cc_kind = rec.get("carrying_capacity", {}).get("source", {}).get("kind")
    if cc_kind != "world_model_read":
        v.rejected_by.append("T1-CONST")

    # T5-RESOLVE -- every claimed world_model_read must resolve to a declared biosphere
    # state entry. A source may not merely *claim* to read from W; the ref must exist.
    for ref in _binding_read_refs(rec):
        if not ref or ref not in biosphere_refs:
            if "T5-RESOLVE" not in v.rejected_by:
                v.rejected_by.append("T5-RESOLVE")

    # T3-QOL -- every QoL dimension must aggregate from a human-twin dimension.
    for dim in rec.get("qol_index", {}).get("dimensions", []):
        deriv = dim.get("derivation", {})
        if deriv.get("kind") != "twin_aggregate" or not deriv.get("from_twin_dimension"):
            v.rejected_by.append("T3-QOL")
            break

    for asset in rec.get("ecosystem_assets", []):
        rung = asset.get("rung")
        regen_kind = asset.get("regeneration", {}).get("source", {}).get("kind")
        # T4-REGEN -- renewable regeneration rate must be a world-model read.
        if rung == "renewable_harvest" and regen_kind != "world_model_read":
            if "T4-REGEN" not in v.rejected_by:
                v.rejected_by.append("T4-REGEN")
        # T1-RESERVE -- a non-renewable draw below the declared reserve floor is flagged.
        stock = asset.get("stock", {})
        draw = stock.get("non_renewable_draw", 0) or 0
        current = stock.get("current", 0) or 0
        floor = stock.get("reserve", {}).get("floor", 0) or 0
        if rung in ("natural_capital", "extractive_nonrenewable") and draw > 0:
            if (current - draw) < floor:
                if "T1-RESERVE" not in v.flagged_by:
                    v.flagged_by.append("T1-RESERVE")

    return v


def judge_transfer(rec: Dict[str, Any], composition: Dict[str, Any]) -> Verdict:
    v = Verdict()

    # T6-COMPOSE -- the transfer must be consistent with the declared twin-hierarchy
    # composition: its scale_stack must be the declared ordered stack, and its
    # parent->child scales must be a declared adjacent parent->child edge.
    ordered = composition.get("ordered_stack", CANONICAL_SCALE_STACK)
    edges = {(s.get("scale"), s.get("child")) for s in composition.get("scales", [])}
    parent_scale = rec.get("parent", {}).get("scale")
    child_scales = {c.get("scale") for c in rec.get("children", [])}
    stack_ok = rec.get("scale_stack") == ordered
    edges_ok = all((parent_scale, cs) in edges for cs in child_scales) if edges else True
    if not stack_ok or not edges_ok:
        v.rejected_by.append("T6-COMPOSE")

    parent = rec.get("parent", {}).get("value", 0) or 0
    children = sum((c.get("value", 0) or 0) for c in rec.get("children", []))
    sinks = sum((s.get("amount", 0) or 0) for s in rec.get("declared_sinks", []))
    sources = sum((s.get("amount", 0) or 0) for s in rec.get("declared_sources", []))
    tol = rec.get("conservation", {}).get("tolerance", 0) or 0

    # T2-CONSERVE (IC-1) -- value must be conserved across the aggregation.
    residual = parent - (children + sinks - sources)
    if abs(residual) > tol:
        v.rejected_by.append("T2-CONSERVE")

    return v


def judge(rec: Dict[str, Any], biosphere_refs: set[str], composition: Dict[str, Any]) -> Tuple[str, Verdict, List[str]]:
    """Return (kind, verdict, structural_errors)."""
    if rec.get("binding_type") == "ValueFlowSubsystemBinding":
        errs = _missing(rec, REQUIRED_BINDING)
        return "binding", judge_binding(rec, biosphere_refs), errs
    if rec.get("transfer_type") == "TwinScaleValueTransfer":
        errs = _missing(rec, REQUIRED_TRANSFER)
        return "transfer", judge_transfer(rec, composition), errs
    return "unknown", Verdict(), ["unrecognized record: no binding_type/transfer_type"]


def main() -> int:
    if not FIXTURES.is_dir():
        print(f"FAIL: fixtures directory not found: {FIXTURES}", file=sys.stderr)
        return 1

    fixtures = sorted(FIXTURES.glob("*.json"))
    if not fixtures:
        print(f"FAIL: no fixtures under {FIXTURES}", file=sys.stderr)
        return 1

    biosphere_refs = load_biosphere_refs()
    composition = load_composition()
    if not biosphere_refs:
        print(f"FAIL: no biosphere state declared under {BIOSPHERE_STATES}", file=sys.stderr)
        return 1
    if not composition.get("ordered_stack"):
        print(f"FAIL: twin-hierarchy composition record missing: {COMPOSITION_RECORD}", file=sys.stderr)
        return 1

    failures: List[str] = []
    fired_teeth: set[str] = set()
    checked = 0

    for path in fixtures:
        rel = path.relative_to(ROOT)
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{rel}: not valid JSON: {exc}")
            continue

        expected = rec.get("_expected")
        if not expected:
            failures.append(f"{rel}: fixture carries no `_expected` verdict block")
            continue

        kind, verdict, struct_errs = judge(rec, biosphere_refs, composition)
        if kind == "unknown":
            failures.append(f"{rel}: {struct_errs}")
            continue

        # Admitted records must be structurally complete; rejected ones need not be.
        if expected.get("verdict") in ("admit", "admit_with_flag") and struct_errs:
            failures.append(f"{rel}: admitted record missing required fields: {struct_errs}")

        want_verdict = expected.get("verdict")
        want_tooth = expected.get("tooth")

        if verdict.decision != want_verdict:
            failures.append(
                f"{rel}: verdict mismatch -- expected {want_verdict!r} got "
                f"{verdict.decision!r} (teeth fired: {verdict.teeth or 'none'})"
            )
        elif want_tooth and want_tooth not in verdict.teeth:
            failures.append(
                f"{rel}: expected tooth {want_tooth!r} to fire, but fired: "
                f"{verdict.teeth or 'none'}"
            )

        for t in verdict.teeth:
            fired_teeth.add(t)

        marker = {"admit": "ADMIT", "admit_with_flag": "FLAG", "reject": "REJECT"}[verdict.decision]
        print(f"  [{marker:6}] {rel}  teeth={verdict.teeth or '-'}  expected={want_verdict}")
        checked += 1

    # No dead teeth: every declared tooth must have fired on some fixture.
    dead = DECLARED_TEETH - fired_teeth
    if dead:
        failures.append(f"dead teeth never exercised in firing direction: {sorted(dead)}")

    print()
    print(f"checked {checked} fixture(s); teeth exercised: {sorted(fired_teeth)}")

    if failures:
        print("\nFAIL:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("OK: value-flow subsystem contract holds; all teeth fire in both directions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
