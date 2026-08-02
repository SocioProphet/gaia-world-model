# GAIA Governed World-Claim Contract

Status: v0 reference document
Date: 2026-05-01

## Scope

This document defines the governed world-claim contract for GAIA geospatial and world-model observations. It describes the canonical loop, the objects GAIA owns, the formal invariant, map evidence display requirements, and the boundaries between GAIA, Sherlock, Holmes, Sociosphere, Guardrail Fabric, and Agentplane.

## Canonical loop

```
Observe -> Anchor -> Normalize -> Propose -> Explain -> Verify -> Govern -> Act -> Receipt -> Learn
```

GAIA owns `Observe -> Anchor -> Normalize -> Propose` for geospatial and world-model observations. Holmes/Policy owns `Verify -> Govern`. Agentplane owns `Act -> Receipt`. Sociosphere owns `Learn`.

A map label or spatial feature must not be treated as truth until it has anchors, evidence, temporal validity, uncertainty, and policy status.

## Repo boundaries

| Phase | Owner | Contract |
| --- | --- | --- |
| Observe (sensor, EO, OSM, DEM, weather) | GAIA | `GeoAnchor`, `SourceEvidence` |
| Anchor (geometry, H3, bbox, tile, time window) | GAIA | `GeoAnchor` |
| Normalize (feature classification, risk, coverage) | GAIA | `WorldClaim.proposed_value` |
| Propose (assembled world-state assertion) | GAIA | `WorldClaim` (status=proposed) |
| Explain (fusion rule, evidence chain, uncertainty) | GAIA | `FusionExplanation` |
| Verify (schema, attribution, CRS, temporal check) | Holmes | `PolicyDecision` |
| Govern (admit/provisional/review decision) | Holmes/Policy | `WorldClaimPolicyStatus` |
| Act (map display, routing, downstream use) | Agentplane/GAIA | `WorldClaim` (status=admitted/provisional) |
| Receipt (audit trail, immutable log) | Sociosphere/Guardrail Fabric | Evidence chain |
| Learn (feedback, model update, similarity retrieval) | Sociosphere | `VectorCandidate` (status=candidate_only) |

## Required objects

### GeoAnchor

Binds a world-claim to a verifiable spatial-temporal location. Anchor types:

- `point` — single coordinate
- `linestring` — linear feature (road, rail, waterway segment)
- `polygon` — area feature (building, landuse, watershed boundary)
- `bbox` — bounding-box region
- `h3_cell` — H3 discrete global grid cell
- `tile_region` — raster or vector tile region (XYZ, TMS, STAC tile)
- `document_span` — source document span (field report section)
- `time_window` — temporal anchor only (for observation time windows)

Schema: `schemas/geospatial/geo_anchor.v1.schema.json`

A claim without a GeoAnchor is not admissible.

### SourceEvidence

Evidence from a single source supporting a world-claim. Source types:

- `osm` — OpenStreetMap community data (ODbL-1.0)
- `eo_stac` — Earth Observation product from STAC catalog
- `dem_lidar` — Digital Elevation Model or LiDAR point cloud
- `weather_reanalysis` — weather or reanalysis product (ERA5, etc.)
- `field_report` — field observation report
- `generated_manifest` — GAIA-generated artifact manifest
- `sensor_observation` — sensor measurement (SensorThings, OFIF)
- `synthetic_fixture` — synthetic/demo fixture (not for production admission)

Schema: `schemas/geospatial/source_evidence.v1.schema.json`

Every SourceEvidence record must carry:
- `source_ref` — stable URI for the source artifact
- `attribution` — source name, license ref, and attribution text
- `temporal` — observed_at and staleness class
- `confidence` — score and confidence class

A claim without SourceEvidence must not be admitted.

### WorldClaim

A world-state assertion for a spatial-temporal location. Claim types:

- `feature_classification` — classification of a map feature (road, building, waterway, etc.)
- `risk` — risk or hazard assessment for a location
- `coverage` — coverage fraction or density estimate
- `source_attribution` — source attribution chain for a map label
- `fusion_result` — result of fusing multiple evidence sources
- `observation_passthrough` — direct passthrough of a single observation

Schema: `schemas/geospatial/world_claim.v1.schema.json`

Formal invariant:
```
Observation/Evidence -> ProposedWorldClaim -> ExplanationTrace + Uncertainty -> PolicyDecision -> Admitted/Provisional/Review WorldClaim
```

### FusionExplanation

Records the fusion rule applied, input evidence with roles and weights, derivation steps, uncertainty derivation, and replay instructions.

Schema: `schemas/geospatial/fusion_explanation.v1.schema.json`

A single-source claim uses `fusion_rule.rule_class = single_source_passthrough`. A multi-source claim must document each input with a role (`primary`, `corroborating`, `context`, `constraint`, `prior`, `update`, `override`) and weight.

