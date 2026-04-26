# Princeton PlanetLab Successor Strategy

Status: v0 reference integration and successor strategy

## Upstream reference

Reference system: Princeton PlanetLab / PlanetLab Consortium

PlanetLab was a global research network for planetary-scale services, distributed systems, overlays, distributed storage, content distribution, DHTs, query processing, and network telemetry. The current Princeton site is a static archive of the original PlanetLab web site.

## Decision

Do not integrate PlanetLab as an active dependency.

Use PlanetLab as a design predecessor for SocioProphet's local-first / mesh-first / cloud-twin / cloud-mesh architecture.

PlanetLab teaches how to operate distributed research infrastructure with slices, node governance, telemetry, acceptable-use policies, and real-world network conditions. SocioProphet should modernize those lessons into governed agentic mesh execution, SourceOS fleet management, OFIF field intelligence, GAIA world modeling, Lampstand local sampling, Sherlock discovery, and Lattice Forge runtime provenance.

## What PlanetLab contributes conceptually

PlanetLab's durable ideas:

- globally distributed nodes;
- slices as isolated resource allocations across many machines;
- overlay-network experimentation;
- deployment path from prototype to long-running service;
- node health monitoring;
- traffic accountability;
- acceptable-use and hosting policies;
- software package for private PlanetLabs;
- measurement from many vantage points;
- testbed plus deployment platform duality.

## Why not adopt it directly

PlanetLab is historically important but not the implementation substrate we need:

- the Princeton site is now an archive;
- original deployment assumptions predate modern container, microVM, Nix, SBOM, SLSA, OIDC, confidential computing, and cloud-native observability practices;
- slice isolation needs to be reinterpreted through modern SourceOS / agentplane isolation profiles;
- telemetry needs to be evidence-grade and linked to governance artifacts;
- runtime provenance needs Lattice Forge-style lockfiles, SBOMs, signatures, scans, and promotion evidence.

## SocioProphet successor doctrine

```text
PlanetLab slice concept
  -> SourceOS / agentplane governed workspace or agent slice
  -> Lattice Forge runtime asset
  -> Lampstand local state sampler
  -> OFIF field event layer where sensors/edge nodes participate
  -> GAIA world-state / scenario / evidence graph
  -> Sherlock discovery and audit search
  -> SocioSphere governance and fleet registration
```

## Mapping: PlanetLab to SocioProphet

| PlanetLab concept | SocioProphet successor |
| --- | --- |
| Node | SourceOS-managed host / edge node / cloud twin node |
| Slice | Governed workspace, agent cell, or microVM/container allocation |
| MyPLC private PlanetLab | SourceOS local mesh / org mesh deployment |
| Bootstrapping nodes | nlboot / SourceOS BootReleaseSet / recovery environment |
| Node health views | Lampstand local health + SocioSphere fleet status |
| PlanetFlow traffic accountability | OFIF/agentplane/network telemetry with evidence IDs |
| CoMon / CoTop / SliceStat | local + mesh observability records and Sherlock-indexed status |
| SWORD resource discovery | Sherlock + SocioSphere resource discovery |
| Acceptable-use policy | PolicyBundle + capability manifests + audit envelopes |
| Overlay service deployment | Agentplane + Lattice Forge runtime promotion |
| Network measurement | OFIF link-state events + GAIA communications availability layers |

## Required successor primitives

### 1. MeshNodeRecord

A registered host, edge device, VM, cloud twin, or recovery node.

Fields:

- node ID;
- public key / identity claim;
- platform adaptation layer;
- SourceOS release set;
- policy bundle;
- health status;
- capabilities;
- location / network region where allowed;
- trust and attestation state.

### 2. SliceAllocationRecord

A governed allocation of compute/network/storage/runtime capacity.

Fields:

- slice ID;
- owner/project/org;
- isolation profile;
- runtime asset ID;
- policy bundle;
- resource limits;
- allowed network scopes;
- evidence/provenance refs;
- expiration / renewal policy.

### 3. MeshTelemetryEnvelope

PlanetLab-style telemetry modernized for evidence and governance.

Fields:

- node ID;
- slice ID;
- observed_at / ingested_at;
- metric family;
- measurements;
- producer identity;
- integrity hash/signature;
- handling tags;
- policy ref;
- Sherlock search/discovery refs.

### 4. MeshExperimentManifest

A reproducible distributed experiment or deployment plan.

Fields:

- experiment ID;
- purpose;
- node selector;
- slice/runtime requirements;
- Lattice Forge runtime assets;
- GAIA/OFIF data bindings;
- expected evidence outputs;
- rollback strategy;
- acceptable-use policy binding.

## Integration with current work

### GAIA

GAIA receives mesh telemetry and field observations as world-state evidence. Network geography, edge availability, field sensor status, and distributed model outputs become spatial/temporal context.

### OFIF

OFIF owns field events and link-state/custody/adversarial observations. PlanetLab-style network telemetry becomes OFIF events where it concerns field/edge operations.

### Lampstand

Lampstand samples local node state and produces local-state records. These percolate upward only through policy-controlled envelopes.

### Sherlock Search

Sherlock indexes mesh nodes, slice records, telemetry, runtime assets, experiments, and decision cards for discovery and audit.

### Lattice Forge

Lattice Forge packages every distributed runtime used in a mesh experiment or deployment, including SBOMs, lockfiles, signatures, scans, and promotion evidence.

### SourceOS / nlboot

SourceOS and nlboot provide boot, recovery, enrollment, update, rollback, and local-first mesh node lifecycle management.

### SocioSphere

SocioSphere should own composition, validation, governance gates, workspace/fleet registration, and policy conformance across mesh nodes and slices.

## Modern design target

Build a **SocioProphet MeshLab** capability:

- local-first;
- opt-in;
- policy-governed;
- agentic;
- source-available;
- reproducible;
- mesh-ready;
- audit-first;
- able to run on local host, local mesh, cloud twin, and cloud mesh.

This is the modern successor to PlanetLab's testbed plus deployment-platform duality.

## Non-goals

- Do not resurrect legacy PlanetLab infrastructure as-is.
- Do not rely on archived PlanetLab services.
- Do not allow unmanaged slices.
- Do not let distributed execution bypass SourceOS / agentplane / policy boundaries.
- Do not treat search, telemetry, or runtime metadata as permission to access raw data.

## First implementation targets

1. `schemas/mesh/mesh_node_record.v1.schema.json`
2. `schemas/mesh/slice_allocation_record.v1.schema.json`
3. `schemas/mesh/mesh_telemetry_envelope.v1.schema.json`
4. `schemas/mesh/mesh_experiment_manifest.v1.schema.json`
5. `fixtures/mesh/soil-intelligence-mesh-experiment.sample.v1.json`
6. Sherlock search fixture for a mesh experiment record.
7. Lattice Forge runtime fixture for a distributed GAIA/OFIF bridge runtime.

## Summary

CyberConnector informs Gaia's Earth-science model validation surface. PlanetLab informs SocioProphet's planetary-scale mesh execution and governance surface.

The right move is not to adopt old systems. The right move is to preserve their strongest ideas and rebuild them as modern, governed, reproducible, local-first and mesh-first infrastructure.
