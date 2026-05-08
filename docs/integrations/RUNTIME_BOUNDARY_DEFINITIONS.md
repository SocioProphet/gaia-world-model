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

Purpose: convert a GAIA artifact derived from an OFIF field observation plus EO/reanalysis context into a soil-intelligence fusion artifact.

Entrypoint: `scripts/soil_intelligence_fusion.py`

Required inputs:

- GAIA OFIF-derived world-state artifact;
- GAIA EO/reanalysis context fixture or data product;
- model/context metadata.

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

Rollback semantics: stop the local execution slice; no persistent external actuation exists in v0.

Status: executable proof exists, but not automatically admitted to Lattice Forge.

## Runtime 2 — GAIA navigation LiDAR feature runtime

Runtime name: `gaia-navigation-lidar-feature-runtime`

Domain: navigation and transportation infrastructure intelligence

Purpose: convert LiDAR / point-cloud corridor observations into infrastructure evidence features such as vegetation encroachment, clearance envelopes, rail/road segment condition, and map-ready derived features.

Entrypoint: `navigation/lidar_feature_extract.py`

Required inputs:

- LiDAR corridor observation;
- point-cloud asset reference;
- route/corridor geometry;
- model/config refs;
- policy constraints.

Current input examples:

- `fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json`
- `fixtures/navigation/lidar-derived-infrastructure-assets.sample.v1.json` as checked-in output fixture.

Emitted outputs:

- `gaia.navigation.lidar_feature_extract.output` artifact;
- TransportInfrastructureAsset-compatible records;
- LiDAR-derived rail-segment, vegetation, and clearance features;
- point-cloud source refs;
- H3 and linear-reference refs;
- provenance and confidence records;
- advisory safety status.

Schema references:

- `schemas/navigation/lidar_corridor_observation.v1.schema.json`
- `schemas/navigation/transport_infrastructure_asset.v1.schema.json`

Validation command:

```bash
python3 navigation/lidar_feature_extract.py \
  fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json \
  /tmp/lidar-derived-infrastructure-assets.json
```

Policy constraints:

- no safety-critical navigation claim without validation;
- preserve point-cloud source provenance;
- preserve acquisition platform/sensor calibration metadata;
- expose uncertainty and confidence;
- LiDAR-derived fixture outputs are advisory until a route validation record and safety case exist.

Runtime isolation default: container for fixture processing; VM/microVM when processing untrusted uploads or sensitive infrastructure data.

Network posture: restricted

Secret posture: none by default

Promotion criteria:

- executable entrypoint exists;
- fixture processing emits asset records with source refs;
- confidence and risk tags are preserved;
- advisory safety status is explicit;
- contract fixture CI passes;
- malformed point-cloud/input fixture corpus exists before production packaging.

Rollback semantics: derived features are versioned; rollback demotes the derived feature layer and restores prior corridor condition state. Original point-cloud observations remain immutable.

Status: executable proof exists for fixture input, but not automatically admitted to Lattice Forge. Lattice admission requires packaging, SBOM, signing, malformed-input tests, rollback tests, and safety-case boundary review.

## Runtime 3 — GAIA control tower anomaly runtime

Runtime name: `gaia-control-tower-anomaly-runtime`

Domain: open industrial IoT / supply-chain control tower

Purpose: score asset, inventory, route, and mesh observations for control-tower decision support. Emit risk exposure records, decision-card inputs, and work-order candidates.

Entrypoint: `control_tower/anomaly_score.py`

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

Rollback semantics: demote generated decision cards/work-order candidates; preserve evidence trail and mark prior recommendations superseded.

Status: executable proof exists, but not automatically admitted to Lattice Forge.

## Runtime 4 — GAIA OpenStreetMap ingestion runtime

Runtime name: `gaia-osm-ingestion-runtime`

Domain: OpenStreetMap / GAIA geospatial substrate

Purpose: ingest OpenStreetMap extracts or query results and emit GAIA OSMFeatureBinding records that preserve OSM identity, tags, attribution, and provenance.

