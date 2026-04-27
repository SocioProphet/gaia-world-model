# OpenStreetMap Runtime Admission Decision

Status: not admitted to Lattice Forge
Date: 2026-04-27
Owner surface: GAIA
Related platform surface: Prophet Platform OSM Map API

## Purpose

This document records the current Lattice Forge admission decision for the OpenStreetMap runtime family.

The OSM runtimes now have deterministic executable proofs in GAIA, but they are **not yet admitted** as Lattice Forge `RuntimeAsset` records.

## Decision

Do not add Lattice Forge RuntimeAssets yet for:

- `gaia-osm-ingestion-runtime`
- `gaia-osm-route-graph-runtime`
- `gaia-osm-tile-export-runtime`

## Why not admitted yet

The executable proofs are fixture-grade, not production-runtime-grade.

Current strengths:

- deterministic fixture input;
- deterministic output;
- CI validation;
- attribution preservation;
- OSM source identity preservation;
- advisory routing status;
- runtime boundary documentation.

Remaining admission gaps:

- no packaged runtime lockfile;
- no SBOM;
- no signed artifact;
- no production input adapters for PBF, Overpass, or region extracts;
- no performance limits or memory profile;
- no failure-mode matrix for malformed OSM data;
- no runtime promotion/rollback test;
- no strict cross-repo workspace attribution validation yet;
- no Lattice Forge packaging review.

## Runtime-by-runtime state

### `gaia-osm-ingestion-runtime`

Current state: executable proof.

Entrypoint:

```bash
python3 geospatial/osm_ingest.py \
  fixtures/geospatial/osm-way-input.sample.v1.json \
  /tmp/osm-feature-bindings.json
```

Admission state: not admitted.

Required before admission:

- define supported production input formats;
- define fixture and malformed-input corpus;
- add package lockfile;
- add SBOM generation plan;
- add signed artifact strategy;
- add Lattice RuntimeAsset fixture only after packaging review.

### `gaia-osm-route-graph-runtime`

Current state: executable proof.

Entrypoint:

```bash
python3 geospatial/osm_route_graph.py \
  fixtures/geospatial/osm-road-feature-binding.sample.v1.json \
  /tmp/osm-route-graph.json
```

Admission state: not admitted.

Required before admission:

- define route graph semantics beyond single-feature fixture;
- define advisory/validated/not-for-navigation transition rules;
- define safety-case dependency for validated routing;
- add malformed and restricted access-tag tests;
- add Lattice RuntimeAsset only after route safety boundary review.

### `gaia-osm-tile-export-runtime`

Current state: executable proof.

Entrypoint:

```bash
python3 geospatial/osm_tile_export.py \
  fixtures/geospatial/osm-road-feature-binding.sample.v1.json \
  /tmp/osm-derived-map-tile-layer.json
```

Admission state: not admitted.

Required before admission:

- define tile artifact output format and storage contract;
- define MapLibre style/version contract;
- define attribution preservation tests for exports and reports;
- add packaging and SBOM plan;
- add Lattice RuntimeAsset only after artifact contract review.

## Minimum admission checklist

A runtime may be admitted to Lattice Forge only after:

1. executable entrypoint exists;
2. validation command exists;
3. production input/output scope is defined;
4. fixture corpus includes success and failure cases;
5. attribution/source preservation tests pass;
6. safety/advisory status handling is tested;
7. packaging lockfile exists;
8. SBOM plan exists;
9. signed artifact strategy exists;
10. rollback semantics are tested;
11. SocioSphere source-exposure and attribution governance pass;
12. Lattice Forge RuntimeAsset fixture is reviewed before merge.

## Immediate next step

Open a Lattice Forge tracking issue requesting admission review criteria, not a runtime asset.

The issue should reference this decision document and the GAIA executable proofs.
