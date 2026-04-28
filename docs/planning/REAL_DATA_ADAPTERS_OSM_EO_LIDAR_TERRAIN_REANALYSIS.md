# Real-Data Adapter Planning: OSM, EO, LiDAR, Terrain, and Reanalysis

Status: v0 planning contract
Scope: GAIA world-model data adapters

## Purpose

This document defines the minimum contract for moving from fixture-backed GAIA geospatial demos toward real data adapters.

It does not implement live ingestion. It does not approve production navigation. It does not admit any Lattice RuntimeAsset.

The current GAIA `/map` workbench and OSM Map API are fixture/API-backed proof slices. This document states what must exist before those proof slices become production ingestion, production fusion, or runtime-admitted services.

## Current fixture-backed baseline

The current validated fixture families include:

- OSM feature binding: `fixtures/geospatial/osm-road-feature-binding.sample.v1.json`
- OSM-derived map tile layer manifest: `fixtures/geospatial/osm-derived-map-tile-layer.sample.v1.json`
- OSM route graph manifest: `fixtures/geospatial/osm-route-graph.sample.v1.json`
- LiDAR corridor observation: `fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json`
- LiDAR-derived infrastructure assets: `fixtures/navigation/lidar-derived-infrastructure-assets.sample.v1.json`
- LiDAR advisory safety case: `fixtures/navigation/navigation-safety-case.lidar-advisory.sample.v1.json`
- LiDAR runtime rollback plan: `fixtures/navigation/lidar-runtime-rollback-plan.sample.v1.json`
- Soil / EO context: `fixtures/gaia/context/soil-eo-context.sample.v1.json`
- Mesh and control-tower fixtures used by the multi-domain validation lanes.

These fixtures are proof artifacts, not production data products.

## Adapter family 1: OpenStreetMap

### Candidate sources

- OSM PBF regional extracts
- Overpass API query output
- OSM diff/update streams
- Curated internal OSM-derived extracts

### Minimum source envelope

Every OSM adapter output must preserve:

- OSM element type: node, way, relation
- OSM element ID
- source extract or query reference
- timestamp or replication sequence where available
- tags used by the adapter
- geometry reference and CRS
- attribution text
- license reference
- provenance source refs

### Required output products

- OSM feature binding compatible with `osm_feature_binding.v1`
- optional map tile layer manifest compatible with `map_tile_layer_manifest.v1`
- optional advisory route graph compatible with `osm_route_graph_manifest.v1`

### Required validation before production use

- schema validation for the binding output
- attribution preservation check
- provenance/source-ref preservation check
- geometry validity check
- H3/cell assignment check where H3 indexing is emitted
- advisory route-safety check for any graph product

### Explicit blockers

OSM topology alone must never be treated as safety-critical routing authority.

A production OSM ingestion adapter must not bypass attribution or provenance requirements.

## Adapter family 2: satellite and EO products

### Candidate sources

- vegetation indices such as NDVI/EVI from Sentinel or Landsat families
- land-surface temperature products from MODIS, VIIRS, Landsat, or equivalent
- soil-moisture products such as SMAP or fused products
- cloud masks and data-quality bands
- multispectral or hyperspectral products where licensing permits

### Minimum source envelope

Every EO adapter output must include:

- provider or mission family
- product ID or collection ID
- acquisition time
- processing time where available
- spatial resolution
- temporal resolution or revisit interval
- CRS and grid/tile reference
- uncertainty or quality flags where available
- cloud/quality mask reference where relevant
- license/access constraints
- provenance source refs

### Required output products

- EO context record for fusion workflows
- quality mask / uncertainty metadata
- spatial indexing compatible with the GAIA map and evidence layers
- temporal validity window

### Required validation before production use

- CRS/grid normalization check
- temporal validity check
- missing-data and cloud-mask handling
- uncertainty/quality flag propagation
- provenance/source-ref preservation
- license/access check

### Explicit blockers

EO products must not be fused into operational recommendations without quality/uncertainty propagation.

Fixture weighted baselines must not be represented as calibrated models.

## Adapter family 3: LiDAR and point-cloud products

### Candidate sources

- COPC
- LAZ/LAS
- tiled point-cloud datasets
- derived corridor or infrastructure observations
- provider-specific point-cloud feeds where licensing permits

### Minimum source envelope

Every LiDAR adapter output must include:

- source asset ID
- acquisition time or survey time
- processing time where available
- CRS and vertical datum
- point density or resolution metadata where available
- classification codes used
- confidence/quality metrics where available
- calibration references where available
- provenance source refs
- integrity/hash references for large assets

### Required output products

