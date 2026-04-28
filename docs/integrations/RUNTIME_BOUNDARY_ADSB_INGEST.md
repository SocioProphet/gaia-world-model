# Runtime Boundary — GAIA ADS-B Ingest

Status: executable fixture proof; Lattice admission candidate, not admitted
Date: 2026-04-27

## Runtime identity

Runtime name: `gaia-adsb-ingest-runtime`

Domain: GAIA air-domain awareness / air-track ingestion

Purpose: convert an ADS-B-like message fixture into a standards-bound `AirTrackObservation` while preserving aircraft identity, observed position, altitude, motion, flight status, source attribution, provenance, runtime evidence, and sensitive-geospatial governance metadata.

## Standards references

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Entrypoint

`multidomain/adsb_ingest.py`

## Required inputs

- ADS-B-like message JSON fixture.
- Feed reference.
- ICAO24 identity and optional callsign.
- Observed time, latitude, longitude, altitude, track, speed, vertical rate, and flight status.
- Attribution and license metadata.
- Sensitive geospatial classification reference.

Current fixture:

- `fixtures/multidomain/adsb-message-input.sample.v1.json`

Negative fixtures:

- `fixtures/multidomain/negative/adsb-message-wrong-source.sample.v1.json`
- `fixtures/multidomain/negative/adsb-message-bad-altitude.sample.v1.json`

## Emitted outputs

- `AirTrackObservation` JSON object.
- Standards references for storage and knowledge contracts.
- Aircraft identity refs: ICAO24 and callsign where present.
- Track position, altitude, motion, and flight status.
- Source attribution, license, and access tier.
- Provenance with `runtime_boundary_id = runtime:adsb-ingest:v0`.
- Governance and classification fields.
- Runtime evidence bundle with input/output hashes, policy posture, and replay command.

## Validation command

```bash
python3 multidomain/adsb_ingest.py \
  fixtures/multidomain/adsb-message-input.sample.v1.json \
  /tmp/gaia-adsb-ingest-output.json
```

CI workflow:

- `.github/workflows/multidomain-runtime.yml`

## Policy constraints

- Fixture proof is deterministic and does not perform network access.
- Live ADS-B feed access must be declared as a separate network-enabled runtime profile.
- Attribution and license refs must be preserved.
- Air-track outputs are evidence artifacts and advisory context, not autonomous enforcement or targeting decisions.
- Sensitive geospatial policy references must be preserved.
- Defense/public-safety use requires explicit authorization and policy gating.
- Unauthorized tracking workflows are out of scope.

## Runtime isolation default

Container for deterministic fixture processing.

VM or microVM when processing untrusted feeds, restricted feeds, customer-owned restricted data, or defense/public-safety data.

## Network posture

Restricted / none for fixture proof.

Live ADS-B feed mode requires explicit network posture and source allowlist.

## Secret posture

None for fixture proof.

Live private feed access requires secret-door integration and redacted audit logs.

## Promotion criteria

The runtime may be considered for Lattice Forge admission only after:

1. executable entrypoint exists;
2. deterministic fixture proof exists;
3. CI validates output invariants;
4. malformed ADS-B fixture corpus exists;
5. source attribution and license preservation are tested;
6. sensitive geospatial policy preservation is tested;
7. runtime evidence bundle is defined;
8. replay command is documented;
9. packaging, SBOM, signing, and rollback tests exist;
10. live feed mode is separately scoped and governed.

## Rollback semantics

Generated air-track observations are versioned artifacts. Rollback demotes the generated air-track record and restores the previous air-domain projection. Source ADS-B messages are treated as immutable evidence inputs.

## Current status

Executable fixture proof exists. Not admitted to Lattice Forge.
