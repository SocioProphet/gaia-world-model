# Runtime Boundary — GAIA SensorThings Ingest

Status: executable fixture proof; Lattice admission candidate, not admitted
Date: 2026-04-27

## Runtime identity

Runtime name: `gaia-sensorthings-ingest-runtime`

Domain: GAIA field sensor / SensorThings observation ingestion

Purpose: convert a SensorThings-like observation fixture into a standards-bound `SensorObservationEnvelope` while preserving sensor identity, platform reference, observed properties, geometry, measurements, source attribution, provenance, runtime evidence, and sensitive-geospatial governance metadata.

## Standards references

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Entrypoint

`multidomain/sensorthings_ingest.py`

## Required inputs

- SensorThings-like observation JSON fixture.
- Feed reference.
- Sensor identity, sensor type, and platform reference.
- Observed properties.
- Observation time, geometry reference, measurements, and quality.
- Attribution and license metadata.
- Sensitive geospatial classification reference.

Current fixture:

- `fixtures/multidomain/sensorthings-observation-input.sample.v1.json`

Negative fixtures:

- `fixtures/multidomain/negative/sensorthings-observation-wrong-source.sample.v1.json`
- `fixtures/multidomain/negative/sensorthings-observation-bad-lat.sample.v1.json`

## Emitted outputs

- `SensorObservationEnvelope` JSON object.
- Standards references for storage and knowledge contracts.
- Sensor and platform refs.
- Observation geometry and measurements.
- Source attribution, license, and access tier.
- Provenance with `runtime_boundary_id = runtime:sensorthings-ingest:v0`.
- Governance and classification fields.
- Runtime evidence bundle with input/output hashes, policy posture, and replay command.

## Validation command

```bash
python3 multidomain/sensorthings_ingest.py \
  fixtures/multidomain/sensorthings-observation-input.sample.v1.json \
  /tmp/gaia-sensorthings-ingest-output.json
```

CI workflow:

- `.github/workflows/multidomain-runtime.yml`

## Policy constraints

- Fixture proof is deterministic and does not perform network access.
- Live SensorThings API access must be declared as a separate network-enabled runtime profile.
- Attribution and license refs must be preserved.
- Sensor outputs are evidence artifacts and advisory context unless promoted by governance.
- Sensitive geospatial policy references must be preserved.
- Defense/public-safety use requires explicit authorization and policy gating.

## Runtime isolation default

Container for deterministic fixture processing.

VM or microVM when processing untrusted feeds, restricted feeds, customer-owned restricted data, smart-space data, or defense/public-safety data.

## Network posture

Restricted / none for fixture proof.

Live SensorThings API mode requires explicit network posture and source allowlist.

## Secret posture

None for fixture proof.

Live private feed access requires secret-door integration and redacted audit logs.

## Promotion criteria

The runtime may be considered for Lattice Forge admission only after:

1. executable entrypoint exists;
2. deterministic fixture proof exists;
3. CI validates output invariants;
4. malformed SensorThings fixture corpus exists;
5. source attribution and license preservation are tested;
6. sensitive geospatial policy preservation is tested;
7. runtime evidence bundle is defined;
8. replay command is documented;
9. packaging, SBOM, signing, and rollback tests exist;
10. live SensorThings mode is separately scoped and governed.

## Rollback semantics

Generated sensor observation envelopes are versioned artifacts. Rollback demotes the generated observation record and restores the previous sensor-observation projection. Source SensorThings observations are treated as immutable evidence inputs.

## Current status

Executable fixture proof exists. Not admitted to Lattice Forge.