### WorldClaimPolicyStatus

Governance status of a world-claim. Encoded inline in `WorldClaim.policy_status`:

| Status | Meaning |
| --- | --- |
| `proposed` | Evidence assembled; not yet reviewed by Holmes/Policy |
| `provisional` | Partially admitted with display and expiry constraints |
| `admitted` | Fully governed; may be shown as world state on /map |
| `review` | Flagged for human review; display with explicit qualification |
| `rejected` | Not admissible; must not be displayed as world state |

A `proposed` or `review` claim must not be displayed as truth on `/map`. A `provisional` claim must carry visible uncertainty, expiry, and advisory labels. An `admitted` claim may be shown as world state subject to source attribution display.

### VectorCandidate

Vector-symbolic memory record for similar-observation retrieval. Used by Sherlock for federated discovery of past observations similar to a current query.

Schema: `schemas/geospatial/vector_candidate.v1.schema.json`

**Invariant**: `VectorCandidate.status` is always `candidate_only`. A VectorCandidate:
- must not be used as evidence for world-claim admission;
- must not influence policy decisions;
- must not be shown as world state on /map;
- is a retrieval memory aid only.

## Fusion rules

### Single-source passthrough

Used when a single authoritative source is the only evidence for a claim.

- `rule_class = single_source_passthrough`
- Evidence confidence propagates directly to the claim.
- No weighted aggregation.
- Policy status is `proposed` unless Holmes/Policy explicitly admits.

### Weighted mean

Used when multiple evidence sources are combined.

- `rule_class = weighted_mean`
- Each input carries a role and weight (weights sum to 1.0).
- Combined confidence = sum(weight_i * confidence_i).
- Cloud-cover, resolution, and staleness penalties applied per source.
- Policy status is `proposed` until confidence exceeds admission threshold.

Confidence thresholds (v0):

| Combined confidence | Candidate policy status |
| --- | --- |
| ≥ 0.80 | proposed (may be admitted by Holmes/Policy) |
| 0.60 – 0.79 | proposed → provisional after Holmes review |
| < 0.60 | proposed → review (requires human review) |

These thresholds are advisory in v0. Holmes/Policy makes the binding governance decision.

## Map display requirements

The `/map` surface must display the following for every world-claim layer:

### Admitted claims

- Source attribution text visible on hover/click.
- Temporal validity window visible (valid_from / valid_to).
- Confidence score and uncertainty class visible.
- Evidence chain link available (links to SourceEvidence and FusionExplanation).
- Policy status badge: "Admitted world state".

### Provisional claims

- Source attribution text visible on hover/click.
- Temporal validity window and expiry notice visible.
- Confidence score, uncertainty class, and uncertainty notes visible.
- Evidence chain link available.
- Advisory label from `map_display.advisory_label`.
- Policy status badge: "Provisional — constraints apply".
- Active constraints listed.

### Proposed and review claims

- Must not be displayed as truth.
- If shown (e.g. in a candidate layer), must carry a prominent advisory label.
- Policy status badge: "Candidate — not admitted" or "Under review".
- Confidence and uncertainty visible.
- No routing or actuation allowed from proposed/review claims.

### VectorCandidates

- Must not appear on /map as world-state features.
- May appear in a separate "similar observations" panel with explicit "candidate_only" label.

## Worked examples

### Example 1: OSM feature ingest → proposed world claim

Input: `fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json`

OSM way 424242 (residential road, Demo Corridor Road) is ingested from an OpenStreetMap extract. The ingest script:

1. **Observe**: Read OSM feature with tags, geometry, H3 cells, bbox, routing metadata.
2. **Anchor**: Build a `linestring` GeoAnchor with temporal binding from OSM changeset timestamp.
3. **Normalize**: Map `highway=residential` + `surface=asphalt` tags to entity type `RoadSegment`.
4. **Propose**: Assemble a `WorldClaim` with `claim_type=feature_classification`, `policy_status=proposed`.
5. **Explain**: Record `single_source_passthrough` FusionExplanation with confidence=0.85.

Output: `fixtures/geospatial/osm-feature-world-claim.sample.v1.json`

Validation command:
```bash
python3 geospatial/world_claim_ingest.py \
  fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json \
  /tmp/gaia-world-claim-output.json
```

Deterministic validation expectations:
- Output contains `claims[0].policy_status.status = "proposed"`.
- Output contains `claims[0].claim_type = "feature_classification"`.
- Output contains `claims[0].uncertainty.confidence_score = 0.85`.
- Output contains `claims[0].map_display.display_layer = "proposed_candidate"`.
- Output contains `evidence_records[0].source_type = "osm"`.
- Output contains `explanation_traces[0].fusion_rule.rule_class = "single_source_passthrough"`.

