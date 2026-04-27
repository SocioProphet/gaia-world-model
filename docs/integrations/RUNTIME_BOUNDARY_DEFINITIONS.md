# Runtime Boundary Definitions

Status: v0 boundary gate
Date: 2026-04-27

## Purpose

This document defines the gate that must be crossed before any GAIA domain runtime is mirrored into Lattice Forge as a `RuntimeAsset`.

Lattice Forge owns reproducible runtime provenance. It should not receive speculative fixtures until the runtime has a clear executable boundary.

## Required boundary fields

Every runtime boundary must define:

- runtime name;
- owning domain;
- purpose;
- entrypoint;
- required inputs;
- emitted outputs;
- schema references;
- policy constraints;
- expected evidence artifacts;
- runtime isolation default;
- network posture;
- secret posture;
- validation command;
- promotion criteria;
- rollback semantics.

## Runtime 1 — GAIA soil intelligence baseline runtime

Runtime name: `gaia-soil-intelligence-baseline-runtime`

Domain: GAIA + OFIF soil intelligence

Purpose:

Convert a GAIA artifact derived from an OFIF field observation plus EO/reanalysis context into a soil-intelligence fusion artifact.

Entrypoint:

`scripts/soil_intelligence_fusion.py`

Required inputs:

- GAIA OFIF-derived world-state artifact;
- GAIA EO/reanalysis context fixture or data product;
- model/context metadata.

Required input examples:

- `/tmp/gaia-ofif-output.json`
- `fixtures/gaia/context/soil-eo-context.sample.v1.json`

Emitted outputs:

- `gaia.soil_intelligence.fusion.v0` artifact;
- confidence record;
- evidence refs;
- policy constraints.

Validation command:

```bash
python3 scripts/ofif_to_gaia_bridge.py \
  fixtures/ofif/observation-event.sample.v1.json \
  /tmp/gaia-ofif-output.json

python3 scripts/soil_intelligence_fusion.py \
  /tmp/gaia-ofif-output.json \
  fixtures/gaia/context/soil-eo-context.sample.v1.json \
  /tmp/gaia-soil-fusion-output.json
```

Policy constraints:

- no autonomous actuation;
- fixture output is not agronomic advice;
- preserve OFIF raw event provenance;
- preserve model/context refs.

Runtime isolation default: container

Network posture: restricted

Secret posture: none

Promotion criteria:

- bridge invariant checks pass;
- soil fusion emits required fields;
- fixture validation CI passes;
- runtime boundary reviewed.

Rollback semantics:

Stop the local execution slice; no persistent external actuation exists in v0.

## Runtime 2 — GAIA navigation LiDAR feature runtime

Runtime name: `gaia-navigation-lidar-feature-runtime`

Domain: navigation and transportation infrastructure intelligence

Purpose:

Convert LiDAR / point-cloud corridor observations into infrastructure evidence features such as vegetation encroachment, clearance envelopes, rail/road segment condition, and map-ready derived features.

Entrypoint:

Undecided. Candidate future entrypoint:

`navigation/lidar_feature_extract.py`

Required inputs:

- LiDAR corridor observation;
- point-cloud asset reference;
- route/corridor geometry;
- model/config refs;
- policy constraints.

Required input examples:

- `fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json`

Emitted outputs:

- transport infrastructure asset records;
- LiDAR-derived feature records;
- clearance/vegetation risk evidence;
- map/tile/point-cloud derived feature refs;
- provenance and confidence records.

Policy constraints:

- no safety-critical navigation claim without validation;
- preserve point-cloud source provenance;
- preserve acquisition platform/sensor calibration metadata;
- expose uncertainty and accuracy.

Runtime isolation default: container for fixture processing; VM/microVM when processing untrusted uploads or sensitive infrastructure data.

Network posture: restricted

Secret posture: none by default

Promotion criteria:

- executable entrypoint exists;
- fixture processing emits schema-valid infrastructure features;
- confidence and uncertainty fields are present;
- safety caveats are emitted for route-facing outputs.

Rollback semantics:

Derived features are versioned; rollback means demote derived feature layer and restore prior corridor condition state.

