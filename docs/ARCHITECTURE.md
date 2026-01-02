# Architecture

GAIA is built as a pipeline with explicit interfaces:

**CV (Sources) → Canonical Ontology → Validation → Actions → Reports**

## 1) Curation Vault (CV)
The CV is our provenance engine:
- origins (URL + pinned SHA)
- manifests (license evidence + counts + merkle roots)
- checklist (file-level hashes)
- storage policy (git vs LFS)

## 2) Canonical ontology entrypoints
We do not treat every file in every repo as “the ontology.”
We select entrypoint(s) per source and track them explicitly.

- `gaia/ontology/canonical/index.yaml` — authoritative map of entrypoints
- `gaia/ontology/imports_index.yam` – import/merge strategy (evolves over time)

## 3) Validation
Evolves toward:
- SHACL shapes and repeatable validation runner (CI-friendly)
- import-closure checks and consistency constraints

## 4) Actions
Actions are declarative templates:
- observe (collect measurements)
- audit (evaluate against constraints/policies)
- plan (propose interventions)
- actuate (execute bounded changes)

Actions must be attributable, testable, policy-constrained, and produce auditable outputs.

## 5) Reports
Every major decision should be accompanied by generated evidence:
- entrypoint selection reports
- license/manifest diffs
- validation results
- action run summaries
