# FAQ


## Is this related to GAIA driving world models (GAIA-1/GAIA-2)?
No. Name collision. This repo is about Earth digital twinning via ontologies + provenance + auditable actions.

## Why store sources in-repo?
Reproducibility and auditability. We pin upstream SHAs and store snapshots so rebuilds don’t depend on upstream drift.


## Why Git LFS?
Some upstream ontology artifacts are large. LFS keeps normal git usable while preserving exact content.


## Does GAIA define a single universal ontology?
No. We integrate multiple domain ontologies and map/align them explicitly and testably.


## How do we respect licensing?
We record license evidence in `gaia/cv/manifests/` and document policy in `docs/ATTRIBUTION_POLICY.md` and `THIRD_PARTY_NOTICES.md`.
