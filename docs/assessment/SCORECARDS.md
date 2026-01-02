# Assessment Scorecards (Interop + Repro + Policy)

Assessment produces structured results that can be signed and attached as attestations.

## Scorecard axes
- Interop: contract conformance (schema/unit/crs), adapter correctness, API/protocol compliance
- Reproducibility: pinned inputs+environment, re-run where possible, provenance completeness
- Policy: consent/locality compliance, least-privilege access, minimization/redaction compliance
- Operational: runtime stability, graceful degradation, observability completeness

## Minimal output shape
- artifact_ref
- run_id
- timestamp
- results[]: axis, check, status (pass|fail|warn), evidence (links/hashes/log excerpts)
- signature (optional)

## Promotion gates
Example thresholds: no FAIL on policy; interop PASS for required checks; reproducibility WARN-free for canonical promotion.
