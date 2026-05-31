# GAIA world model

Canonical contracts, profile projections, and domain packs for auditable world models.

## Profiles
- agent
- local
- meso
- earth
- universal

## Core contract families
- entity
- relation
- state
- observation
- action
- policy
- capability
- provenance
- evidence

## World-state claim contracts

GAIA owns the governed world-claim pipeline for geospatial and world-model observations:

```
Observe -> Anchor -> Normalize -> Propose
```

Downstream phases (Verify → Govern → Act → Receipt → Learn) are owned by Holmes/Policy, Agentplane, Guardrail Fabric, and Sociosphere respectively.

| Contract | Schema | Purpose |
| --- | --- | --- |
| `GeoAnchor` | `schemas/geospatial/geo_anchor.v1.schema.json` | Spatial-temporal binding for observations and claims |
| `SourceEvidence` | `schemas/geospatial/source_evidence.v1.schema.json` | Evidence from OSM, EO/STAC, DEM/LiDAR, weather/reanalysis, field reports |
| `WorldClaim` | `schemas/geospatial/world_claim.v1.schema.json` | Governed world-state assertion with policy status |
| `FusionExplanation` | `schemas/geospatial/fusion_explanation.v1.schema.json` | Fusion rule, evidence chain, and uncertainty derivation |
| `VectorCandidate` | `schemas/geospatial/vector_candidate.v1.schema.json` | Similar-observation retrieval (status=candidate_only always) |

Reference document: `docs/contracts/GOVERNED_WORLD_CLAIM_CONTRACT.md`

Formal invariant:
```
Observation/Evidence -> ProposedWorldClaim -> ExplanationTrace + Uncertainty -> PolicyDecision -> Admitted/Provisional/Review WorldClaim
```
