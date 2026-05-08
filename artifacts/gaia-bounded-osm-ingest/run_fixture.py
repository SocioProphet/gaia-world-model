#!/usr/bin/env python3
"""GAIA Bounded OSM Ingest – Local Fixture Runner

Executes the full ProphetArtifact verb sequence in order:
  1. detect  – host runtime facts
  2. fetch   – resolve region-bbox and OSM source fixtures
  3. prepare – normalize OSM features into GAIA bindings
  4. validate – validate GAIA feature bindings
  5. run     – write feature store and tile manifest
  6. benchmark – collect deterministic metrics
  7. publish  – emit Sociosphere, Sherlock, and Delivery Excellence payloads
  8. attest   – assemble run-record, checksums, and lineage

All effects are local and bounded. No live network ingestion. No privileged
runtime. Outputs are deterministic given the same input fixture.

Usage:
  python3 artifacts/gaia-bounded-osm-ingest/run_fixture.py [--out build/gaia/osm-ingest]

Exit codes:
  0 – all verbs completed successfully
  1 – one or more verbs failed (see stderr for details)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = Path(__file__).resolve().parent / "adapters"

# Ensure the adapters directory is importable
sys.path.insert(0, str(ADAPTERS))

import detect as detect_mod
import fetch as fetch_mod
import prepare as prepare_mod
import validate as validate_mod
import run as run_mod
import benchmark as benchmark_mod
import publish as publish_mod
import attest as attest_mod


FIXTURE_BBOX = "fixtures/gaia/osm/regions/demo-bbox.json"
FIXTURE_SOURCE = "fixtures/osm/demo-region.osm.json"


def step(name: str, fn, *args, **kwargs) -> None:
    print(f"\n── [{name}] ──────────────────────────────────────────", file=sys.stderr)
    rc = fn(*args, **kwargs)
    if rc != 0:
        print(f"ERROR: verb '{name}' exited with code {rc}", file=sys.stderr)
        raise SystemExit(rc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="GAIA bounded OSM ingest local fixture runner."
    )
    parser.add_argument(
        "--out",
        default="artifacts/gaia-bounded-osm-ingest/build",
        help="Output directory root. Default: artifacts/gaia-bounded-osm-ingest/build",
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help="Override generated_at timestamp (ISO 8601) for fully deterministic CI runs.",
    )
    args = parser.parse_args(argv)

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out

    # Derived paths
    evidence = out / "evidence"
    gaia_osm = out / "gaia" / "osm"
    gaia_features = out / "gaia" / "features"
    gaia_tiles = out / "gaia" / "tiles"

    host_facts_path        = str(evidence / "host-facts.json")
    source_receipts_path   = str(evidence / "source-receipts.json")
    bindings_path          = str(gaia_features / "osm-feature-bindings.v1.json")
    ndjson_path            = str(gaia_osm / "normalized-features.ndjson")
    validation_path        = str(evidence / "validation-report.json")
    tile_manifest_path     = str(gaia_tiles / "tile-manifest.json")
    benchmark_path         = str(evidence / "benchmark-report.json")
    sociosphere_path       = str(evidence / "sociosphere-registration.json")
    sherlock_path          = str(evidence / "sherlock-index-payload.json")
    de_path                = str(evidence / "delivery-excellence-scoreboard.json")
    run_record_path        = str(evidence / "run-record.json")
    checksums_path         = str(evidence / "checksums.json")
    lineage_path           = str(evidence / "lineage.json")

    t0 = time.monotonic()

    # 1. detect
    step("detect", detect_mod.main, ["--out", host_facts_path])

    # 2. fetch
    step("fetch", fetch_mod.main, [
        "--bbox", FIXTURE_BBOX,
        "--source", FIXTURE_SOURCE,
        "--out", source_receipts_path,
    ])

    # 3. prepare
    prepare_argv = [
        "--source", FIXTURE_SOURCE,
        "--out-ndjson", ndjson_path,
        "--out-bindings", bindings_path,
    ]
    if args.generated_at:
        prepare_argv += ["--generated-at", args.generated_at]
    step("prepare", prepare_mod.main, prepare_argv)

    # 4. validate
    step("validate", validate_mod.main, [
        "--bindings", bindings_path,
        "--out", validation_path,
    ])

    # 5. run
    step("run", run_mod.main, [
        "--bindings", bindings_path,
        "--out-store", str(gaia_features),
        "--out-manifest", tile_manifest_path,
    ])

    # 6. benchmark
    latency_ms = (time.monotonic() - t0) * 1000
    step("benchmark", benchmark_mod.main, [
        "--bindings", bindings_path,
        "--validation-report", validation_path,
        "--out", benchmark_path,
        "--latency-ms", str(round(latency_ms, 1)),
    ])

    # 7. publish
    step("publish", publish_mod.main, [
        "--bindings", bindings_path,
        "--validation-report", validation_path,
        "--benchmark-report", benchmark_path,
        "--out-sociosphere", sociosphere_path,
        "--out-sherlock", sherlock_path,
        "--out-delivery-excellence", de_path,
    ])

    # 8. attest
    step("attest", attest_mod.main, [
        "--source-receipts", source_receipts_path,
        "--validation-report", validation_path,
        "--benchmark-report", benchmark_path,
        "--bindings", bindings_path,
        "--tile-manifest", tile_manifest_path,
        "--out-run-record", run_record_path,
        "--out-checksums", checksums_path,
        "--out-lineage", lineage_path,
    ])

    total_ms = (time.monotonic() - t0) * 1000
    print(f"\n  ✓  GAIA bounded OSM ingest complete in {total_ms:.0f}ms", file=sys.stderr)
    print(f"     outputs: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