### Example 2: EO + OSM + DEM/weather fusion → risk/feature claim

Fixture: `fixtures/geospatial/eo-osm-dem-fusion-world-claim.sample.v1.json`

Four evidence sources are fused to produce a road-surface risk claim for lower Manhattan:

| Source | Type | Confidence | Role | Weight |
| --- | --- | --- | --- | --- |
| Sentinel-like EO scene (STAC) | `eo_stac` | 0.72 | primary | 0.35 |
| OSM way 424242 | `osm` | 0.85 | corroborating | 0.25 |
| SRTM DEM (30m) | `dem_lidar` | 0.80 | context | 0.20 |
| ERA5-like reanalysis | `weather_reanalysis` | 0.74 | context | 0.20 |

Combined confidence = 0.68 (moderate; EO cloud-cover penalty applied).

Result: `claim_type=risk`, `risk_class=moderate`, `policy_status=provisional` (confidence below 0.80 admission threshold). Claim expires at `2026-05-01T15:00:00Z` (weather validity window).

Map display: `display_layer=provisional_overlay` with advisory label, visible uncertainty, and expiry time.

## Vector-symbolic memory notes

`VectorCandidate` records enable Sherlock to retrieve past world-claims similar to a current observation query. They support:

- Context retrieval for new observations (is this observation unusual relative to historical patterns?);
- Evidence discovery (find past claims that corroborate or contradict a new proposed claim);
- Model feedback loops (Sociosphere/Learn phase).

Key constraints:

- `VectorCandidate.status` is always `candidate_only`. This is an invariant, not a configuration.
- Vector retrieval results must not be passed directly to Holmes/Policy as evidence.
- Vector candidates must pass through the full `Observe -> Anchor -> Normalize -> Propose -> Explain -> Verify -> Govern` pipeline before any claim status update.
- Embedding models and index versions must be recorded in `VectorCandidate.similarity.embedding_model_ref` and `index_ref`.

Fixture: `fixtures/geospatial/vector-candidate.sample.v1.json`

## Integration notes

### Sherlock Search

GAIA publishes world-claims as searchable records with:
- `claim_id`, `claim_type`, `policy_status`;
- `geo_anchor` (H3 cells, bbox);
- `temporal_validity`;
- `source_evidence_refs`;
- `attribution.primary_source_name`.

Sherlock must not return `proposed` or `rejected` claims as world-state features. Search result snippets must include policy status and advisory labels.

See `docs/integrations/SHERLOCK_SEARCH_INTEGRATION.md`.

### Holmes (reasoning)

Holmes consumes `WorldClaim` (status=proposed or provisional) and emits `PolicyDecision` records that update claim status. Holmes must:
- Check attribution validity and license compatibility;
- Validate CRS, geometry encoding, and temporal bounds;
- Review uncertainty class against thresholds;
- Apply active policy constraints;
- Produce an explicit `admitted`, `provisional`, `review`, or `rejected` decision with reasoning.

Holmes issue: SocioProphet/holmes#7

### Sociosphere

Sociosphere consumes admitted and provisional world-claims for higher-order world-state aggregation, learning loops, and coordination signals. Sociosphere must not consume `proposed` or `rejected` claims as world state.

Parent coordination issue: SocioProphet/sociosphere#310

### Guardrail Fabric

Guardrail Fabric enforces:
- No autonomous actuation from `proposed` or `review` claims;
- No map display of `proposed` claims as truth;
- No bypass of source attribution, license, geometry, CRS, temporal, or uncertainty checks;
- Mandatory advisory labels for `provisional` claims on /map.

### Agentplane

Agentplane may act on `admitted` world-claims subject to policy constraints. It must not act on `proposed`, `review`, or `rejected` claims without explicit human approval.

### Ontogenesis canonical contracts

