# Runtime Boundary — GAIA Sensitive Geospatial Policy Evaluation

Status: executable fixture proof; Lattice admission candidate, not admitted
Date: 2026-04-27

## Runtime identity

Runtime name: `gaia-sensitive-geo-policy-eval-runtime`

Domain: GAIA sensitive geospatial governance / policy evaluation

Purpose: evaluate a `SensitiveGeoPolicyRecord` against a target GAIA multidomain record and emit an advisory governance artifact that declares masking, delay, access-control, audit, approval, and accountability requirements.

This runtime is a governance runtime. It does not unmask locations, restore precision, target, engage, authorize effects, or bypass policy approval.

## Standards references

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Entrypoint

`multidomain/sensitive_geo_policy_eval.py`

## Required inputs

- `SensitiveGeoPolicyRecord` JSON fixture.
- Target GAIA multidomain record fixture.
- Standards refs on policy and subject records.
- Subject governance and classification metadata.
- Sensitive geospatial policy ref.

Current fixtures:

- `fixtures/multidomain/sensitive-geo-policy.sample.v1.json`
- `fixtures/multidomain/multi-domain-fusion-event.sample.v1.json`

Negative fixtures:

- `fixtures/multidomain/negative/sensitive-policy-eval-subject-is-policy.sample.v1.json`

## Emitted outputs

- `gaia.sensitive_geo_policy_eval.output` JSON artifact.
- Policy ref and subject ref.
- Subject domain inference.
- Effective action.
- Approval-required state.
- Accountability ledger requirement.
- Authority and human-approval requirements.
- Masking, delay, access-control, and audit controls.
- Provenance with `runtime_boundary_id = runtime:sensitive-geo-policy-eval:v0`.
- Runtime evidence bundle with input/output hashes, policy posture, and replay command.

## Validation command

```bash
python3 multidomain/sensitive_geo_policy_eval.py \
  fixtures/multidomain/sensitive-geo-policy.sample.v1.json \
  fixtures/multidomain/multi-domain-fusion-event.sample.v1.json \
  /tmp/gaia-sensitive-geo-policy-eval-output.json
```

CI workflow:

- `.github/workflows/sensitive-geo-policy-runtime.yml`

## Policy constraints

- The runtime is advisory and governance-only.
- The runtime must not unmask, restore precision, or authorize action.
- Effects-linked or defense/public-safety use requires accountability ledger references before production use.
- The runtime must preserve policy refs and subject evidence refs.
- The runtime must emit approval and authority requirements when sensitive geospatial handling is triggered.
- Ungoverned effects execution remains out of scope.

## Runtime isolation default

Container for deterministic fixture processing.

VM or microVM when processing restricted, customer-owned, defense/public-safety, or effects-linked operational data.

## Network posture

Restricted / none for fixture proof.

Live policy-service mode requires explicit network posture and source allowlist.

## Secret posture

None for fixture proof.

Live private policy or identity service integration requires secret-door integration and redacted audit logs.

## Accountability posture

The runtime emits whether an accountability ledger is required. Production integration must write or reference a ledger entry when:

- the evaluated subject is defense/public-safety related;
- the evaluated subject is effects-linked;
- approval is required;
- unmasked or higher-precision geospatial access is requested;
- an advisory artifact could be mistaken for an operational command.

## Promotion criteria

The runtime may be considered for Lattice Forge admission only after:

1. executable entrypoint exists;
2. deterministic fixture proof exists;
3. CI validates output invariants;
4. malformed fixture corpus exists;
5. policy preservation is tested;
6. accountability requirements are tested;
7. runtime evidence bundle is defined;
8. replay command is documented;
9. packaging, SBOM, signing, and rollback tests exist;
10. live policy-service mode is separately scoped and governed.

## Rollback semantics

Generated policy-evaluation artifacts are versioned advisory records. Rollback demotes the generated evaluation output and restores the prior governance projection. Source policy and subject records are immutable evidence inputs.

## Current status

Executable fixture proof exists. Not admitted to Lattice Forge.
