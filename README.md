# GAIA World Model

A modular, auditable world-model + ontology + action framework for responsible Earth digital twinning.

We treat “world modeling” like engineering: **every dataset, ontology, and action is traceable, hashed, and attributable**.
This repo is MIT-licensed **as a wrapper**; upstream sources retain their original licenses (tracked under `gaia/cv/`).

## What’s in here

- **GAIA ontology** (core + domain extensions + alignments): `gaia/ontology/`
- **Curation Vault (CV)**: ingested source corpora, manifests, and file-level checklist: `gaia/cv/`
- **Adapters**: offline importers / inventory tools: `gaia/adapters/`
- **Actions**: declarative action templates (observe / audit / plan / actuate): `gaia/actions/`
- **Docs**: architecture, integration notes, governance: `gaia/docs/` and `docs/`

## Quickstart (local)

1) Inspect what’s been ingested:
- `gaia/cv/inventory.yaml`
- `gaia/cv/manifests/`
- `gaia/cv/checklist.csv`

2) Pick canonical ontology entrypoints:
- promote selected files into: `gaia/ontology/canonical/`
- update: `gaia/ontology/imports_index.yaml` (staging) → `gaia/ontology/canonical/index.yaml` (authoritative)

3) Run adapters (examples):
- OSM chef inventory: `python gaia/adapters/osm/chef_inventory.py /path/to/openstreetmap-chef`
- MBTiles introspection: `python gaia/adapters/openmaptiles/mbtiles_introspect.py /path/to/tiles.mbtiles`

## Governance + attribution

- MIT license applies to GAIA wrapper code and original files created here.
- All third-party materials are tracked in the CV:
  - `gaia/cv/sources/` (raw ingests)
  - `gaia/cv/manifests/` (license evidence + counts + merkle roots)
  - `gaia/cv/checklist.csv` (file-level hashes)

See: `THIRD_PARTY_NOTICES.md` and `docs/ATTRIBUTION_POLICY.md`.

## Status

This repo is in active construction. Current state includes integrations and CV ingestion up through **v0.8**; see `docs/CHANGELOG.md` and `docs/INTEGRATION_LOG.md`.
