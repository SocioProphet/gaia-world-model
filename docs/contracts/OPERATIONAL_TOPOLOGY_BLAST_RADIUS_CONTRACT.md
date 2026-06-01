# Operational Topology and Blast-Radius Contract v0.1

Status: contract draft  
Plane: GAIA operational topology projection  
Consumers: Prophet Platform DevSecOps Workroom, AgentPlane, Sociosphere, Guardrail Fabric

## Purpose

This contract defines the minimum GAIA record shape for operational topology and blast-radius evidence consumed by the DevSecOps Intelligence Workroom.

It extends GAIA's provenance discipline to service/runtime topology without treating operational topology as a geospatial world claim.

## Ownership

GAIA owns operational topology and blast-radius evidence projection.

Prophet Platform consumes topology and blast-radius references in Workroom records.

AgentPlane owns runtime execution and evidence production.

Sociosphere owns workspace and environment state.

Guardrail Fabric owns safety/adversarial policy fixtures.

## Core references

A Workroom incident record may reference:

```text
topology://gaia/workroom/<workspace-or-service>/<context>
blast-radius://gaia/workroom/<workspace-or-service>/<incident-or-context>
```

A GAIA topology fixture must preserve:

- topology reference;
- blast-radius reference when available;
- workspace or service context;
- environment reference;
- observed time window;
- source/provenance records;
- service nodes;
- dependency edges;
- affected consumers;
- confidence and uncertainty notes;
- non-claims.

## Minimal topology object

Required fields:

- `schema_version`;
- `topology_ref`;
- `blast_radius_ref`;
- `workspace_ref`;
- `environment_ref`;
- `observed_window`;
- `source_evidence`;
- `nodes`;
- `edges`;
- `blast_radius`;
- `policy_status`;
- `non_claims`.

## Source evidence

Each source evidence item must include:

- `evidence_ref`;
- `source_system`;
- `source_ref`;
- `observed_at`;
- `collection_method`;
- `non_claims`.

## Nodes

Each node must include:

- `node_ref`;
- `node_type`;
- `label`;
- `environment_ref`;
- `evidence_refs`.

Allowed initial node types:

- `service`;
- `deployment`;
- `database`;
- `queue`;
- `frontend`;
- `external_dependency`;
- `runtime_environment`.

## Edges

Each edge must include:

- `edge_ref`;
- `source_node_ref`;
- `target_node_ref`;
- `relation_type`;
- `evidence_refs`;
- `confidence`.

Allowed initial relation types:

- `depends_on`;
- `calls`;
- `publishes_to`;
- `reads_from`;
- `writes_to`;
- `served_by`;
- `deployed_to`.

## Blast-radius section

The `blast_radius` section must include:

- `radius_status`;
- `affected_node_refs`;
- `candidate_consumer_refs`;
- `impact_hypotheses`;
- `confidence`;
- `non_claims`.

Allowed `radius_status` values:

- `candidate_only`;
- `supported_by_topology`;
- `confirmed_by_observation`.

The initial Workroom integration should use `supported_by_topology` at most unless observational impact evidence exists.

## Policy status

Allowed initial policy statuses:

- `candidate_only`;
- `fixture_validated`;
- `runtime_observed`;
- `deprecated`.

## Workroom consumption rule

A Prophet Platform post-merge incident Workroom record may cite GAIA topology only as evidence for:

- dependency context;
- candidate blast radius;
- hypothesis generation;
- affected-service explanation.

Topology alone must not prove root cause.

## Non-claims

This contract does not execute runtime probes.

This contract does not certify RCA causality.

This contract does not authorize remediation.

This contract does not certify Signadot feature parity.

This contract does not replace AgentPlane execution receipts, Sociosphere environment state, or Prophet Platform Workroom claims.
