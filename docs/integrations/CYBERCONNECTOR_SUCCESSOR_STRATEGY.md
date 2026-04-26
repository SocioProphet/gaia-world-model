# CyberConnector / COVALI Successor Strategy

Status: v0 successor strategy

## Upstream check

Target upstream: `CSISS/cc`

Checked fork: `SocioProphet/cc`

As of this integration pass, `SocioProphet/cc:master` is identical to `CSISS/cc:master` at commit `31b82de869772438147eb793be8cf5144dc400d8`.

The fork is not currently behind upstream. The issue is not fork staleness; the issue is architectural age and stack alignment.

## Decision

Do not make CyberConnector / COVALI the core Gaia runtime.

Use CyberConnector as a capability reference and migration source for EarthCube-era model-data comparison workflows. Build a Gaia-native successor aligned with the SocioProphet stack.

## Why CyberConnector is still valuable

CyberConnector/COVALI captures important capabilities:

- connecting Earth science data sources to models;
- comparing and validating atmospheric and Earth science model outputs;
- GRIB/NetCDF visualization;
- map-based data loading;
- statistics over points and lines;
- animation across time steps;
- regridding with ESMF/xESMF patterns;
- NCO-style operations over NetCDF variables;
- multi-perspective 2D/3D visualization.

Those are exactly the kinds of capabilities Gaia needs. The implementation stack is what should be modernized.

## Why not adopt it as-is

CyberConnector is centered on older deployment assumptions:

- Java/Tomcat web application packaging;
- ncWMS deployment dependency;
- Anaconda-side regridding setup;
- legacy Docker/Tomcat service model;
- UI/runtime assumptions outside the Gaia/SourceOS/Lattice/Sherlock/Lampstand architecture.

Gaia needs cloud-native, local-first, mesh-capable, provenance-backed, runtime-governed, searchable, agent-addressable geospatial computation.

## Successor name

Working name: **Gaia Model Validation Surface**.

This is the Gaia-native successor to CyberConnector/COVALI capabilities.

## Successor doctrine

```text
Earth science data/model asset
  -> Gaia catalog / STAC / data cube registration
  -> Lampstand local sampling when local
  -> Lattice Forge governed runtime
  -> Gaia model comparison / validation / regridding action
  -> Evidence report + map/coverage layer
  -> Sherlock discovery record
  -> OFIF context/event binding when field observations participate
```

## Core successor capabilities

### 1. Coverage/data-cube registration

Support modern and legacy scientific data formats:

- NetCDF;
- GRIB/GRIB2;
- Cloud Optimized GeoTIFF;
- Zarr;
- GeoParquet;
- STAC Items/Collections;
- OGC Coverages and coverage-like products.

### 2. Model comparison and validation

Provide reproducible comparison actions:

- model vs observation;
- model vs model;
- forecast vs later observation;
- field event vs satellite/reanalysis context;
- scenario branch vs baseline.

### 3. Regridding and spatial alignment

Modernize COVALI regridding into governed actions:

- source grid -> target grid;
- raster grid -> H3/S2/DGGS cells;
- EO/reanalysis grid -> OFIF field observation neighborhood;
- model output -> map/coverage tile layer.

### 4. Scientific operators

Replace ad hoc legacy tool invocation with governed process actions:

- averaging;
- binary operations;
- arithmetic expressions;
- clipping/subsetting;
- temporal aggregation;
- anomaly computation;
- statistics over points, lines, polygons, and H3 cell sets.

### 5. Evidence-first reports

Every comparison/validation action emits:

- input asset IDs;
- source hashes;
- runtime asset ID;
- parameters;
- spatial/temporal scope;
- model/version refs;
- metrics;
- uncertainty notes;
- provenance refs;
- handling tags;
- Sherlock discovery record.

### 6. Map and decision surfaces

Outputs should be usable as:

- MapLibre/Cesium/deck.gl layers;
- OGC API tiles/features/coverages/processes;
- Gaia decision cards;
- Sherlock searchable artifacts;
- Lattice Forge runtime-linked reports.

## Integration with existing stack

### Gaia

Owns catalog, data cube, validation semantics, evidence reports, world-state binding, and actions.

### OFIF

Provides field observations, custody state, adversarial confidence impacts, and local sensor evidence.

### Lampstand

Samples local NetCDF/GRIB/Zarr/COG/notebook/model-output files and emits governed `LocalStateRecord` / `PercolationEnvelope` records.

### Lattice Forge

Packages the runtime for regridding, validation, scientific operators, notebooks, and model comparison.

### Sherlock Search

Indexes model validation reports, coverage layers, decision cards, runtime assets, and local-state records.

## Migration from CyberConnector

Treat CyberConnector as a reference capability map:

| CyberConnector/COVALI capability | Gaia-native successor |
| --- | --- |
| GRIB/NetCDF add-data UI | Gaia coverage asset registration |
| UCAR/local data search | Sherlock + Gaia catalog search |
| Map visualization | Gaia map/coverage layer |
| Animation | Temporal coverage preview |
| Point/line statistics | Gaia coverage statistics action |
| Regridding | Gaia regrid action using Lattice runtime |
| NCO operations | Gaia scientific operator action |
| COVALI comparison | Gaia model validation report |
| Tomcat/ncWMS runtime | Lattice Forge runtime assets + OGC APIs |

## First implementation targets

1. `schemas/model-validation/model_validation_report.v1.schema.json`
2. `schemas/model-validation/regrid_run_manifest.v1.schema.json`
3. `docs/GAIA_MODEL_VALIDATION_SURFACE.md`
4. `fixtures/model-validation/soil-context-validation-report.sample.v1.json`
5. `fixtures/lattice/gaia-model-validation-runtime-asset.sample.v1.json`

## Non-goals

- Do not port the entire legacy Java/Tomcat app into Gaia.
- Do not make ncWMS the core rendering dependency.
- Do not rely on mutable ad hoc Anaconda environments for production workflows.
- Do not erase CyberConnector attribution or upstream provenance.

## Summary

CyberConnector is an important predecessor. Gaia should build the successor: a modern, provenance-first, runtime-governed, searchable, agent-addressable Earth science model validation surface.
