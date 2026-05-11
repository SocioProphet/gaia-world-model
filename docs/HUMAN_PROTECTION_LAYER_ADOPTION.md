# Human Protection Layer adoption for GAIA World Model

Status: adoption stub referencing ProCybernetica reconciliation draft.

Authoritative doctrine source: `SocioProphet/ProCybernetica/docs/reconciliation/HUMAN_PROTECTION_LAYER.md`.

## 0. Position

GAIA adopts the Human Protection Layer for Earth/world-model actions whenever outputs can affect people, communities, populations, ecosystems relied upon by people, infrastructure, institutions, or resource access.

GAIA remains a modular, auditable world-model, ontology, and action framework. The Human Protection Layer clarifies that world actions must account for affected populations, consent/participation where relevant, provenance, reversibility, and public-safe reporting.

## 1. GAIA-specific protection rule

GAIA actions must not treat planetary or infrastructure intervention as merely technical. Every world action has possible human and ecological consequences.

Default policy:

- observation is allowed when provenance and license rules pass;
- audit and planning are allowed when clearly labeled;
- actuation requires policy constraints, affected-population review, reversibility analysis, and report generation;
- speculative world-control claims cannot become action templates;
- hidden or unattributable data sources cannot support high-impact recommendations;
- public reports must distinguish evidence tier, uncertainty, limitations, and policy status.

## 2. Mapping HPL onto the GAIA pipeline

GAIA pipeline:

```text
CV / Sources -> Canonical Ontology -> Validation -> Actions -> Reports
```

HPL overlay:

```text
CV / Sources
  -> provenance, license, publication boundary
Canonical Ontology
  -> protected-person and affected-population semantics
Validation
  -> SHACL/constraints plus HPL gates
Actions
  -> observe/audit/plan/actuate with policy status
Reports
  -> evidence tier, affected-population risk, redress/consultation notes
```

## 3. Affected-population review

Every GAIA action template that may affect people must include:

```yaml
affected_population_review:
  required: true
  population_scope: individual | group | community | region | global | unknown
  benefit_claim: string
  risk_claim: string
  distributional_effects: string
  uncertainty: low | medium | high | unknown
  consultation_required: boolean
  reversibility: reversible | partially_reversible | irreversible | unknown
  redress_path: string
  policy_status: allow | deny | block | needs_review
```

## 4. GAIA action status labels

GAIA should use HPL status labels for action outputs:

- SAFE_TO_USE_AS_INTERNAL_PLANNING;
- SAFE_TO_PUBLISH_AS_SPEC;
- BLOCKED_AFFECTED_POPULATION_RISK;
- BLOCKED_UNDERIDENTIFIED;
- BLOCKED_POLICY;
- SPECULATIVE_ONLY;
- REQUIRES_ETHICS_REVIEW;
- REQUIRES_REGULATORY_REVIEW.

GAIA should not collapse these into a single pass/fail result.

## 5. Required checks before GAIA action promotion

- source provenance is present;
- license/publication boundary is recorded;
- canonical ontology entrypoint is declared;
- validation constraints pass;
- affected-population review is complete where relevant;
- evidence tier is declared;
- reversibility/rollback is described;
- report artifact is generated;
- policy status is recorded;
- speculative claims are not promoted to action templates.

## 6. Digital Control Atlas relationship

GAIA owns the world-chart profile of the Digital Control Atlas.

GAIA does not own human-boundary claim export, ProCybernetica control law, Superconscious planning authority, or AgentPlane replay authority.

Canonical relation:

```text
AtlasWorldChart -> GAIA CV/ontology entrypoint -> Validation -> ActionTemplate -> Report -> Policy Decision
```

There is no direct path from Atlas chart validity to GAIA actuation.
