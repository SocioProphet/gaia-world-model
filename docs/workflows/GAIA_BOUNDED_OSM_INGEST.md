# GAIA Bounded OSM Ingest – Vertical Slice Workflow

## Overview

This document describes the **GAIA bounded OSM ingest** ProphetArtifact vertical
slice. It is the first fixture-backed, reproducible, policy-bounded GAIA ingest
workflow that can be executed by the Prophet Platform artifact runner.

All effects are **local and bounded**: no live network ingestion, no production
tile-serving requirement, no privileged runtime.

---

## Artifact location

```
artifacts/gaia-bounded-osm-ingest/
├── prophet-artifact.yaml           # ProphetArtifact manifest
├── run_fixture.py                  # Local fixture runner (all 8 verbs)
├── adapters/
│   ├── detect.py                   # verb: detect  (sourceos.host-detect.v1)
│   ├── fetch.py                    # verb: fetch   (gaia.osm.fetch-bounded-region.v1)
│   ├── prepare.py                  # verb: prepare (gaia.osm.normalize.v1)
│   ├── validate.py                 # verb: validate (gaia.features.validate.v1)
│   ├── run.py                      # verb: run     (gaia.ingest.bounded.v1)
│   ├── benchmark.py                # verb: benchmark (delivery-excellence.metrics.collect.v1)
│   ├── publish.py                  # verb: publish (prophet-platform.registry-export.v1)
│   └── attest.py                   # verb: attest  (prophet-platform.attest-run.v1)
└── schemas/
    ├── gaia.region-bbox.schema.json
    ├── gaia.osm-feature.schema.json
    ├── gaia.source-receipt.schema.json
    ├── gaia.validation-report.schema.json
    ├── gaia.benchmark-report.schema.json
    └── gaia.tile-manifest.schema.json
```

---

## Fixture data

| File | Purpose |
|------|---------|
| `fixtures/gaia/osm/regions/demo-bbox.json` | Region bbox input – Lower Manhattan demo region |
| `fixtures/osm/demo-region.osm.json` | Bounded OSM source (3 features: node, way, relation) |

Both fixtures use the **Lower Manhattan bounded extract** (bbox: `[-74.012, 40.705, -73.998, 40.718]`,
EPSG:4326). Attribution: © OpenStreetMap contributors, ODbL-1.0.

---

## Running the fixture locally

```bash
# From the repo root
python3 artifacts/gaia-bounded-osm-ingest/run_fixture.py

# Outputs go to:
#   artifacts/gaia-bounded-osm-ingest/build/
```

Or override the output directory:

```bash
python3 artifacts/gaia-bounded-osm-ingest/run_fixture.py --out /tmp/my-gaia-run
```

For fully deterministic CI runs (pin the timestamp):

```bash
python3 artifacts/gaia-bounded-osm-ingest/run_fixture.py \
  --generated-at 2026-04-26T00:00:00Z \
  --out /tmp/ci-gaia-run
```

---

## Verb sequence

The runner executes these verbs in order:

| # | Verb | Adapter | Description |
|---|------|---------|-------------|
| 1 | detect | `sourceos.host-detect.v1` | Emit host runtime facts |
| 2 | fetch | `gaia.osm.fetch-bounded-region.v1` | Resolve fixtures, emit source receipts |
| 3 | prepare | `gaia.osm.normalize.v1` | Normalize OSM features → GAIA bindings |
| 4 | validate | `gaia.features.validate.v1` | Validate bindings against OSM feature contract |
| 5 | run | `gaia.ingest.bounded.v1` | Write feature store + tile manifest |
| 6 | benchmark | `delivery-excellence.metrics.collect.v1` | Collect deterministic metrics |
| 7 | publish | `prophet-platform.registry-export.v1` | Emit Sociosphere, Sherlock, DE payloads |
| 8 | attest | `prophet-platform.attest-run.v1` | Assemble run-record, checksums, lineage |

---

## Output artifacts

All outputs land under `build/` (relative to `--out`):

