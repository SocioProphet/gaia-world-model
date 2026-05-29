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

## Repo layout

- `gaia/cv/` — ‚Curation Vault (CV)’*: ingested sources + manifests + file-hash checklist  
  - `origins.csv` pins upstream URLs + commit SHAs  
  - `manifests/*.njson` records license evidence + counts + merkle roots  
  - `checklist.csv` provides file-level hashes  
  - large artifacts live in Git LFS (see `docs/CV_STORAGE_POLICY.md`)
- `gaia/ontology/` — canonical entrypoints + imports index (authoritative integration map)
- `gaia/reports/` – generated reports (e.g., Issue-001 entrypoint candidates)
- `docs/` – architecture, policies, releases, integration notes
- `scripts/` – validation/adapters scaffolding (evolves into repeatable pipelines)

## Orion / OSIRIS source-record lane

This repository owns the Gaia side of the Orion/OSIRIS excavation migration: source records, source ledgers, transparent adapter boundaries, provenance discipline, and evidence-grade classification.

`mdheller/osiris` is a quarantine/excavation carcass only. It is not a runtime dependency and is not a trusted source-ingestion implementation. Gaia must not copy OSIRIS route handlers or `stealthFetch`.

Current artifacts:

- `docs/integrations/ORION_OSIRIS_SOURCE_ADAPTERS.md`
- `docs/integrations/ORION_OSIRIS_SOURCE_LEDGER.md`
- `schemas/orion-osiris/gaia_source_record.v0_1.schema.json`
- `fixtures/orion-osiris/source-records/**`
- `scripts/validate_orion_osiris_source_records.py`
- `.github/workflows/orion-osiris-source-records.yml`

Validation:

```bash
python3 scripts/validate_orion_osiris_source_records.py
```

Boundary:

- Gaia owns source/provenance records.
- Orion owns observation events, fusion links, decision cards, receipts, and map markers.
- SCOPE-D owns scanner, sweep, recon, and active target behavior.
- Prophet Platform is a later runtime/workbench consumer after the Gaia/Orion seam stabilizes.

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
