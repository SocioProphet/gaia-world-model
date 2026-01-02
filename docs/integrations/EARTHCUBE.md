# EarthCube Alignment -> GAIA World Model

EarthCube workbench loop: discover resources -> compose workflows -> assess -> run on platforms -> feed gaps back.
GAIA implements the same loop, hardened for adversarial, privacy-bounded, community-owned compute.

## Workbench loop mapped to GAIA
- Resource discovery -> semantic capability registry + trust envelope
- Solutions/workflows -> typed, contract-checked execution graphs (portable workflow IR)
- Assessment -> interop + reproducibility + policy validation (scorecards, attestations)
- Resource platforms -> federated runtime substrate (placement, scheduling, local-first storage, observability)

## What GAIA adds (citizen fog hardening)
- signed artifacts + provenance attestations
- policy-aware placement (consent, locality, risk tier)
- sandboxed execution (containers/WASM where appropriate)
- reputation + decay for untrusted resources
- offline-tolerant operation

## Enforceable specs
- Registry contract: docs/contracts/REGISTRY_CONTRACT.md
- Workflow IR: docs/workflows/WORKFLOW_IR.md
- Assessment scorecards: docs/assessment/SCORECARDS.md