- LiDAR corridor observation compatible with the existing navigation fixture family
- derived infrastructure asset output where feature extraction occurs
- advisory safety case if the output is used for navigation-adjacent workflows
- rollback/demotion plan for derived runtime outputs

### Required validation before production use

- malformed-input corpus
- CRS/vertical-datum validation
- calibration metadata preservation
- feature extraction reproducibility check
- advisory safety-case validation
- rollback/demotion execution proof

### Explicit blockers

LiDAR-derived features are advisory until validation, approval, and operator boundary documents exist.

No LiDAR runtime may be admitted to Lattice without executable entrypoint, validation command, rollback plan, fixture proof, and reviewed runtime boundary.

## Adapter family 4: DEM, terrain, and hydrology context

### Candidate sources

- DEM products
- slope/aspect derivatives
- terrain roughness products
- hydrology and drainage derivatives
- landform classification products

### Minimum source envelope

Every terrain adapter output must include:

- source DEM/product ID
- resolution
- CRS and vertical datum
- derivative method where relevant
- temporal validity or survey date
- uncertainty or quality flags where available
- provenance source refs
- license/access constraints

### Required output products

- terrain context record
- slope/aspect/roughness derivatives where used by downstream fusion
- spatial indexing compatible with GAIA map/evidence surfaces

### Required validation before production use

- resolution compatibility check
- CRS/vertical-datum validation
- derivative reproducibility check
- uncertainty/quality propagation
- provenance/source-ref preservation

### Explicit blockers

Terrain derivatives must not silently override higher-confidence local observations.

Terrain context used in navigation or infrastructure workflows requires advisory boundary language until validated.

## Adapter family 5: weather and reanalysis products

### Candidate sources

- ERA5 / ERA5-Land style reanalysis
- forecast grids
- station observations
- radar/precipitation products
- soil-temperature and surface-energy context products

### Minimum source envelope

Every weather/reanalysis adapter output must include:

- provider/product ID
- issue time
- valid time
- forecast horizon where applicable
- spatial resolution and grid reference
- variable names and units
- quality flags where available
- uncertainty where available
- provenance source refs
- license/access constraints

### Required output products

- weather/reanalysis context record
- temporal validity window
- unit-normalized fields for downstream fusion
- spatial indexing compatible with GAIA evidence surfaces

### Required validation before production use

- unit normalization check
- valid-time and forecast-horizon check
- temporal alignment with observations
- uncertainty/quality propagation
- provenance/source-ref preservation

### Explicit blockers

Forecast/reanalysis products must not be used as ground truth without explicitly marking their model or forecast status.

## Cross-adapter fusion requirements

Any fusion pipeline combining OSM, EO, LiDAR, terrain, weather, or field observations must preserve:

- source refs for every component input
- product-level provenance
- temporal validity windows
- spatial resolution and CRS metadata
- uncertainty/quality fields
- license/attribution constraints
- advisory or validated safety status
- fallback behavior when one source family is absent

Fusion outputs must identify whether they are:

- fixture-backed demo output
- heuristic baseline
- calibrated model output
- validated operational output

Only the final category may be considered for operational use, and only after validation and approval boundaries exist.

## Safety and decision boundaries

The following are blocked until explicitly implemented and validated:

- safety-critical navigation
- dispatch authority
- live route guidance
- automated infrastructure work-order execution without approval
- Lattice RuntimeAsset admission for ingestion/fusion runtimes
- production tile serving from live OSM/EO/LiDAR products

Any advisory output must include prohibited-use language where it touches navigation, infrastructure, or operational decision workflows.

## Lattice RuntimeAsset admission prerequisites

No real-data adapter runtime is admission-ready until the owning domain repo provides:

1. executable runtime entrypoint;
2. validation command;
3. at least one passing fixture;
4. policy constraints;
5. rollback or demotion semantics;
6. reviewed runtime boundary;
7. provenance and evidence output definition;
8. failure-mode documentation;
9. source-exposure and license posture;
10. SocioSphere readiness registration.

## Minimum validation lane additions before production adapters

Future production adapters should add validation lanes for:

- OSM source ingestion and attribution preservation
- OSM diff/update replay
- EO context product validation
- LiDAR point-cloud input hardening
- terrain derivative reproducibility
- weather/reanalysis temporal/unit normalization
- cross-source fusion uncertainty propagation
- fallback/degradation behavior

## Implementation posture

This document intentionally stops before implementation.

The next implementation-safe step is to add schemas and fixtures for each adapter family, not to add live ingestion.

The first live-ingestion candidate should be selected only after the schema, fixture, validation, and governance lane exist.
