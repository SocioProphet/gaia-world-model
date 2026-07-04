# GAIA Identifier Profile v1

This profile narrows the existing registry `id` concept into stable identifiers used by GAIA layer, event, policy, workflow, and generated-report artifacts.

## Purpose

The profile exists so that GAIA artifacts can be joined without relying on prose, filenames, spreadsheet rows, or manually copied URLs. Every generated report, workflow run, layer query, and policy decision should carry identifiers that are stable, namespaced, and machine-checkable.

## Identifier rules

- Identifiers MUST be stable once published.
- Identifiers MUST be namespaced by domain or artifact family.
- Identifiers SHOULD be lowercase.
- Identifiers SHOULD use UUIDv7, ULID, or a deterministic content hash where time ordering or reproducibility matters.
- Identifiers MUST NOT encode secrets, credentials, access tokens, or private personal data.
- Identifiers MAY include human-readable prefixes when this improves reviewability.

## Canonical fields

| Field | Meaning | Example namespace |
|---|---|---|
| `artifact_ref` | Stable pointer to a generated artifact or manifest bundle | `gaia:artifact:` |
| `dataset_id` | Stable dataset identity independent of a specific version | `gaia:dataset:` |
| `layer_id` | Stable spatiotemporal layer identity | `gaia:layer:` |
| `layer_version_id` | Versioned layer artifact or manifest | `gaia:layer-version:` |
| `event_id` | Immutable event-envelope identity | `gaia:event:` |
| `run_id` | Workflow/action/query run identity | `gaia:run:` |
| `policy_id` | Policy or policy profile identity | `gaia:policy:` |
| `policy_decision_ref` | Audit pointer to a policy decision | `gaia:policy-decision:` |
| `work_item_id` | Work item, issue, request, or task identity | `gaia:work-item:` |
| `engagement_id` | Operational engagement or bounded collaboration identity | `gaia:engagement:` |

## Relationship to existing registry contract

This profile does not replace the Registry Contract. It specializes the `id`, `version`, `content_hash`, `origin`, `lineage`, `policy`, and `attestations` fields for GAIA-generated artifacts and PAIRS-like spatiotemporal layer workflows.

## Validation posture

Each identifier-bearing example SHOULD validate against `schemas/jsonschema/core/identifier-profile.v1.schema.json` directly or through a higher-level schema that imports the same field constraints.
