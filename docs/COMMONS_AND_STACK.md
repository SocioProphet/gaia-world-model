# GAIA in the Global AI & Knowledge Commons — and the SocioProphet Stack

GAIA World Model is **Earth digital twinning you can audit**.

Not “trust the model.”  
Not “just merge the ontology.”  
But: **pin what we used, prove what we claimed, constrain what we did.**

GAIA is the integration spine that turns Earth-relevant sources into **reproducible, attributable, checkable building blocks**.

---

## 1) Why GAIA exists (the commons problem)

The global AI + knowledge commons is full of “open” artifacts that still fail the real test:

- *Where did this come from, exactly?*
- *What changed, when, and why?*
- *What are we allowed to do with it?*
- *Can we reproduce the exact graph we’re using?*
- *Can we constrain actions and audit the outcomes?*

GAIA answers those questions by treating world modeling like engineering.

---

## 2) What we publish to the commons (the “commons contract”)

GAIA’s baseline contribution is a **commons contract**:

1. **Pinned provenance**  
   Upstream URL + commit SHA: `gaia/cv/origins.csv`

2. **Immutable snapshots**  
   Vendored artifacts stored reproducibly (Git LFS where needed): `gaia/cv/source_archives/`, `gaia/cv/sources/`

3. **File-level hashes**  
   Every ingested file is hashed: `gaia/cv/checklist.csv`

4. **Per-source manifests**  
   Provenance, counts, license evidence pointers: `gaia/cv/manifests/*.json` and `gaia/cv/inventory.json`

5. **Explicit semantic entrypoints**  
   We do not pretend every file is canonical. Entrypoints are declared: `gaia/ontology/canonical/index.yaml`

6. **Repeatable validation + reports**  
   We publish evidence outputs under version control: `gaia/reports/`

This is how the commons stops being a pile of files and becomes a substrate for shared, inspectable intelligence.

---

## 3) How GAIA integrates with the SocioProphet stack

GAIA is the **semantic + provenance substrate** that other SocioProphet components can rely on without guesswork.

### 3.1 TriRPC (tritrpc) as the deterministic action transport

TriRPC gives us:
- deterministic encoding (replayable fixtures)
- authenticated envelopes
- strong boundaries between input, output, and auditability

GAIA provides the content and semantics that “ride” inside those envelopes.

So GAIA “Actions” become portable RPC contracts:
- inputs are typed and provenance-linked (which sources, which SHAs, which entrypoints)
- outputs are attributable and checkable (reports, deltas, validation results)
- runs are replayable when fixtures are preserved

### 3.2 Capability descriptors (CapD) and registries

GAIA work should be representable as capabilities so it can be composed safely:

- `caps.gaia.validate@x.y.z` — run graph/shape validation and emit auditable reports
- `caps.gaia.materialize@x.y.z` — build canonical graph snapshots from entrypoints
- `caps.gaia.tiles@x.y.z` — generate map tile products with provenance
- `caps.gaia.region_agg@x.y.z` — aggregate indicators by boundaries / regions
- `caps.gaia.geocode_audit@x.y.z` — audit geocoding correctness + drift

Each capability must reference:
- the CV source set (pinned SHAs + hashes)
- the canonical entrypoints
- the validation constraints
- the policy guardrails governing allowable actions

### 3.3 Semantic OS / governance layer

GAIA emits **policy-relevant evidence** as first-class output:
- what we used (inputs + provenance)
- what we asserted (derived indicators)
- what is uncertain (hypotheses vs facts)
- what changed (deltas)
- what was blocked (guardrails)

This is the difference between “modeling” and “responsible stewardship.”

---

## 4) Guardrails (non-negotiable)

GAIA is **not** a covert tracking platform.

We explicitly design against:
- covert individual surveillance
- doxxing / intimidation
- unlawful monitoring
- weaponized targeting

We prefer:
- public, consented, or appropriately aggregated data
- explicit uncertainty labeling
- policy + audit logs as first-class outputs

See: `docs/RESPONSIBLE_USE.md`.

---

## 5) Practical starting points

- CV provenance: `gaia/cv/origins.csv`
- Manifests: `gaia/cv/manifests/`
- Hashes: `gaia/cv/checklist.csv`
- Storage policy: `docs/CV_STORAGE_POLICY.md`
- Current entrypoint report: `gaia/reports/issue-001_entrypoints_report.md`

