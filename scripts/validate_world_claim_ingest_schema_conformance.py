#!/usr/bin/env python3
"""Validate that geospatial/world_claim_ingest.py emits schema-conformant WorldClaims.

SocioProphet/gaia-world-model's Propose step (geospatial/world_claim_ingest.py)
must emit WorldClaim / SourceEvidence / FusionExplanation records that validate
against the canonical v1 JSON Schemas:

  - schemas/geospatial/world_claim.v1.schema.json
  - schemas/geospatial/source_evidence.v1.schema.json
  - schemas/geospatial/fusion_explanation.v1.schema.json

socioprophet-web/client-vue/src/gaia/worldClaim.ts mirrors these same schemas
field-for-field for the cockpit, so schema conformance here is also cockpit
contract conformance.

Unlike scripts/validate_contract_fixtures.py and
scripts/validate_chronos_carrier_fixtures.py (dependency-light by design,
jsonschema optional), this validator requires `jsonschema` and hard-fails
without it, matching the precedent in
scripts/validate_operational_topology_blast_radius.py. See
.github/workflows/contract-fixtures.yml, which pins jsonschema==4.23.0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

WORLD_CLAIM_SCHEMA = ROOT / "schemas/geospatial/world_claim.v1.schema.json"
SOURCE_EVIDENCE_SCHEMA = ROOT / "schemas/geospatial/source_evidence.v1.schema.json"
FUSION_EXPLANATION_SCHEMA = ROOT / "schemas/geospatial/fusion_explanation.v1.schema.json"

INGEST_SCRIPT = ROOT / "geospatial/world_claim_ingest.py"
INPUT_FIXTURE = ROOT / "fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json"
GOLDEN_FIXTURE = ROOT / "fixtures/geospatial/osm-feature-world-claim.sample.v1.json"
RUNTIME_OUTPUT = Path("/tmp/gaia-world-claim-ingest-schema-conformance-output.json")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def run_ingest(output_path: Path) -> Dict[str, Any]:
    """Run the real world_claim_ingest.py CLI entrypoint against the fixture input."""
    subprocess.run(
        [sys.executable, str(INGEST_SCRIPT), str(INPUT_FIXTURE), str(output_path)],
        check=True,
        cwd=ROOT,
    )
    return load_json(output_path)


def validate_bundle(
    label: str,
    doc: Dict[str, Any],
    claim_validator: Draft202012Validator,
    evidence_validator: Draft202012Validator,
    trace_validator: Draft202012Validator,
) -> int:
    """Validate every claim/evidence/trace record in a world_claim_ingest.py-style bundle."""
    checked = 0
    for claim in doc.get("claims", []):
        errors = list(claim_validator.iter_errors(claim))
        if errors:
            details = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
            fail(f"{label}: claim {claim.get('claim_id')!r} fails world_claim.v1 schema: {details}")
        checked += 1
    for evidence in doc.get("evidence_records", []):
        errors = list(evidence_validator.iter_errors(evidence))
        if errors:
            details = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
            fail(f"{label}: evidence {evidence.get('evidence_id')!r} fails source_evidence.v1 schema: {details}")
        checked += 1
    for trace in doc.get("explanation_traces", []):
        errors = list(trace_validator.iter_errors(trace))
        if errors:
            details = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
            fail(f"{label}: trace {trace.get('trace_id')!r} fails fusion_explanation.v1 schema: {details}")
        checked += 1
    if checked == 0:
        fail(f"{label}: expected at least one claim/evidence/trace record, found none")
    return checked


def check_no_stray_anchor_source_ref(label: str, doc: Dict[str, Any]) -> None:
    """Regression guard for the specific non-conformance this validator was added for.

    GeoAnchor, when embedded inline under WorldClaim.geo_anchor, does not
    declare a "source_ref" property and additionalProperties=false rejects
    it. Assert this directly (in addition to the schema check above) so the
    failure mode is self-explanatory if it ever regresses.
    """
    for claim in doc.get("claims", []):
        anchor = claim.get("geo_anchor", {})
        if "source_ref" in anchor:
            fail(
                f"{label}: claim {claim.get('claim_id')!r} geo_anchor carries 'source_ref', "
                "which is not an allowed property of the inline WorldClaim.geo_anchor schema"
            )


def main() -> int:
    claim_validator = Draft202012Validator(load_json(WORLD_CLAIM_SCHEMA))
    evidence_validator = Draft202012Validator(load_json(SOURCE_EVIDENCE_SCHEMA))
    trace_validator = Draft202012Validator(load_json(FUSION_EXPLANATION_SCHEMA))

    bundles: List[Tuple[str, Dict[str, Any]]] = [
        (str(RUNTIME_OUTPUT), run_ingest(RUNTIME_OUTPUT)),
        (str(GOLDEN_FIXTURE), load_json(GOLDEN_FIXTURE)),
    ]

    checked = 0
    for label, doc in bundles:
        checked += validate_bundle(label, doc, claim_validator, evidence_validator, trace_validator)
        check_no_stray_anchor_source_ref(label, doc)

    print(
        f"validated {checked} WorldClaim/SourceEvidence/FusionExplanation record(s) "
        "against the full v1 schemas (world_claim_ingest.py runtime output + golden fixture)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
