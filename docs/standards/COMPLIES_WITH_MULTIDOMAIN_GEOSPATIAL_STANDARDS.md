# Complies with Standards — Multi-Domain Geospatial Intelligence

Status: Draft implementation conformance

This GAIA implementation repository consumes the SocioProphet multi-domain geospatial standards package.

## Standards consumed

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/prophet-platform-standards/registry/multidomain-geospatial-standards-map.v1.json`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-storage/schemas/jsonschema/multidomain/multidomain_geospatial_record.v1.schema.json`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-standards-knowledge/schemas/jsonschema/multidomain/multidomain_geospatial_knowledge_artifact.v1.schema.json`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Implementation responsibility

`gaia-world-model` owns domain implementation schemas, fixtures, examples, and executable proofs for GAIA world-model capabilities.

GAIA implementation artifacts SHOULD reference the standards authority before being treated as stable.

## Required GAIA domain artifacts

- `SpaceAssetRecord`
- `TelemetryObservation`
- `EarthObservationProductRecord`
- `VesselTrackObservation`
- `AirTrackObservation`
- `SensorObservationEnvelope`
- `MultiDomainFusionEvent`
- `SensitiveGeoPolicyRecord`
- `MapLayerManifest`
- `RuntimeBoundaryEvidenceRecord`

## Promotion gate

A GAIA schema or fixture is draft until it references storage and knowledge standards. A GAIA runtime boundary is draft until it references the agent runtime standard and emits evidence/replay metadata.