| GAIA object | Ontogenesis canonical |
| --- | --- |
| `GeoAnchor` | `gaia:SpatialAnchor` (schema root SocioProphet/ontogenesis#77) |
| `SourceEvidence` | `gaia:EvidenceObservation` |
| `WorldClaim` | `gaia:WorldStateClaim` |
| `FusionExplanation` | `gaia:ExplanationTrace` |
| `WorldClaimPolicyStatus` | `gaia:PolicyDecisionStatus` |
| `VectorCandidate` | `gaia:VectorMemoryCandidate` |

Schema root issue: SocioProphet/ontogenesis#77

## CHRONOS carrier compatibility (SocioProphet/gaia-world-model#38)

Sociosphere's `docs/integration/neurosymbolic-chronos-alignment.md` defines a "CHRONOS carrier" boundary: any object crossing a governance boundary that references neuro-symbolic reasoning must carry source evidence reference, method family, method output type, grounding status, validation status, explanation trace reference, owning authority plane, non-authority declaration, replay reference, and governance decision/pending. GAIA's `WorldClaim`/`FusionExplanation` contract already matched this shape closely. This is an **additive** extension — every field below is optional, `additionalProperties` stays `false` only at the level each field was added to, and no existing field, required list, or runtime behavior changed. Fixtures written before this change remain valid.

| CHRONOS carrier concept | GAIA field | Status |
| --- | --- | --- |
| Source evidence reference | `WorldClaim.source_evidence_refs` | Already covered — no new field |
| Method family | `FusionExplanation.fusion_rule.chronos_method_family` | **New.** Distinct from `rule_class`, which classifies GAIA's own fusion mechanics (weighted_mean, bayesian_update, ...), not neuro-symbolic technique |
| Method output type | `FusionExplanation.fusion_rule.chronos_method_output_type` | **New.** `hard_value` by default; non-hard values (`fuzzy_satisfaction_score`, `truth_bound`, `symbolic_derivation`, `learned_rule_candidate`, `ontology_delta_candidate`, `policy_proposal`, `event_schema_candidate`) require a non-authority declaration |
| Grounding status | `WorldClaim.chronos_grounding_status` | **New.** Distinct from `uncertainty.confidence_score`/`uncertainty_class`, which remain GAIA's existing confidence measure |
| Validation status | `WorldClaim.policy_status` | Already covered — GAIA's contract has Holmes perform verify+govern as one step (see "Repo boundaries" above), so `policy_status.status` already carries both the CHRONOS "validation status" and "governance decision" roles. No new field |
| Explanation trace reference | `WorldClaim.explanation_trace_ref` | Already covered — no new field |
| Owning authority plane | `WorldClaim.chronos_owning_authority_plane` | **New.** Names which repo/plane holds final admission authority for this specific claim (e.g. `SocioProphet/holmes`) |
| Non-authority declaration | `FusionExplanation.chronos_non_authority_declaration` | **New.** Required whenever `chronos_method_family`/`chronos_method_output_type` name a neuro-symbolic or soft-output method. Directly implements the CHRONOS negative rule "a fuzzy satisfaction score is promoted as truth": `is_candidate_only=true` plus `policy_status.status != admitted` must both hold |
| Replay reference | `FusionExplanation.replay` | Already covered — no new field |
| Governance decision or pending | `WorldClaim.policy_status.status` | Already covered — no new field |

Worked examples:

- `fixtures/geospatial/eo-osm-dem-fusion-world-claim.sample.v1.json` — classical weighted-mean fusion; `chronos_method_family=classical_deterministic`, `chronos_method_output_type=hard_value`, no non-authority declaration needed.
- `fixtures/geospatial/ltn-fuzzy-vegetation-dryness-risk-world-claim.sample.v1.json` — an LTN-style differentiable fuzzy-logic fusion producing a `fuzzy_satisfaction_score`; carries a full `chronos_non_authority_declaration` and is correctly held at `policy_status.status=review`, never `admitted`.
- `fixtures/geospatial/negative/world-claim-fuzzy-score-admitted-without-non-authority-declaration.invalid.v1.json` — the same fuzzy-score fusion incorrectly promoted to `admitted` with no non-authority declaration; must be, and is, rejected.

Validator: `scripts/validate_chronos_carrier_fixtures.py` (wired into `.github/workflows/contract-fixtures.yml`) checks both schemas declare the new fields as optional, validates the positive fixtures, and confirms the negative fixture is rejected.

## Non-goals (v0)

- Live ingestion pipelines (fixtures and deterministic proofs only in this PR).
- Publishing admitted map state from raw model output or raw vector retrieval.
- Bypassing source attribution, license, geometry, CRS, temporal, or uncertainty checks.
- Using VectorCandidates as evidence for policy decisions.

## Validation

Run the worked example validation command:
```bash
python3 geospatial/world_claim_ingest.py \
  fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json \
  /tmp/gaia-world-claim-output.json
```

Inspect the output:
```bash
python3 -c "
import json
with open('/tmp/gaia-world-claim-output.json') as f:
    d = json.load(f)
c = d['claims'][0]
assert c['policy_status']['status'] == 'proposed', 'claim must be proposed'
assert c['uncertainty']['confidence_score'] == 0.85, 'confidence must be 0.85'
assert c['map_display']['display_layer'] == 'proposed_candidate', 'must be proposed_candidate layer'
assert d['evidence_records'][0]['source_type'] == 'osm', 'source_type must be osm'
assert d['explanation_traces'][0]['fusion_rule']['rule_class'] == 'single_source_passthrough'
print('All deterministic validation checks passed.')
"
```

If a JSON Schema validator is available:
```bash
# pip install check-jsonschema
check-jsonschema --schemafile schemas/geospatial/world_claim.v1.schema.json \
  fixtures/geospatial/osm-feature-world-claim.sample.v1.json
```
