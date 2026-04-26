# GAIA ↔ OFIF Integration

Status: v0 integration contract

## Purpose

This document defines how GAIA World Model integrates with the Orion Field Intelligence Framework (OFIF).

GAIA owns the world model: geospatial substrate, ontology integration, evidence graph, data cube, simulation, map surfaces, and policy-constrained actions.

OFIF owns field intelligence: event envelopes, observation schemas, sensor fusion primitives, field custody, communications state, adversarial indicators, and decision-card evidence discipline.

The integration rule is simple:

**OFIF tells GAIA what happened in the field. GAIA tells OFIF what that means in the world.**

## Authority boundaries

| Domain | System of record |
| --- | --- |
| Field event envelope | OFIF |
| Sensor observation schema | OFIF |
| Custody/comms/adversarial primitives | OFIF |
| Canonical world entity identity | GAIA |
| Geospatial substrate and spatial joins | GAIA |
| Satellite/remote-sensing data cube | GAIA |
| Forecasts, simulations, and scenario branches | GAIA |
| Map/tile surfaces | GAIA |
| Evidence/provenance graph | Shared, GAIA canonicalizes |

## Integration flow

1. OFIF emits a signed or hash-addressed event envelope.
2. GAIA validates the envelope and payload schema.
3. GAIA maps the event to spatial, temporal, and ontology bindings.
4. GAIA creates or updates a world-state feature, evidence node, or action candidate.
5. GAIA links source event IDs, model versions, derivation steps, and confidence metadata.
6. GAIA exposes the result through catalog, map, process, report, and agent APIs.

## Required mappings

The bridge must support these initial mappings:

| OFIF object | GAIA target |
| --- | --- |
| ObservationEvent | ObservationFeature / EvidenceObservation |
| EventEnvelope.provenance | EvidenceLineageNode |
| EventEnvelope.integrity | EvidenceIntegrityRecord |
| EventEnvelope.classification | DataHandlingPolicyBinding |
| EventEnvelope.adversarial | ConfidenceAdjustment / ThreatIndicator |
| location.h3_cell | SpatialIndexCell |
| location.lat/lon | GeometryPoint |
| environment | EnvironmentalContextObservation |
| media | MediaEvidenceAsset |
| detections | DetectedEntityObservation |
| link_state | CommunicationsAvailabilityObservation |
| custody_state | AssetCustodyObservation |

## Spatial semantics

H3 is the first shared spatial key between OFIF and GAIA. GAIA may also bind an event to WGS84 geometry, OSM features, parcels, facilities, watersheds, administrative units, STAC item footprints, raster grid cells, or simulation meshes.

The bridge must preserve original OFIF coordinates and H3 cell values. Derived spatial joins must be represented as GAIA derivations, not mutations of the original event.

## Temporal semantics

`observed_at` is the field observation time. `ingested_at` is the ingestion time. GAIA-derived timestamps must not overwrite OFIF timestamps. Forecasts, simulations, and backfilled enrichments must carry their own run IDs and validity intervals.

## Confidence and adversarial semantics

GAIA must not treat OFIF events as neutral facts. Every observation may carry custody risk, communication degradation, replay risk, calibration risk, deception risk, or model-confidence impact.

The first confidence model is additive and conservative:

- preserve OFIF confidence values;
- preserve adversarial confidence impact;
- record derived confidence as a GAIA enrichment;
- never erase the raw event confidence;
- always expose evidence IDs and model version IDs on decision cards.

## Data products

The first integrated products are:

1. Live field observation layer.
2. Sensor and gateway health layer.
3. Custody/tamper layer.
4. Communications availability layer.
5. Adversarial indicator layer.
6. Soil intelligence layer that fuses satellite/reanalysis data with OFIF local field observations.

## Soil intelligence use case

The flagship integration demo should predict or estimate soil state using both broad Earth-observation context and local OFIF observations.

GAIA inputs:

- satellite land-surface temperature;
- soil moisture products;
- weather/reanalysis;
- vegetation indices;
- elevation, slope, aspect;
- soil taxonomy;
- land cover;
- precipitation and snow/irrigation indicators.

OFIF inputs:

- local temperature/moisture observations;
- camera or multimodal detections;
- gateway link state;
- custody/tamper state;
- calibration version;
- signed observation envelopes.

Outputs:

- estimated soil temperature and/or moisture;
- depth band when available;
- forecast horizon;
- uncertainty interval;
- confidence mask;
- map layer;
- decision card with evidence IDs, model IDs, and provenance.

## Implementation artifacts

Required follow-on artifacts:

- `contracts/mappings/ofif-to-gaia.v1.json`
- `contracts/mappings/gaia-to-ofif-context.v1.json`
- `gaia/ontology/imports/ofif.yaml`
- OFIF `ontology/gaia-bindings.ttl`
- bridge validation tests
- one end-to-end demo event converted into a GAIA world-state feature

## Non-goals

- OFIF does not become the canonical Earth ontology.
- GAIA does not replace OFIF event contracts.
- The bridge must not silently coerce defensive/adversarial context into operational attack guidance.
- Raw field events must remain auditable and attributable.
