# Runtime Boundary — GAIA STAC Ingest

Status: executable fixture proof; Lattice admission candidate, not admitted
Date: 2026-04-27

## Runtime identity

Runtime name: `gaia-stac-ingest-runtime`

Domain: GAIA Earth observation / satellite product ingestion

Purpose: convert a STAC-like item fixture into a standards-bound `EarthObservationProductRecord` while preserving catalog, collection, asset, spatial, temporal, attribution, provenance, and sensitive-geospatial governance metadata.

## Standards references

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Entrypoint

`multidomain/stac_ingest.py`

## Required inputs

- STAC-like item JSON fixture.
- Catalog reference.
- Collection reference.
- STAC item ID, geometry, bbox, temporal properties, and assets.
- Attribution and license metadata.
- Sensitive geospatial classification reference.

Current fixture:

- `fixtures/multidomain/stac-item-input.sample.v1.json`

## Emitted outputs

- `EarthObservationProductRecord` JSON object.
- Standards references for storage and knowledge contracts.
- Product asset refs derived from STAC asset hrefs.
- Spatial refs: GeoJSON geometry, bbox, H3 refs when present.
- Temporal refs: observed start, observed end, published time.
- Source attribution, license, and access tier.
- Provenance with `runtime_boundary_id = runtime:stac-ingest:v0`.
- Governance and classification fields.

## Validation command

```bash
python3 multidomain/stac_ingest.py \
  fixtures/multidomain/stac-item-input.sample.v1.json \
  /tmp/gaia-stac-ingest-output.json
```

CI workflow:

- `.github/workflows/multidomain-runtime.yml`

## Policy constraints

- Fixture proof is deterministic and does not perform network access.
- Live STAC catalog access must be declared as a separate network-enabled runtime profile.
- Attribution and license refs must be preserved.
- Derived Earth observation products are evidence artifacts, not autonomous action decisions.
- Sensitive geospatial policy references must be preserved.
- Defense/public-safety use requires explicit authorization and policy gating.

## Runtime isolation default

Container for deterministic fixture processing.

VM or microVM when processing untrusted catalogs, private catalogs, customer-owned restricted data, or defense/public-safety data.

## Network posture

Restricted / none for fixture proof.

Live catalog mode requires explicit network posture and source allowlist.

## Secret posture

None for fixture proof.

Live private catalog access requires secret-door integration and redacted audit logs.

## Promotion criteria

The runtime may be considered for Lattice Forge admission only after:

1. executable entrypoint exists;
2. deterministic fixture proof exists;
3. CI validates output invariants;
4. malformed STAC fixture corpus exists;
5. source attribution and license preservation are tested;
6. sensitive geospatial policy preservation is tested;
7. runtime evidence bundle is defined;
8. replay command is documented;
9. packaging, SBOM, signing, and rollback tests exist.

## Rollback semantics

Generated Earth observation records are versioned artifacts. Rollback demotes the generated EO product record and restores the previous catalog projection. Source STAC items are treated as immutable evidence inputs.

## Current status

Executable fixture proof exists. Not admitted to Lattice Forge.
