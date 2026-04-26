# Lattice Forge Integration for GAIA / OFIF / Lampstand / Sherlock

Status: v0 integration contract

## Purpose

Lattice Forge is the governed runtime and package distribution surface for reproducible Prophet Lattice work. GAIA uses Lattice Forge when geospatial, field-intelligence, model, notebook, and bridge artifacts must become reproducible runtime assets.

GAIA and OFIF produce evidence and model artifacts. Lampstand samples local state. Sherlock discovers records. Lattice Forge packages the reproducible runtime boundary that makes those artifacts rebuildable, promotable, and auditable.

## Authority boundaries

| Domain | Authority |
| --- | --- |
| Runtime closure and build provenance | Lattice Forge |
| Local file/state sampling | Lampstand |
| Field event envelope | OFIF |
| World model/evidence/simulation | GAIA |
| Search/discovery | Sherlock Search |

## Integration doctrine

A GAIA/OFIF/Lampstand artifact graduates to Lattice Forge when it must be reproducible as a runtime, model, feature pipeline, notebook, or execution image.

```text
GAIA/OFIF/Lampstand artifact
  -> reproducibility requirement
  -> Lattice Forge RuntimeAsset or SurfaceRecord
  -> SBOM / lockfile / signature / scan / promotion evidence
  -> Sherlock searchable discovery record
  -> GAIA evidence links back to runtime provenance
```

## Initial runtime assets

The first GAIA + OFIF Lattice Forge assets should be:

1. `gaia-ofif-bridge-runtime`
   - Runs OFIF event validation and GAIA bridge transforms.
2. `gaia-soil-intelligence-baseline-runtime`
   - Runs the v0 soil-intelligence fusion pipeline.
3. `gaia-geospatial-notebook-runtime`
   - Notebook environment for EO/context analysis and decision-card review.
4. `gaia-sherlock-index-export-runtime`
   - Emits Sherlock-compatible search/discovery records.

## Required provenance links

Every Lattice Forge runtime used by GAIA must link:

- runtime asset ID;
- runtime version;
- source refs;
- lockfile refs;
- SBOM digest;
- signature digest;
- scan status;
- promotion channel;
- rollback ref;
- compatible surfaces.

GAIA model runs and decision cards must be able to cite the runtime asset that produced them.

## Runtime policy defaults

For GAIA + OFIF bridge runtimes:

- network: restricted;
- secrets: none or scoped;
- accelerators: CPU by default;
- default isolation: container for dev, VM/microVM for sensitive field or private data;
- telemetry: build-duration, artifact-size, scan-duration, promotion-result.

## Sherlock integration

Lattice Forge runtime assets should be emitted into Sherlock discovery as `RUNTIME_ASSET` records with:

- runtime name/version;
- model or pipeline purpose;
- compatible surfaces;
- promotion channel;
- provenance refs;
- GAIA/OFIF artifact refs;
- SBOM/scan/signature refs.

## Lampstand integration

Lampstand can sample local runtime/build artifacts before they become promoted Lattice Forge assets. Examples:

- local flake files;
- notebooks;
- model outputs;
- lockfiles;
- generated features;
- scan reports;
- artifact bundles.

A Lampstand `LocalStateRecord` can percolate into a Lattice Forge RuntimeAsset only after policy approval and reproducibility checks.

## Non-goals

- Lattice Forge does not own GAIA world-state semantics.
- Lattice Forge does not own OFIF field-event semantics.
- Runtime availability does not imply data access permission.
- Reproducibility metadata must not leak sensitive local paths or raw field data.
