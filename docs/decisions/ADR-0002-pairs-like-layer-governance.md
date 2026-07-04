# ADR-0002: GAIA PAIRS-like Layer Governance

Status: Proposed

## Context

GAIA already defines the repository spine for responsible Earth digital twinning: Curation Vault provenance, canonical ontology entrypoints, validation, declarative actions, generated reports, registry contracts, Workflow IR, and assessment scorecards. The PAIRS-like platform pattern we want to adopt is therefore not a new repository estate. It is a GAIA profile for spatiotemporal layers, generated operational artifacts, policy-aware query contracts, and auditable event envelopes.

The operating failure mode we are avoiding is the hybrid memo becoming the operational database: a hand-authored document that mixes links, people, work items, client or domain context, dates, policy claims, and cost/usage fragments without machine-checkable provenance or classification. GAIA should make those artifacts generated views over structured records.

## Decision

Land the PAIRS-like layer/query/governance work inside `SocioProphet/gaia-world-model` as contracts, schemas, examples, report templates, and validation hooks. Do not create new repositories for `gaia-contracts`, `gaia-catalog`, `gaia-ledger`, `socioprophet-runsheet`, `socioprophet-query-plane`, or `socioprophet-policy-pdp` until the contracts prove that a runtime split is required.

## Consequences

- GAIA remains the semantic and provenance home for world-model layers.
- The Curation Vault remains the provenance/capture home for sources, manifests, hashes, and inventory.
- The Registry Contract remains the discovery/composition contract and is extended by identifier, event, classification, RunSheet, and layer-query profiles.
- Workflow IR remains the execution-shape home for ingest, normalize, register, evaluate policy, query, and report workflows.
- Reports become generated evidence artifacts with schemas and manifests rather than hand-maintained authority.

## Non-goals

- No production query service is introduced by this ADR.
- No new repository is created by this ADR.
- No claim is made that GAIA is a complete Earth simulator today.
- No network ingestion or external data fetch is required by the initial contract package.

## Initial implementation package

- `docs/contracts/IDENTIFIER_PROFILE.md`
- `docs/contracts/EVENT_ENVELOPE.md`
- `docs/contracts/SPATIOTEMPORAL_LAYER_QUERY.md`
- `docs/contracts/RUNSHEET_CONTRACT.md`
- `docs/policy/CLASSIFICATION_PROFILE.md`
- `schemas/jsonschema/**`
- `examples/**`
- `gaia/reports/templates/runsheet.v1.md`
- `scripts/validate_gaia_contract_examples.py`
