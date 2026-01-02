# Minimal Registry Contract (Discovery + Safe Composition)

Smallest field set required for safe discovery, composition, validation, and governance.

## 1) Identity and versioning
- id: stable identifier (namespaced)
- version: semver or pinned commit/tag
- kind: dataset | ontology | tool | model | agent | workflow
- content_hash: hash of artifact or manifest bundle
- license: SPDX identifier(s)
- attribution: source + authors + required notices

## 2) Interfaces (can we wire this?)
- inputs[]: name, schema_ref, units, crs, constraints
- outputs[]: same shape as inputs
- protocols[]: file/http/grpc/tritrpc/etc
- runtime: cpu/gpu/mem, OS constraints, container/WASM hints

## 3) Provenance (where did it come from?)
- origin: URL + pinned revision + retrieval date
- lineage: transforms applied (tool versions + hashes)
- prov_bundle: pointer to PROV / RO-Crate style packaging

## 4) Policy + placement (where may it run?)
- visibility: public | restricted | private
- consent_class: consent-bounded classification when applicable
- locality: allowed regions / must-run-local flags
- risk_tier: low/med/high
- redactions: minimization / aggregation constraints

## 5) Trust envelope (should we trust it?)
- signatures: who signed what
- attestations: signed interop/repro/policy results
- reputation: optional computed signals + decay pointer

## 6) Gap reports
On compose/validate failure, emit a Gap Analysis Report: missing metadata, missing adapter, interface mismatch, policy violation, reproducibility failure.
See docs/assessment/SCORECARDS.md.
