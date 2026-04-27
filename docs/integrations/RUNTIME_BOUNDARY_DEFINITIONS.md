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

Undecided. Candidate future entrypoint:

`control_tower/anomaly_score.py`

Required inputs:

- AssetHealthObservation;
- InventoryEvent / InventoryNodeRecord;
- RoutePlan / infrastructure evidence;
- mesh telemetry when relevant;
- policy bundle;
- model/runtime refs.

Current input examples:

- `fixtures/control-tower/navigation-asset-health-card.sample.v1.json`
- `fixtures/control-tower/work-order-candidate.rail-vegetation.sample.v1.json`
- `fixtures/control-tower/inventory-node.rail-maintenance-depot.sample.v1.json`
- `fixtures/control-tower/risk-exposure.rail-vegetation.sample.v1.json`

Emitted outputs:

- RiskExposureRecord;
- ControlTowerDecisionCard;
- WorkOrderCandidate;
- Sherlock result record;
- evidence/provenance refs.

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
- generated decision card and work-order candidate pass schema validation;
- Sherlock result emitted and validated;
- policy constraints are preserved.

Rollback semantics:

Demote generated decision cards/work-order candidates; preserve evidence trail and mark prior recommendations superseded.

Status:

Boundary is not yet ready for Lattice Forge mirroring. The executable scoring entrypoint and validation harness must be implemented first.

## Lattice Forge admission rule

A runtime may be mirrored into Lattice Forge only when:

1. this document has a reviewed boundary section for the runtime;
2. an executable entrypoint exists;
3. a validation command exists;
4. at least one fixture passes validation;
5. policy constraints and rollback semantics are explicit;
6. provenance and evidence outputs are named.

Until then, runtime references remain planning references only.