Entrypoint: `geospatial/osm_ingest.py`

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

Validation command:

```bash
python3 geospatial/osm_ingest.py \
  fixtures/geospatial/osm-way-input.sample.v1.json \
  /tmp/osm-feature-bindings.json
```

Policy constraints:

- preserve OSM node/way/relation identity;
- preserve OSM tags as source metadata;
- carry OSM attribution and license refs;
- derived GAIA features must cite original OSM refs;
- OSM-derived route outputs are advisory unless separately validated.

Runtime isolation default: container

Network posture: restricted for local fixtures/extracts; explicitly declared if pulling live OSM/Overpass data.

Secret posture: none

Promotion criteria:

- executable entrypoint exists;
- at least one OSM input fixture maps to a valid OSMFeatureBinding-like output;
- attribution metadata is present;
- OSM refs are preserved;
- contract fixture CI passes.

Rollback semantics: demote generated OSM bindings and restore prior GAIA spatial binding set. Original OSM source records are never mutated.

Status: executable proof exists, but not automatically admitted to Lattice Forge.

## Runtime 5 — GAIA OpenStreetMap route graph runtime

Runtime name: `gaia-osm-route-graph-runtime`

Domain: OSM routing / navigation substrate

Purpose: convert OSM-derived topology into route graph artifacts usable by GAIA route plans and navigation/infrastructure intelligence.

Entrypoint: `geospatial/osm_route_graph.py`

Required inputs:

- OSMFeatureBinding record;
- route-mode configuration carried by binding routing field;
- access/restriction tag policy;
- safety/advisory policy.

Current input examples:

- `fixtures/geospatial/osm-road-feature-binding.sample.v1.json`
- `fixtures/geospatial/osm-route-graph.sample.v1.json` as checked-in output fixture.

Emitted outputs:

- OSMRouteGraphManifest;
- route topology refs;
- advisory route-plan inputs;
- provenance/attribution refs.

Schema references:

- `schemas/geospatial/osm_route_graph_manifest.v1.schema.json`

Validation command:

```bash
python3 geospatial/osm_route_graph.py \
  fixtures/geospatial/osm-road-feature-binding.sample.v1.json \
  /tmp/osm-route-graph.json
```

Policy constraints:

- OSM-only route graph output is advisory by default;
- HD or safety-critical routing requires LiDAR/field validation and safety-case records;
- OSM attribution must remain available in route outputs.

Runtime isolation default: container

Network posture: restricted

Secret posture: none

Promotion criteria:

- executable entrypoint exists;
- deterministic route graph fixture exists;
- OSM attribution preserved;
- route output safety status is explicit;
- contract fixture CI passes.

Rollback semantics: demote generated route graph and restore prior graph artifact; source OSM bindings remain immutable.

Status: executable proof exists, but not automatically admitted to Lattice Forge.

## Runtime 6 — GAIA OpenStreetMap tile export runtime

Runtime name: `gaia-osm-tile-export-runtime`

Domain: OSM-derived map/tile surfaces

Purpose: export OSM-derived GAIA spatial features into MapLibre-compatible map/tile layer manifests and tile artifacts.

Entrypoint: `geospatial/osm_tile_export.py`

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

Validation command:

```bash
python3 geospatial/osm_tile_export.py \
  fixtures/geospatial/osm-road-feature-binding.sample.v1.json \
  /tmp/osm-derived-map-tile-layer.json
```

Policy constraints:

- attribution must be present in tile layer manifests;
- generated layers must cite OSM source refs;
- no safety-critical navigation claim from map layer display alone.

Runtime isolation default: container

Network posture: restricted

Secret posture: none

Promotion criteria:

- executable entrypoint exists;
- deterministic tile layer manifest fixture exists;
- attribution text and license refs are present;
- Sherlock map-layer record validates;
- contract fixture CI passes.

Rollback semantics: demote generated tile layer and restore prior map layer manifest; source OSM bindings remain immutable.

Status: executable proof exists, but not automatically admitted to Lattice Forge.

## Runtime 7 — GAIA governed world-claim ingest runtime