```
build/
├── evidence/
│   ├── host-facts.json
│   ├── source-receipts.json          ← schema: gaia.source-receipt.schema.json
│   ├── validation-report.json        ← schema: gaia.validation-report.schema.json
│   ├── benchmark-report.json         ← schema: gaia.benchmark-report.schema.json
│   ├── sociosphere-registration.json
│   ├── sherlock-index-payload.json
│   ├── delivery-excellence-scoreboard.json
│   ├── run-record.json
│   ├── checksums.json
│   └── lineage.json
├── gaia/
│   ├── osm/
│   │   └── normalized-features.ndjson   ← schema: gaia.osm-feature.schema.json
│   ├── features/
│   │   ├── osm-feature-bindings.v1.json
│   │   ├── node-111111.json
│   │   ├── way-424242.json
│   │   └── relation-999.json
│   └── tiles/
│       └── tile-manifest.json           ← schema: gaia.tile-manifest.schema.json
```

Every output carries:
- **provenance**: `fixture_digest` (SHA-256 of the input OSM fixture)
- **attribution**: `© OpenStreetMap contributors`, `ODbL-1.0`
- **classification**: `public`, `["demo", "osm", "bounded-extract", "geospatial", "advisory"]`

---

## Evidence and provenance

The `attest` verb assembles three evidence documents:

- **`checksums.json`** – SHA-256 of every evidence artifact
- **`run-record.json`** – what was run, with what inputs, outputs, and policy
- **`lineage.json`** – causal chain from input fixture → normalized features → validation → metrics

The `fixture_digest` field (SHA-256 of `fixtures/osm/demo-region.osm.json`) threads
through every output, providing an unbroken chain back to the input.

---

## OSM attribution and ODbL license

All outputs preserve OSM attribution:

```json
{
  "attribution": {
    "source_name": "OpenStreetMap",
    "license_ref": "ODbL-1.0",
    "attribution_text": "© OpenStreetMap contributors",
    "source_url": "https://www.openstreetmap.org"
  }
}
```

The `fetch` adapter validates that the source fixture carries `license_ref: "ODbL-1.0"` before
proceeding. No output is emitted without attribution.

---

## How this becomes the `/map` workbench demo loop

The `/map` workbench is the interactive UI entry point for GAIA geospatial
exploration. This vertical slice provides the backend data pipeline for it:

1. **User selects a region** on the `/map` workbench (or accepts the default demo bbox).
2. The workbench calls the `fetch` verb with the chosen `region-bbox`.
3. The `prepare` → `validate` → `run` chain produces the feature store and tile manifest.
4. The tile manifest's `url_template` is passed to the map renderer to load the vector tiles.
5. The `publish` verb posts the Sherlock index payload, making features searchable.
6. The `attest` output (lineage + checksums) appears in the workbench's provenance panel.

In fixture mode (this tranche), the tile `url_template` is a placeholder:
```
placeholder://tiles/gaia/osm-bounded/{z}/{x}/{y}.mvt
```

When live tile-serving is added (future tranche), the runner will replace this
with a real endpoint and set `fixture_mode: false` in the manifest.

---

## Policy

| Property | Value |
|----------|-------|
| Safety class | `bounded` |
| Network I/O | `false` (fixture mode) |
| Privileged | `false` |
| Promotion gate | `gaia-bounded-osm-fixture-validation` |
| Requires human review | `false` |
| Reproducibility target | `1.0` |

---

## Non-goals (this tranche)

- No unbounded live ingest.
- No production tile-serving.
- No privileged runtime admission.
- Route graph generation is explicitly deferred (`route_graph_status` field in receipts).

---

## Acceptance criteria

- [x] Manifest validates against ProphetArtifact contract shape
- [x] All 8 verbs execute successfully from a single `run_fixture.py` invocation
- [x] Outputs include provenance, attribution, checksums, and lineage
- [x] fixture_digest threads through all output documents
- [x] ODbL-1.0 license evidence preserved in every output
- [x] Deterministic metrics emitted for Delivery Excellence scoreboard
- [x] Sherlock/Holmes index payload emitted
- [x] Sociosphere registration payload emitted
