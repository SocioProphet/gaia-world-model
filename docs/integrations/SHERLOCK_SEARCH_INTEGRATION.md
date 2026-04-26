# Sherlock Search Integration for GAIA / OFIF / Lampstand / Lattice Forge

Status: v0 integration contract

## Purpose

Sherlock Search is the federated discovery surface for local, workspace, platform, and memory search. GAIA, OFIF, Lampstand, and Lattice Forge must publish search-ready records without collapsing their authority boundaries.

Current Sherlock platform contracts define normalized search results with source values such as `LAMPSTAND`, `PLATFORM`, `MEMORY`, and `MIXED`. GAIA and OFIF artifacts therefore enter Sherlock initially through platform-mediated records or Lampstand-local records, with a later schema extension for geospatial/event/model artifacts.

## Authority boundaries

| Capability | Authority |
| --- | --- |
| Local desktop/file sampling | Lampstand |
| Federated retrieval and ranking | Sherlock Search |
| World-state/evidence artifacts | GAIA |
| Field event envelopes | OFIF |
| Runtime/model/build artifacts | Lattice Forge |
| Workspace/platform permission boundary | prophet-platform |

## Indexing doctrine

Sherlock should index discovery records, not become the system of record.

Search records must retain:

- source artifact IDs;
- source system;
- authority owner;
- permission boundary;
- handling tags;
- provenance references;
- spatial/temporal keys where present;
- model/runtime references where present.

## Record families

### GAIA search record

GAIA publishes searchable records for:

- world-state features;
- evidence artifacts;
- map layers;
- model outputs;
- decision cards;
- reports;
- ontology bindings;
- spatial/temporal context packets.

### OFIF search record

OFIF publishes searchable records for:

- event envelopes;
- observation events;
- custody events;
- communications events;
- adversarial indicators;
- decision cards;
- derivation events.

### Lampstand search record

Lampstand publishes searchable records for approved local samples and local-state deltas.

### Lattice Forge search record

Lattice Forge publishes searchable records for runtime assets, lockfiles, SBOMs, model/runtime surfaces, build artifacts, and promotion evidence.

## Minimal adapter shape

Until Sherlock receives native geospatial/event/model entity types, GAIA bridge records should be emitted as `source=PLATFORM` or `source=MIXED` with `entity_type=DOCUMENT` and a canonical format such as:

- `gaia/world-state-feature+json`
- `gaia/evidence-artifact+json`
- `gaia/decision-card+json`
- `ofif/event-envelope+json`
- `lattice/runtime-asset+json`

## Recommended Sherlock schema extension

Add source values:

- `GAIA`
- `OFIF`
- `LATTICE_FORGE`

Add entity types:

- `WORLD_STATE_FEATURE`
- `EVIDENCE_ARTIFACT`
- `FIELD_EVENT`
- `OBSERVATION_EVENT`
- `DECISION_CARD`
- `MODEL_RUN`
- `MAP_LAYER`
- `RUNTIME_ASSET`
- `LOCAL_STATE_RECORD`

Add optional fields:

- `spatial_refs`
- `temporal_refs`
- `evidence_refs`
- `model_refs`
- `runtime_refs`
- `handling_tags`
- `provenance_refs`
- `authority_ref`

## Query examples

- "soil temperature confidence north field"
- "events in H3 cell 8928308280fffff"
- "custody warnings for soil probes"
- "show decision cards with calibration drift"
- "find runtime assets used by soil intelligence model"
- "local files that produced this GAIA evidence artifact"

## Security and governance

Sherlock must preserve permission boundaries. Indexability does not imply readability. Search result snippets must be redacted according to source handling tags and permission refs.

Search records should be treated as derived discovery metadata, not raw evidence. Raw evidence remains with GAIA, OFIF, Lampstand, or Lattice Forge depending on authority.
