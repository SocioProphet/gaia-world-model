# Runtime Boundary: GAIA World-Claim Ingest

Status: v0 boundary definition
Date: 2026-05-01

## Runtime name

`gaia-world-claim-ingest-runtime`

## Domain

GAIA geospatial / governed world-model observations

## Purpose

Convert OSM feature extracts (and, in follow-up PRs, EO/STAC, DEM/LiDAR, and weather/reanalysis inputs) into governed GAIA WorldClaim bundles following the contracted ingest pipeline:

```
Observe -> Anchor -> Normalize -> Propose
```

Emitted claims carry `policy_status=proposed`. They must pass Holmes/Policy review before admission to world state or display as truth on `/map`.

## Entrypoint

`geospatial/world_claim_ingest.py`

## Required inputs

- OSM-like JSON fixture or OSM extract query result
- Attribution and license metadata (source_name, license_ref, attribution_text)
- H3 cell refs and geometry (from OSM feature or future indexing step)
- Classification metadata

## Current input examples

- `fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json`

## Emitted outputs

- `gaia.world_claim_ingest.output` bundle containing:
  - `WorldClaim` records (status=proposed)
  - `SourceEvidence` records (OSM, one per feature)
  - `FusionExplanation` traces (single_source_passthrough, one per feature)
  - `runtime_evidence` record
  - `policy` summary
  - `invariants` list

## Schema references

- `schemas/geospatial/world_claim.v1.schema.json`
- `schemas/geospatial/source_evidence.v1.schema.json`
- `schemas/geospatial/geo_anchor.v1.schema.json`
- `schemas/geospatial/fusion_explanation.v1.schema.json`
- `schemas/geospatial/vector_candidate.v1.schema.json`

## Validation command

```bash
python3 geospatial/world_claim_ingest.py \
  fixtures/geospatial/osm-feature-world-claim-input.sample.v1.json \
  /tmp/gaia-world-claim-output.json
```

Deterministic output inspection:

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

## Policy constraints

- No autonomous actuation from proposed world claims.
- OSM-derived world claims are advisory until Holmes/Policy admits them.
- Preserve OSM node/way/relation identity and attribution.
- Preserve OSM license ref (ODbL-1.0) in all derived outputs and displays.
- GeoAnchor is required; claims without geometry are not emitted.
- SourceEvidence must carry attribution, temporal validity, and confidence score.
- ExplanationTrace must record the fusion rule applied.
- Map display layer for proposed claims: `proposed_candidate` with advisory label.
- VectorCandidates (if retrieved) are `candidate_only` and must not influence claim status.

## Expected evidence artifacts

- `SourceEvidence` records (one per OSM feature)
- `FusionExplanation` traces (one per claim)
- `runtime_evidence` record with input/output hashes
- `WorldClaim` bundle (status=proposed)

## Runtime isolation default

Container

## Network posture

Restricted (fixture-only mode); explicitly declared if pulling live OSM/Overpass data.

## Secret posture

None

## Promotion criteria

- Executable entrypoint exists and produces valid output.
- At least one OSM input fixture maps to a valid WorldClaim output with required fields.
- Attribution and license refs are preserved.
- OSM identity (osm_type, osm_id, changeset) is preserved in SourceEvidence.
- GeoAnchor binds each claim to a geometry with H3 cells and bbox.
- ExplanationTrace records the single_source_passthrough rule.
- policy_status is `proposed` on all emitted claims (not admitted or admitted-bypassed).
- Deterministic validation command passes.
- Contract fixture CI passes.
- Malformed-input tests cover: missing required fields, invalid osm_type, wrong source, missing attribution.

## Rollback semantics

Demote generated world claims (set status to `review` or `rejected` in policy record); preserve evidence trail and mark prior claims superseded. Original OSM source records are never mutated. GeoAnchor and SourceEvidence records remain immutable.

## Status

Executable proof exists for fixture input. Not automatically admitted to Lattice Forge. Lattice admission requires: packaging, SBOM, signing, malformed-input tests, rollback tests, and Holmes/Policy integration review.

## Contract reference

`docs/contracts/GOVERNED_WORLD_CLAIM_CONTRACT.md`
