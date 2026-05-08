#!/usr/bin/env python3
"""validate adapter – gaia.features.validate.v1

Validates normalized GAIA feature bindings (from prepare.py) against
the GAIA OSM feature contract. Emits a validation-report JSON.

Usage:
  python3 adapters/validate.py \\
      --bindings build/gaia/features/osm-feature-bindings.v1.json \\
      --out build/evidence/validation-report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

ODBL_LICENSE_REF = "ODbL-1.0"
REQUIRED_OSM_TYPES = {"node", "way", "relation"}


def _check(checks: list, name: str, condition: bool, message: str = "") -> bool:
    status = "passed" if condition else "failed"
    checks.append({"check_name": name, "status": status, "message": message or status})
    return condition


def validate_bindings(doc: dict, checks: list) -> None:
    _check(checks, "artifact_type",
           doc.get("artifact_type") == "gaia.osm_bounded_source_adapter.bindings",
           f"artifact_type={doc.get('artifact_type')!r}")

    bindings = doc.get("bindings", [])
    _check(checks, "bindings_non_empty", isinstance(bindings, list) and len(bindings) > 0,
           f"binding count={len(bindings)}")

    seen_types: set = set()
    seen_ids: set = set()
    for idx, b in enumerate(bindings):
        bp = f"binding[{idx}]"
        osm_ref = b.get("osm_ref", {})
        osm_type = osm_ref.get("osm_type")
        osm_id = osm_ref.get("osm_id")
        seen_types.add(osm_type)
        identity = (osm_type, osm_id)
        _check(checks, f"{bp}.no_duplicate_identity", identity not in seen_ids,
               f"identity={identity}")
        seen_ids.add(identity)
        _check(checks, f"{bp}.osm_type_valid", osm_type in {"node", "way", "relation"},
               f"osm_type={osm_type!r}")
        _check(checks, f"{bp}.osm_id_present", bool(osm_id), f"osm_id={osm_id!r}")
        spatial = b.get("spatial", {})
        _check(checks, f"{bp}.geometry_ref", bool(spatial.get("geometry_ref")), "")
        bbox = spatial.get("bbox")
        _check(checks, f"{bp}.bbox_4elem", isinstance(bbox, list) and len(bbox) == 4,
               f"bbox={bbox}")
        h3 = spatial.get("h3_cells")
        _check(checks, f"{bp}.h3_non_empty", isinstance(h3, list) and len(h3) > 0, "")
        attr = b.get("attribution", {})
        _check(checks, f"{bp}.license_ref",
               attr.get("license_ref") == ODBL_LICENSE_REF,
               f"license_ref={attr.get('license_ref')!r}")
        _check(checks, f"{bp}.attribution_text", bool(attr.get("attribution_text")), "")
        prov = b.get("provenance", {})
        _check(checks, f"{bp}.source_refs", bool(prov.get("source_refs")), "")
        _check(checks, f"{bp}.fixture_digest", bool(prov.get("fixture_digest")), "")

    _check(checks, "all_osm_types_present", REQUIRED_OSM_TYPES.issubset(seen_types),
           f"seen_types={sorted(seen_types)}")

    top_attr = doc.get("attribution", {})
    _check(checks, "top_level_license_ref",
           top_attr.get("license_ref") == ODBL_LICENSE_REF,
           f"license_ref={top_attr.get('license_ref')!r}")

    top_prov = doc.get("provenance", {})
    _check(checks, "top_level_source_refs", bool(top_prov.get("source_refs")), "")
    _check(checks, "top_level_fixture_digest", bool(top_prov.get("fixture_digest")), "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate GAIA normalized OSM feature bindings.")
    parser.add_argument("--bindings", required=True, help="Path to osm-feature-bindings JSON.")
    parser.add_argument("--out", required=True, help="Path to write validation-report JSON.")
    args = parser.parse_args(argv)

    bindings_path = Path(args.bindings)
    if not bindings_path.is_absolute():
        bindings_path = ROOT / bindings_path
    if not bindings_path.exists():
        print(f"ERROR: bindings file not found: {bindings_path}", file=sys.stderr)
        return 1

    with bindings_path.open("r", encoding="utf-8") as fh:
        doc = json.load(fh)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    checks: list[dict] = []
    validate_bindings(doc, checks)

    passed = sum(1 for c in checks if c["status"] == "passed")
    failed = sum(1 for c in checks if c["status"] == "failed")
    status = "passed" if failed == 0 else "failed"

    fixture_digest = doc.get("provenance", {}).get("fixture_digest", "")
    report_id = f"gaia-osm-validation-{fixture_digest[-12:] if fixture_digest else 'unknown'}"

    report = {
        "report_version": "v1",
        "report_id": report_id,
        "artifact_type": "gaia.osm_bounded_ingest.validation_report",
        "generated_at": generated_at,
        "fixture_digest": fixture_digest,
        "status": status,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "skipped": 0,
        },
        "attribution": {
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": "© OpenStreetMap contributors",
        },
    }

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"  OK  validation: {status} ({passed}/{len(checks)} checks passed)", file=sys.stderr)
    print(f"  OK  validation report → {out_path}", file=sys.stderr)
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
