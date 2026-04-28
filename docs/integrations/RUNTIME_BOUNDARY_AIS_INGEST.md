# Runtime Boundary — GAIA AIS Ingest

Status: executable fixture proof; Lattice admission candidate, not admitted
Date: 2026-04-27

## Runtime identity

Runtime name: `gaia-ais-ingest-runtime`

Domain: GAIA maritime domain awareness / vessel-track ingestion

Purpose: convert an AIS-like message fixture into a standards-bound `VesselTrackObservation` while preserving vessel identity, observed position, motion, navigation status, source attribution, provenance, runtime evidence, and sensitive-geospatial governance metadata.

## Standards references

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Entrypoint

`multidomain/ais_ingest.py`

## Required inputs

- AIS-like message JSON fixture.
- Feed reference.
- MMSI and optional IMO identity.
- Observed time, latitude, longitude, course, speed, and navigation status.
- Attribution and license metadata.
- Sensitive geospatial classification reference.

Current fixture:

- `fixtures/multidomain/ais-message-input.sample.v1.json`

Negative fixtures:

- `fixtures/multidomain/negative/ais-message-wrong-source.sample.v1.json`
- `fixtures/multidomain/negative/ais-message-bad-lat.sample.v1.json`

## Emitted outputs

- `VesselTrackObservation` JSON object.
- Standards references for storage and knowledge contracts.
- Vessel identity refs: MMSI and IMO where present.
- Track position, motion, and navigation status.
- Source attribution, license, and access tier.
- Provenance with `runtime_boundary_id = runtime:ais-ingest:v0`.
- Governance and classification fields.
- Runtime evidence bundle with input/output hashes, policy posture, and replay command.

## Validation command

```bash
python3 multidomain/ais_ingest.py \
  fixtures/multidomain/ais-message-input.sample.v1.json \
  /tmp/gaia-ais-ingest-output.json
```

CI workflow:

- `.github/workflows/multidomain-runtime.yml`

## Policy constraints

- Fixture proof is deterministic and does not perform network access.
- Live AIS feed access must be declared as a separate network-enabled runtime profile.
- Attribution and license refs must be preserved.
- Vessel-track outputs are evidence artifacts and advisory context, not autonomous enforcement or targeting decisions.
- Sensitive geospatial policy references must be preserved.
- Defense/public-safety use requires explicit authorization and policy gating.
- Unauthorized tracking workflows are out of scope.

## Runtime isolation default

Container for deterministic fixture processing.

VM or microVM when processing untrusted feeds, restricted feeds, customer-owned restricted data, or defense/public-safety data.

## Network posture

Restricted / none for fixture proof.

Live AIS feed mode requires explicit network posture and source allowlist.

## Secret posture

None for fixture proof.

Live private feed access requires secret-door integration and redacted audit logs.

## Promotion criteria

The runtime may be considered for Lattice Forge admission only after:

1. executable entrypoint exists;
2. deterministic fixture proof exists;
3. CI validates output invariants;
4. malformed AIS fixture corpus exists;
5. source attribution and license preservation are tested;
6. sensitive geospatial policy preservation is tested;
7. runtime evidence bundle is defined;
8. replay command is documented;
9. packaging, SBOM, signing, and rollback tests exist;
10. live feed mode is separately scoped and governed.

## Rollback semantics

Generated vessel-track observations are versioned artifacts. Rollback demotes the generated vessel-track record and restores the previous maritime-domain projection. Source AIS messages are treated as immutable evidence inputs.

## Current status

Executable fixture proof exists. Not admitted to Lattice Forge.
