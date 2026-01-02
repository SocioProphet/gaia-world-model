# ISSUE-002: Add SHACL validation shapes and a repeatable validation runner

**Labels:** ontology, validation, v0.10

**Goal:** Create SHACL shapes for core GAIA objects and new domain modules; run validation producing reports.

**Deliverables:**
- `gaia/validation/shacl/*.ttl`
- `scripts/validate.sh` (or python runner) that emits:
  - `gaia/reports/validation/<timestamp>_report.json`
  - `gaia/reports/validation/<timestamp>_report.md`
