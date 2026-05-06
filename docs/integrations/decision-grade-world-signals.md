# Decision-Grade World Signals: Foot-Traffic, Weather, Concordance, and Energy Ledgers

Status: integration note v0.1
Owner surface: GAIA World Model
Related surfaces: Prophet Core Contracts, Prophet Core Ledger, Prophet Platform Fabric MLOps TS Suite, Gaia Ontology

## Purpose

This document integrates four related threads into GAIA World Model:

1. Foot-traffic + weather alternative-data onboarding.
2. Authority Concordance Rex (ACR) entity mastering and concordance.
3. EUTC-style energy-resolution ledgers for entity resolution and evidence promotion.
4. Hill-inspired proof-driven security/forensics artifacts for policy-constrained actions.

The common thesis is that world-model facts must not become canonical merely because they were observed. GAIA should treat all external or derived signals as governed evidence that passes through provenance, resolution, validation, and promotion gates before it becomes an actionable world-model assertion.

This aligns with GAIA's existing architecture: CV (Sources) -> Canonical Ontology -> Validation -> Actions -> Reports.

## Integration pattern

### 1. Source evidence enters the Curation Vault

GAIA should ingest source descriptions, manifests, feature registries, entity-mastering catalogs, and model-evaluation reports through the Curation Vault rather than directly into canonical ontology files.

Examples:

- Weather feature registry definitions.
- Foot Traffic Index (FTI) schema and computation contract.
- ACR canonical entity and concordance-map contracts.
- EUTC-style extraction run manifests.
- Proof artifact examples for no-escape, replay, promotion, or policy-gated action claims.

### 2. Canonical ontology gets concepts, not raw vendor semantics

The canonical ontology should model stable concepts:

- `WorldSignal`
- `FeatureRegistryEntry`
- `PointOfInterest`
- `MobilityObservation`
- `FootTrafficIndex`
- `WeatherFeature`
- `CanonicalEntity`
- `ConcordanceLink`
- `DecisionLedgerEntry`
- `EnergyLedgerEntry`
- `ProofArtifact`
- `PromotionDecision`

Vendor-specific names and delivery details stay in CV manifests, provenance metadata, or source-specific adapters.

### 3. Validation owns the promotion membrane

The validation layer should enforce that no signal becomes canonical without:

- source manifest and license/attribution evidence;
- schema validation;
- provenance link to the originating source or computation;
- promotion decision with policy version;
- replay or recomputation path where feasible;
- explicit uncertainty, margin, or confidence where the signal is derived.

For energy-resolution work, this means GAIA records the top entity, runner-up entity, margin delta, perturbation stability, and promotion decision before accepting a concordance result.

### 4. Actions consume governed facts only

GAIA actions should consume governed facts rather than raw observations. The action chain becomes:

observe -> ledger -> validate -> promote -> plan -> actuate

This matters because weather, mobility, entity concordance, and AI interview/personality models can all drive consequential decisions. Their outputs must therefore be traceable, replayable, and bounded by policy.

## Domain modules

### Foot-traffic + weather world signals

Adopt the Foot Traffic Index pattern as a world-signal contract:

```text
FTI(date, entity_or_poi_set) = unique_observed_population_at_poi_set / total_unique_observed_population_for_day
```

GAIA should not treat FTI as raw truth about total human presence. It is a normalized observable population share. The ontology should therefore distinguish:

- observed pings;
- unique observed population;
- POI membership/version;
- denominator population definition;
- computed index value;
- computation spec hash;
- weather confounders and explanatory features.

Weather features should be registered as `FeatureRegistryEntry` objects with explicit temporal grain, horizon, update cadence, spatial type, resolution, units, nullability, and formats.

### Authority Concordance Rex

ACR becomes GAIA's governed entity-mastering pattern. The world model should distinguish:

- `CanonicalEntity`: stable entity identity;
- `SourceRecord`: raw or normalized source assertion;
- `ConcordanceLink`: mapping from source record to canonical entity;
- `AttributeAssertion`: field-level claim from a source;
- `DecisionLedgerEntry`: survivorship and match decision record;
- `RelationshipEdge`: parent/subsidiary/alias/merged/split lineage.

The golden record is a projection. The durable product surface is crosswalk + decision ledger.

### Energy-resolution ledger

Energy resolution measures whether evidence clearly separates one candidate from another. GAIA should model:

- `top_score`;
- `runnerup_score`;
- `margin_delta = top_score - runnerup_score`;
- perturbation flip-rate;
- extraction run ID;
- policy ID;
- promotion decision.

Low-margin or high-instability evidence should not auto-promote. It should remain evidence-only or route to review.

### Proof-driven security fabric

Proof artifacts become reportable evidence packs for GAIA actions and policy decisions. At minimum, a proof artifact carries:

- claim name and version;
- input hashes;
- domain or analyzer used;
- budgets and widening/precision settings where applicable;
- result status;
- witness or counterexample;
- replay instructions;
- signature or provenance hook.

This lets GAIA support claims such as no-escape, no unauthorized promotion, deterministic replay, policy-constrained action, and bounded actuation.

## Repository ownership map

- `gaia-world-model`: integration doctrine, ontology-facing concepts, CV placement, action semantics, reports.
- `prophet-core-contracts`: JSON schemas and examples for shared contracts such as FeatureRegistryEntry, EnergyLedgerEntry, DecisionLedgerEntry, ProofArtifact, and ConcordanceLink.
- `prophet-core-ledger`: runtime/evidence ledger implementation patterns.
- `prophet-platform-fabric-mlops-ts-suite`: time-series, graph-ML, leakage gates, backtests, feature-store/model-evaluation integration.
- `prophet-domain-gaia-ontology`: ontology modules and SHACL shapes once concepts stabilize.
- `prophet-domain-gaia-curation-vault`: source packs, manifests, and evidence bundles where the data itself belongs outside the main repo.

## Immediate backlog

1. Add draft schemas in `prophet-core-contracts` for:
   - `feature-registry-entry.schema.json`;
   - `energy-ledger-entry.schema.json`;
   - `concordance-link.schema.json`;
   - `proof-artifact.schema.json`.
2. Add GAIA ontology stubs for governed world signals, entity concordance, and promotion decisions.
3. Add MLOps evaluation gates for:
   - leakage-safe FTI/weather backtests;
   - graph-ML projection-loss accounting;
   - semantic-leakage checks for entity-resolution and personality/leadership-assessment models.
4. Add reports that explain which artifacts are evidence-only, review-required, or canonical-promoted.

## Non-goals

- Do not vendor-lock GAIA to any one weather, mobility, MDM, or authority-file provider.
- Do not treat personality, interview, or leadership assessment outputs as canonical human truth.
- Do not auto-actuate on low-margin entity-resolution outputs.
- Do not bypass policy admission for agent-generated claims.
