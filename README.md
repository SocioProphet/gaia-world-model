# GAIA World Model

GAIA World Model is a modular, auditable **world-model + ontology + action framework** for **responsible Earth digital twinning**.

We treat world modeling like engineering: every dataset, ontology, and action is provenance-tracked, hashed, and attributable.

## What GAIA is (and isn’t)

**GAIA is:**
- A reproducible integration spine for Earth-relevant ontologies, datasets, and tooling
- A provenance discipline: pinned upstream commits, file hashes, manifests, and storage policy
- An actions framework: observe → audit → plan → actuate (with explicit semantics and guardrails)

**GAIA is not:**
 - A monolithic “one ontology to rule them all”
- A hidden-data model: we bias toward open, attributable sources
- A turnkey Earth simulator today (we’re building the scaffolding and verification first)


## Governed world-claim contract

GAIA owns the `Observe -> Anchor -> Normalize -> Propose` phases of the canonical world-state loop for geospatial and spatial-temporal observations. A map label or spatial feature is not treated as truth until it has anchors, evidence, temporal validity, uncertainty, and policy status.

Key contracts:

| Contract | Schema | Purpose |
| --- | --- | --- |
| `GeoAnchor` | `schemas/geospatial/geo_anchor.v1.schema.json` | Spatial-temporal binding for observations |
| `SourceEvidence` | `schemas/geospatial/source_evidence.v1.schema.json` | OSM, EO/STAC, DEM/LiDAR, weather, field reports |
| `WorldClaim` | `schemas/geospatial/world_claim.v1.schema.json` | Governed world-state assertion with policy status |
| `FusionExplanation` | `schemas/geospatial/fusion_explanation.v1.schema.json` | Fusion rule, evidence chain, uncertainty trace |
| `VectorCandidate` | `schemas/geospatial/vector_candidate.v1.schema.json` | Similar-observation retrieval (candidate_only) |

Reference: `docs/contracts/GOVERNED_WORLD_CLAIM_CONTRACT.md`

For cross-system discovery: Sherlock (`docs/integrations/SHERLOCK_SEARCH_INTEGRATION.md`), Holmes (SocioProphet/holmes#7), Sociosphere (SocioProphet/sociosphere#310), Guardrail Fabric, and Agentplane consume GAIA world-claims only after Holmes/Policy governance review.

## Repo layout

- `gaia/cv/` — ‚Curation Vault (CV)’*: ingested sources + manifests + file-hash checklist  
  - `origins.csv` pins upstream URLs + commit SHAs  
  - `manifests/*.njson` records license evidence + counts + merkle roots  
  - `checklist.csv` provides file-level hashes  
  - large artifacts live in Git LFS (see `docs/CV_STORAGE_POLICY.md`)
- `gaia/ontology/` — canonical entrypoints + imports index (authoritative integration map)
- `gaia/reports/` – generated reports (e.g., Issue-001 entrypoint candidates)
- `docs/` – architecture, policies, releases, integration notes
- `docs/contracts/` – governed contract reference documents (world-claim, registry, TritRPC)
- `schemas/geospatial/` – JSON Schema definitions for world-claim contracts
- `geospatial/` – ingest scripts (OSM, world-claim, route graph, tile export)
- `fixtures/geospatial/` – worked example fixtures for contracts and runtimes
- `scripts/` – validation/adapters scaffolding (evolves into repeatable pipelines)

## Quickstart

This repo uses **Git LFS**. Without LFS, you’ll only get pointer files for large artifacts.

```bash
git clone https://github.com/SocioProphet/gaia-world-model.git
cd gaia-world-model
git lfs install
git lfs pull
```

## How we work
1) **Ingest** third-party sources into the CV (pinned SHA, manifests, hashes)  
2) **Select canonical entrypoints** per source (`gaia/ontology/canonical/`)  
3) **Validate** graph closure and shapes (SHACL / constraints)  4) **Define actions** with explicit semantics and measurable outputs  
5) **Publish** changes with release tags and reproducible reports

## Licensing and attribution

- MIT license applies to original GAIA wrapper code and docs in this repo.
- Upstream content remains under upstream licenses, tracked in the CV.
- See `THIRD_PARTY_NOTICES.md` and `docs/ATTRIBUTION_POLICY.md`.

## Start here

- `docs/ABOUT.md`
- `docs/GETTING_STARTED.md`
- `docs/ARCHITECTURE.md`
- `docs/RESPONSIBLE_USE.md`
- `docs/RELEASES.md`

Issues: https://github.com/SocioProphet/gaia-world-model/issues
- `docs/COMMONS_AND_STACK.md` — GAIA in the global AI/knowledge commons + SocioProphet stack integration

## Documentation

See `docs/README.md` for the full documentation index.