Runtime name: `gaia-world-claim-ingest-runtime`

Domain: GAIA geospatial / governed world-model observations

Purpose: convert OSM feature extracts into governed GAIA WorldClaim bundles following the contracted ingest pipeline: `Observe -> Anchor -> Normalize -> Propose`. Emitted claims carry `policy_status=proposed` and must pass Holmes/Policy review before admission to world state or display on `/map`.

Entrypoint: `geospatial/world_claim_ingest.py`

Required inputs:

- OSM-like JSON fixture or OSM extract/query result;
- attribution and license metadata;
- H3 cell refs and geometry;
- classification metadata.

Current input examples:

- `fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json`

Emitted outputs:

- `gaia.world_claim_ingest.output` bundle;
- `WorldClaim` records (status=proposed);
- `SourceEvidence` records (one per feature);
- `FusionExplanation` traces (one per claim);
- `runtime_evidence` record with input/output hashes.

Schema references:

- `schemas/geospatial/world_claim.v1.schema.json`
- `schemas/geospatial/source_evidence.v1.schema.json`
- `schemas/geospatial/geo_anchor.v1.schema.json`
- `schemas/geospatial/fusion_explanation.v1.schema.json`
- `schemas/geospatial/vector_candidate.v1.schema.json`

Contract reference: `docs/contracts/GOVERNED_WORLD_CLAIM_CONTRACT.md`

Validation command:

```bash
python3 geospatial/world_claim_ingest.py \
  fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json \
  /tmp/gaia-world-claim-output.json
```

Deterministic output inspection:

```bash
python3 -c "
import json
with open('/tmp/gaia-world-claim-output.json') as f:
    d = json.load(f)
c = d['claims'][0]
assert c['policy_status']['status'] == 'proposed'
assert c['uncertainty']['confidence_score'] == 0.85
assert c['map_display']['display_layer'] == 'proposed_candidate'
assert d['evidence_records'][0]['source_type'] == 'osm'
assert d['explanation_traces'][0]['fusion_rule']['rule_class'] == 'single_source_passthrough'
print('All deterministic validation checks passed.')
"
```

Policy constraints:

- no autonomous actuation from proposed world claims;
- OSM-derived world claims are advisory until Holmes/Policy admits them;
- preserve OSM node/way/relation identity and ODbL-1.0 attribution;
- GeoAnchor required — claims without geometry are not emitted;
- SourceEvidence must carry attribution, temporal validity, and confidence score;
- ExplanationTrace must record the fusion rule applied;
- map_display.display_layer for proposed claims must be `proposed_candidate` with advisory label;
- VectorCandidates are `candidate_only` and must not influence claim status.

Runtime isolation default: container

Network posture: restricted for fixture mode; explicitly declared if pulling live OSM/Overpass data.

Secret posture: none

Promotion criteria:

- executable entrypoint exists;
- at least one OSM input fixture produces a valid WorldClaim output with all required fields;
- attribution and ODbL-1.0 license ref preserved in SourceEvidence;
- GeoAnchor binds each claim to a geometry with H3 cells and bbox;
- ExplanationTrace records single_source_passthrough rule;
- policy_status is `proposed` on all emitted claims;
- deterministic validation command passes;
- malformed-input corpus covers: missing required fields, invalid osm_type, wrong source, missing attribution.

Rollback semantics: demote generated world claims to `rejected` in policy record; preserve evidence trail and mark prior claims superseded. Original OSM source records are never mutated. GeoAnchor and SourceEvidence records remain immutable.

Status: executable proof exists, but not automatically admitted to Lattice Forge.

## Lattice Forge admission rule

A runtime may be mirrored into Lattice Forge only when:

1. this document has a reviewed boundary section for the runtime;
2. an executable entrypoint exists;
3. a validation command exists;
4. at least one fixture passes validation;
5. policy constraints and rollback semantics are explicit;
6. provenance and evidence outputs are named;
7. packaging, SBOM, signing, malformed-input tests, and rollback tests are reviewed.

Until then, runtime references remain planning references only.
