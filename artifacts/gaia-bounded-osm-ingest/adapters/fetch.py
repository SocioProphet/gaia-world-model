#!/usr/bin/env python3
"""fetch adapter – gaia.osm.fetch-bounded-region.v1

Resolves the region-bbox fixture and returns the bounded OSM source
(the fixture file). In fixture mode this performs no network I/O:
it reads a local file and emits a source-receipt confirming the
fixture was located and is attribution-complete.

Usage:
  python3 adapters/fetch.py \\
      --bbox fixtures/gaia/osm/regions/demo-bbox.json \\
      --source fixtures/osm/demo-region.osm.json \\
      --out build/evidence/source-receipts.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

ODBL_LICENSE_REF = "ODbL-1.0"


def sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch bounded OSM region source (fixture mode).")
    parser.add_argument("--bbox", required=True, help="Path to region-bbox fixture JSON.")
    parser.add_argument("--source", required=True, help="Path to bounded OSM source fixture JSON.")
    parser.add_argument("--out", required=True, help="Path to write source-receipts JSON.")
    args = parser.parse_args(argv)

    bbox_path = Path(args.bbox)
    if not bbox_path.is_absolute():
        bbox_path = ROOT / bbox_path
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = ROOT / source_path

    if not bbox_path.exists():
        print(f"ERROR: bbox fixture not found: {bbox_path}", file=sys.stderr)
        return 1
    if not source_path.exists():
        print(f"ERROR: OSM source fixture not found: {source_path}", file=sys.stderr)
        return 1

    bbox_doc = load_json(bbox_path)
    source_doc = load_json(source_path)

    # Validate attribution chain
    source_attr = source_doc.get("attribution", {})
    if source_attr.get("license_ref") != ODBL_LICENSE_REF:
        print(f"ERROR: source fixture attribution.license_ref must be '{ODBL_LICENSE_REF}'", file=sys.stderr)
        return 1

    source_digest = sha256_file(source_path)
    bbox_digest = sha256_file(bbox_path)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    receipt = {
        "receipts_version": "v1",
        "artifact_type": "gaia.osm_bounded_ingest.fetch_receipts",
        "generated_at": generated_at,
        "mode": "fixture",
        "region_bbox": {
            "path": str(bbox_path.relative_to(ROOT)),
            "digest": bbox_digest,
            "region_name": bbox_doc.get("region_name", ""),
            "bbox": bbox_doc.get("bbox", []),
            "crs": bbox_doc.get("crs", ""),
        },
        "osm_source": {
            "path": str(source_path.relative_to(ROOT)),
            "digest": source_digest,
            "extract_ref": source_doc.get("extract_ref", ""),
            "extracted_at": source_doc.get("extracted_at", ""),
            "feature_count": len(source_doc.get("features", [])),
        },
        "attribution": {
            "source_name": source_attr.get("source_name", "OpenStreetMap"),
            "license_ref": ODBL_LICENSE_REF,
            "attribution_text": source_attr.get("attribution_text", "© OpenStreetMap contributors"),
            "source_url": source_attr.get("source_url", "https://www.openstreetmap.org"),
        },
        "network_io": False,
        "policy": {
            "safety_class": "bounded",
            "fixture_mode": True,
        },
    }

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"  OK  source receipts written to {out_path}", file=sys.stderr)
    print(f"  OK  source digest: {source_digest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
