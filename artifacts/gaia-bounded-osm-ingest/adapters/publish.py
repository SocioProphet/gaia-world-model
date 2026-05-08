#!/usr/bin/env python3
"""publish adapter – prophet-platform.registry-export.v1

Builds and emits downstream payloads for:
  - Sociosphere registration
  - Sherlock/Holmes index payload
  - Delivery Excellence scoreboard payload

All outputs are local JSON files (no network I/O in fixture mode).

Usage:
  python3 adapters/publish.py \\
      --bindings build/gaia/features/osm-feature-bindings.v1.json \\
      --validation-report build/evidence/validation-report.json \\
      --benchmark-report build/evidence/benchmark-report.json \\
      --out-sociosphere build/evidence/sociosphere-registration.json \\
      --out-sherlock build/evidence/sherlock-index-payload.json \\
      --out-delivery-excellence build/evidence/delivery-excellence-scoreboard.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

ODBL_LICENSE_REF = "ODbL-1.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish GAIA OSM ingest payloads to downstream consumers.")
    parser.add_argument("--bindings", required=True)
    parser.add_argument("--validation-report", required=True)
    parser.add_argument("--benchmark-report", required=True)
    parser.add_argument("--out-sociosphere", required=True)
    parser.add_argument("--out-sherlock", required=True)
    parser.add_argument("--out-delivery-excellence", required=True)
    args = parser.parse_args(argv)

    def load(p: str) -> dict:
        path = Path(p) if Path(p).is_absolute() else ROOT / p
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            raise SystemExit(1)
        with path.open() as fh:
            return json.load(fh)

    bindings_doc = load(args.bindings)
    val_doc = load(args.validation_report)
    bench_doc = load(args.benchmark_report)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    fixture_digest = bindings_doc.get("provenance", {}).get("fixture_digest", "")
    attribution = bindings_doc.get("attribution", {})
    classification = bindings_doc.get("classification", {})
    extract_ref = bindings_doc.get("extract_ref", "")
    metrics = bench_doc.get("metrics", {})

    def write(path_arg: str, payload: dict) -> None:
        p = Path(path_arg) if Path(path_arg).is_absolute() else ROOT / path_arg
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"  OK  payload → {p}", file=sys.stderr)

    # Sociosphere registration
    sociosphere = {
        "payload_version": "v1",
        "artifact_type": "gaia.osm_bounded_ingest.sociosphere_registration",
        "generated_at": generated_at,
        "fixture_digest": fixture_digest,
        "entity_count": metrics.get("feature_count", 0),
        "layer_ref": bindings_doc.get("envelope_ref", ""),
        "extract_ref": extract_ref,
        "validation_status": val_doc.get("status", "unknown"),
        "attribution": {
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": attribution.get("attribution_text", "© OpenStreetMap contributors"),
        },
        "classification": classification,
        "mode": "fixture",
    }
    write(args.out_sociosphere, sociosphere)

    # Sherlock/Holmes index payload
    bindings = bindings_doc.get("bindings", [])
    sherlock_records = []
    for b in bindings:
        osm_ref = b.get("osm_ref", {})
        gaia_ref = b.get("gaia_ref", {})
        spatial = b.get("spatial", {})
        sherlock_records.append({
            "record_version": "v1",
            "entity_id": gaia_ref.get("entity_id", ""),
            "entity_type": gaia_ref.get("entity_type", ""),
            "osm_type": osm_ref.get("osm_type", ""),
            "osm_id": osm_ref.get("osm_id", ""),
            "name": osm_ref.get("tags", {}).get("name", ""),
            "tags": osm_ref.get("tags", {}),
            "bbox": spatial.get("bbox", []),
            "h3_cells": spatial.get("h3_cells", []),
            "extract_ref": extract_ref,
            "fixture_digest": fixture_digest,
        })
    sherlock_payload = {
        "payload_version": "v1",
        "artifact_type": "gaia.osm_bounded_ingest.sherlock_index_payload",
        "generated_at": generated_at,
        "fixture_digest": fixture_digest,
        "records": sherlock_records,
        "attribution": {
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": attribution.get("attribution_text", "© OpenStreetMap contributors"),
        },
    }
    write(args.out_sherlock, sherlock_payload)

    # Delivery Excellence scoreboard payload
    de_payload = {
        "payload_version": "v1",
        "artifact_type": "gaia.osm_bounded_ingest.delivery_excellence_scoreboard",
        "generated_at": generated_at,
        "fixture_digest": fixture_digest,
        "metrics": metrics,
        "validation_status": val_doc.get("status", "unknown"),
        "validation_summary": val_doc.get("summary", {}),
        "scoreboard_eligible": bench_doc.get("scoreboard_eligible", True),
        "delivery_excellence_ref": bench_doc.get("delivery_excellence_ref", ""),
    }
    write(args.out_delivery_excellence, de_payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
