#!/usr/bin/env python3
"""Validate GAIA-owned Orion/OSIRIS source-record fixtures.

This is a dependency-light structural validator. It does not execute any live
source adapter and does not import or run code from mdheller/osiris.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "orion-osiris" / "source-records"

REQUIRED_FIELDS = [
    "schema_version",
    "source_record_id",
    "source_name",
    "source_family",
    "observed_at",
    "ingested_at",
    "evidence_grade",
    "risk_class",
    "provenance",
]

ALLOWED_EVIDENCE_GRADES = {
    "fixture.synthetic",
    "public_source.unverified",
    "public_source.versioned",
    "public_source.attributed",
    "operator_report.unverified",
    "fused.inferred",
    "policy_gated.action",
}

ALLOWED_RISK_CLASSES = {"low", "medium", "high", "unknown"}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            doc = json.load(handle)
    except FileNotFoundError:
        fail(f"missing fixture: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(doc, dict):
        fail(f"{path} must contain a JSON object")
    return doc


def check_source_record(path: Path, doc: Dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in doc]
    if missing:
        fail(f"{path} missing required fields: {', '.join(missing)}")

    if doc["schema_version"] != "0.1.0":
        fail(f"{path} has unsupported schema_version")

    if not str(doc["source_record_id"]).startswith("gaia-src-"):
        fail(f"{path} source_record_id must start with gaia-src-")

    if doc["evidence_grade"] not in ALLOWED_EVIDENCE_GRADES:
        fail(f"{path} has invalid evidence_grade {doc['evidence_grade']}")

    if doc["risk_class"] not in ALLOWED_RISK_CLASSES:
        fail(f"{path} has invalid risk_class {doc['risk_class']}")

    provenance = doc["provenance"]
    if not isinstance(provenance, dict):
        fail(f"{path} provenance must be an object")
    for field in ["retrieval_mode", "canonicalization_status"]:
        if field not in provenance:
            fail(f"{path} provenance missing {field}")

    if doc["source_family"] == "cyber" and "Scanner/sweep execution remains SCOPE-D-owned" not in doc.get("notes", ""):
        fail(f"{path} cyber source record must state SCOPE-D scanner/sweep boundary")


def main() -> int:
    if not FIXTURE_DIR.exists():
        fail(f"missing fixture directory: {FIXTURE_DIR}")

    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    if not fixtures:
        fail(f"no source-record fixtures in {FIXTURE_DIR}")

    ids = set()
    for fixture in fixtures:
        doc = load_json(fixture)
        check_source_record(fixture, doc)
        source_id = doc["source_record_id"]
        if source_id in ids:
            fail(f"duplicate source_record_id {source_id}")
        ids.add(source_id)

    print(f"validated {len(fixtures)} Orion/OSIRIS Gaia source-record fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
