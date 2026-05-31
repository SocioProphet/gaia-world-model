#!/usr/bin/env python3
"""attest adapter – prophet-platform.attest-run.v1

Assembles the final attestation for a bounded OSM ingest run:
  - run-record  (what was run, when, with what inputs)
  - checksums   (SHA-256 of all evidence artifacts)
  - lineage     (causal chain from input fixture to outputs)

All outputs are local JSON files. No network I/O in fixture mode.

Usage:
  python3 adapters/attest.py \\
      --source-receipts build/evidence/source-receipts.json \\
      --validation-report build/evidence/validation-report.json \\
      --benchmark-report build/evidence/benchmark-report.json \\
      --bindings build/gaia/features/osm-feature-bindings.v1.json \\
      --tile-manifest build/gaia/tiles/tile-manifest.json \\
      --out-run-record build/evidence/run-record.json \\
      --out-checksums build/evidence/checksums.json \\
      --out-lineage build/evidence/lineage.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "sha256:missing"
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def resolve(p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    """Return path relative to ROOT if possible, else the absolute path string."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(p: Path) -> dict:
    if not p.exists():
        print(f"ERROR: file not found: {p}", file=sys.stderr)
        raise SystemExit(1)
    with p.open() as fh:
        return json.load(fh)


def write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"  OK  → {p}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Attest a bounded OSM ingest run.")
    parser.add_argument("--source-receipts", required=True)
    parser.add_argument("--validation-report", required=True)
    parser.add_argument("--benchmark-report", required=True)
    parser.add_argument("--bindings", required=True)
    parser.add_argument("--tile-manifest", required=True)
    parser.add_argument("--out-run-record", required=True)
    parser.add_argument("--out-checksums", required=True)
    parser.add_argument("--out-lineage", required=True)
    args = parser.parse_args(argv)

    receipts_path = resolve(args.source_receipts)
    val_path = resolve(args.validation_report)
    bench_path = resolve(args.benchmark_report)
    bindings_path = resolve(args.bindings)
    manifest_path = resolve(args.tile_manifest)

    receipts = load_json(receipts_path)
    val_doc = load_json(val_path)
    bench_doc = load_json(bench_path)
    bindings_doc = load_json(bindings_path)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    fixture_digest = bindings_doc.get("provenance", {}).get("fixture_digest", "")
    run_id = f"gaia-osm-ingest-run-{fixture_digest[-12:] if fixture_digest else 'unknown'}-{generated_at[:10]}"

    # Run record
    run_record = {
        "run_record_version": "v1",
        "run_id": run_id,
        "artifact_type": "gaia.osm_bounded_ingest.run_record",
        "generated_at": generated_at,
        "mode": "fixture",
        "safety_class": "bounded",
        "fixture_digest": fixture_digest,
        "extract_ref": bindings_doc.get("extract_ref", ""),
        "feature_count": bench_doc.get("metrics", {}).get("feature_count", 0),
        "validation_status": val_doc.get("status", "unknown"),
        "validation_summary": val_doc.get("summary", {}),
        "inputs": {
            "osm_source": receipts.get("osm_source", {}),
            "region_bbox": receipts.get("region_bbox", {}),
        },
        "outputs": {
            "bindings": rel(bindings_path),
            "tile_manifest": rel(manifest_path) if manifest_path.exists() else "",
            "validation_report": rel(val_path),
            "benchmark_report": rel(bench_path),
        },
        "attribution": {
            "license_ref": "ODbL-1.0",
            "attribution_text": "© OpenStreetMap contributors",
            "source_url": "https://www.openstreetmap.org",
        },
        "policy": {
            "network_io": False,
            "privileged": False,
            "promotion_gate": "gaia-bounded-osm-fixture-validation",
        },
    }
    write_json(resolve(args.out_run_record), run_record)

    # Checksums
    evidence_files = [
        receipts_path,
        val_path,
        bench_path,
        bindings_path,
        manifest_path,
    ]
    checksums_entries = []
    for ef in evidence_files:
        checksums_entries.append({
            "path": rel(ef) if ef.exists() else str(ef),
            "digest": sha256_file(ef),
        })

    checksums = {
        "checksums_version": "v1",
        "artifact_type": "gaia.osm_bounded_ingest.checksums",
        "run_id": run_id,
        "generated_at": generated_at,
        "files": checksums_entries,
    }
    write_json(resolve(args.out_checksums), checksums)

    # Lineage
    lineage = {
        "lineage_version": "v1",
        "artifact_type": "gaia.osm_bounded_ingest.lineage",
        "run_id": run_id,
        "generated_at": generated_at,
        "causal_chain": [
            {
                "step": 1,
                "verb": "fetch",
                "description": "Bounded OSM fixture loaded from disk; no network I/O.",
                "input": receipts.get("osm_source", {}).get("path", ""),
                "input_digest": receipts.get("osm_source", {}).get("digest", ""),
            },
            {
                "step": 2,
                "verb": "prepare",
                "description": "OSM features normalized into GAIA bindings.",
                "input": receipts.get("osm_source", {}).get("path", ""),
                "output": rel(bindings_path),
                "output_digest": sha256_file(bindings_path),
            },
            {
                "step": 3,
                "verb": "validate",
                "description": "GAIA feature bindings validated against OSM feature contract.",
                "input": rel(bindings_path),
                "output": rel(val_path),
                "validation_status": val_doc.get("status", "unknown"),
            },
            {
                "step": 4,
                "verb": "run",
                "description": "Feature store and tile manifest written.",
                "output_manifest": rel(manifest_path) if manifest_path.exists() else "",
            },
            {
                "step": 5,
                "verb": "benchmark",
                "description": "Deterministic metrics collected.",
                "output": rel(bench_path),
                "metrics": bench_doc.get("metrics", {}),
            },
        ],
        "fixture_digest": fixture_digest,
        "attribution": {
            "license_ref": "ODbL-1.0",
            "attribution_text": "© OpenStreetMap contributors",
        },
    }
    write_json(resolve(args.out_lineage), lineage)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