Status:

Boundary is not yet ready for Lattice Forge mirroring. Entrypoint and emitted feature schemas need implementation.

## Runtime 3 — GAIA control tower anomaly runtime

Runtime name: `gaia-control-tower-anomaly-runtime`

Domain: open industrial IoT / supply-chain control tower

Purpose:

Score asset, inventory, route, and mesh observations for control-tower decision support. Emit risk exposure records, decision-card inputs, and work-order candidates.

Entrypoint:

`control_tower/anomaly_score.py`

Required inputs:

- ControlTowerDecisionCard fixture or generated decision-card input;
- asset health evidence refs;
- route or infrastructure evidence refs;
- policy bundle refs.

Current input examples:

- `fixtures/control-tower/navigation-asset-health-card.sample.v1.json`
- `fixtures/control-tower/work-order-candidate.rail-vegetation.sample.v1.json`
- `fixtures/control-tower/inventory-node.rail-maintenance-depot.sample.v1.json`
- `fixtures/control-tower/risk-exposure.rail-vegetation.sample.v1.json`

Emitted outputs:

- `gaia.control_tower.anomaly_score.output` bundle;
- RiskExposureRecord;
- WorkOrderCandidate;
- evidence/provenance refs;
- approval-required policy state.

Validation command:

```bash
python3 control_tower/anomaly_score.py \
  fixtures/control-tower/navigation-asset-health-card.sample.v1.json \
  /tmp/control-tower-anomaly-output.json
```

Policy constraints:

- decision cards are advisory unless explicit approval exists;
- work orders require human approval by default;
- safety-critical navigation or infrastructure restrictions require operator validation;
- inventory/search visibility does not imply access to restricted data.

Runtime isolation default: container for fixtures; VM/microVM when using sensitive operational data.

Network posture: restricted

Secret posture: none by default

Promotion criteria:

- executable entrypoint exists;
- risk score emitted from deterministic input fixture;
- generated risk and work-order candidate structures are present;
- policy constraints are preserved;
- contract fixture CI passes.

Rollback semantics:

Demote generated decision cards/work-order candidates; preserve evidence trail and mark prior recommendations superseded.

Status:

Boundary is now executable but not automatically admitted to Lattice Forge. It requires an explicit admission decision before a Lattice RuntimeAsset is added.

## Runtime 4 — GAIA OpenStreetMap ingestion runtime

Runtime name: `gaia-osm-ingestion-runtime`

Domain: OpenStreetMap / GAIA geospatial substrate

Purpose:

Ingest OpenStreetMap extracts or query results and emit GAIA OSMFeatureBinding records that preserve OSM identity, tags, attribution, and provenance.

Entrypoint:

`geospatial/osm_ingest.py`

Required inputs:

- OSM-like JSON fixture or future OSM extract/query result;
- extract metadata;
- attribution/license metadata;
- H3 cell refs or future H3 indexing output;
- target GAIA entity-type mapping derived from tags.

Current input examples:

- `fixtures/geospatial/osm-way-input.sample.v1.json`
- `fixtures/geospatial/osm-road-feature-binding.sample.v1.json` as target fixture.

Emitted outputs:

- `gaia.osm_ingestion.output` artifact;
- OSMFeatureBinding records;
- GAIA spatial/entity refs;
- H3 cell refs;
- attribution metadata;
- provenance refs;
- advisory routing policy marker.

Schema references:

- `schemas/geospatial/osm_feature_binding.v1.schema.json`

Policy constraints:

- preserve OSM node/way/relation identity;
- preserve OSM tags as source metadata;
- carry OSM attribution and license refs;
- derived GAIA features must cite original OSM refs;
- OSM-derived route outputs are advisory unless separately validated.

Runtime isolation default: container

Network posture: restricted for local fixtures/extracts; explicitly declared if pulling live OSM/Overpass data.

Secret posture: none

Validation command:

```bash
python3 geospatial/osm_ingest.py \
  fixtures/geospatial/osm-way-input.sample.v1.json \
  /tmp/osm-feature-bindings.json
```

Promotion criteria:

- executable entrypoint exists;
- at least one OSM input fixture maps to a valid OSMFeatureBinding-like output;
- attribution metadata is present;
- OSM refs are preserved;
- contract fixture CI passes.

Rollback semantics:

Demote generated OSM bindings and restore prior GAIA spatial binding set. Original OSM source records are never mutated.

Status:

Boundary is executable for fixture input but not automatically admitted to Lattice Forge. A Lattice RuntimeAsset requires explicit admission decision after reviewing packaging, input format support, and validation command stability.

## Runtime 5 — GAIA OpenStreetMap route graph runtime

Runtime name: `gaia-osm-route-graph-runtime`

Domain: OSM routing / navigation substrate

Purpose:

Convert OSM-derived topology into route graph artifacts usable by GAIA route plans and navigation/infrastructure intelligence.

Entrypoint:

Undecided. Candidate future entrypoint:

`geospatial/osm_route_graph.py`

Required inputs:

- OSMFeatureBinding records;
- route-mode configuration;
- access/restriction tag policy;
- optional GTFS/NeTEx transfer bindings;
- safety/advisory policy.

Current input examples:

- `fixtures/geospatial/osm-road-feature-binding.sample.v1.json`
- `fixtures/navigation/multimodal-route-plan.sample.v1.json`

Emitted outputs:

- route graph manifest;
- route topology refs;
- advisory route-plan inputs;
- provenance/attribution refs.

Policy constraints:

- OSM-only route graph output is advisory by default;
- HD or safety-critical routing requires LiDAR/field validation and safety-case records;
- OSM attribution must remain available in route outputs.

Runtime isolation default: container

Network posture: restricted

Secret posture: none

Validation command:

Undecided.

Promotion criteria:

- executable entrypoint exists;
- deterministic route graph fixture exists;
- OSM attribution preserved;
- route output safety status is explicit.

Rollback semantics:

Demote generated route graph and restore prior graph artifact; source OSM bindings remain immutable.

Status:

Boundary is not yet ready for Lattice Forge mirroring.

## Runtime 6 — GAIA OpenStreetMap tile export runtime

Runtime name: `gaia-osm-tile-export-runtime`

Domain: OSM-derived map/tile surfaces

Purpose:

Export OSM-derived GAIA spatial features into MapLibre-compatible map/tile layer manifests and tile artifacts.

Entrypoint:

Undecided. Candidate future entrypoint:

`geospatial/osm_tile_export.py`

Required inputs:

- OSMFeatureBinding records;
- GAIA spatial features;
- style/layer configuration;
- attribution metadata;
- tile output configuration.

Current input examples:

- `fixtures/geospatial/osm-road-feature-binding.sample.v1.json`
- `fixtures/geospatial/osm-derived-map-tile-layer.sample.v1.json`

Emitted outputs:

- MapTileLayerManifest records;
- MapLibre style/layer refs;
- tile artifact refs;
- attribution/source refs;
- Sherlock discoverable map-layer refs.

Schema references:

- `schemas/geospatial/map_tile_layer_manifest.v1.schema.json`

Policy constraints:

- attribution must be present in tile layer manifests;
- generated layers must cite OSM source refs;
- no safety-critical navigation claim from map layer display alone.

Runtime isolation default: container

Network posture: restricted

Secret posture: none

Validation command:

Current fixture-level validation:

```bash
python3 scripts/validate_contract_fixtures.py
```

Promotion criteria:

- executable entrypoint exists;
- deterministic tile layer manifest fixture exists;
- attribution text and license refs are present;
- Sherlock map-layer record validates.

Rollback semantics:

Demote generated tile layer and restore prior map layer manifest; source OSM bindings remain immutable.

Status:

Boundary is not yet ready for Lattice Forge mirroring.

## Lattice Forge admission rule

A runtime may be mirrored into Lattice Forge only when:

1. this document has a reviewed boundary section for the runtime;
2. an executable entrypoint exists;
3. a validation command exists;
4. at least one fixture passes validation;
5. policy constraints and rollback semantics are explicit;
6. provenance and evidence outputs are named.

Until then, runtime references remain planning references only.
