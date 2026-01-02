# Workflow IR (Discover -> Compose -> Run -> Assess)

Workflows are a typed DAG: nodes are resources (datasets/tools/models/agents), edges are typed contracts.

## Graph primitives
- Node: ref (registry id+version), role (source/transform/model/agent/sink), io (contract pointers)
- Edge: from node.output -> to node.input with a contract (schema/units/crs)
- Adapter node: schema translator, unit converter, CRS reprojection, codec bridge, auth bridge

## Execution targets
Backend-agnostic: local, citizen fog nodes, coop micro-DC, institutional cluster/HPC.

## Evidence outputs per run
Pinned inputs+env, outputs+hashes, provenance bundle, assessment scorecards, gap report on failure.
