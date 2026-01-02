# Attribution Policy

GAIA is MIT-licensed **only for original work created in this repository**.
Third-party sources (ontologies, datasets, code, documentation) retain their original licenses.

## Rules we follow

1) **Everything we ingest goes into the CV**
   - Raw source: `gaia/cv/sources/<source_id>/...`
   - Manifest: `gaia/cv/manifests/<source_id>.yaml`
   - File-level hash index: `gaia/cv/checklist.csv`

2) **No silent imports**
   - Canonical ontology entrypoints must be explicitly selected into `gaia/ontology/canonical/`.
   - The canonical index must record:
     - source id
     - upstream license identifier + evidence file path(s)
     - selected entrypoints
     - import order / dependencies

3) **Attribution is continuous**
   - Any derived artifact (processed datasets, merged ontologies, validations) must include:
     - upstream source references
     - transformation steps
     - hashes / merkle roots where feasible

## Where attribution lives

- `THIRD_PARTY_NOTICES.md` (human-readable)
- `gaia/cv/` (machine-readable provenance)
- `docs/INTEGRATION_LOG.md` (development narrative)

## License hygiene

- Do not copy third-party files into “GAIA original” directories without preserving license headers/notices.
- If in doubt, keep the file under `gaia/cv/sources/` and reference it from canonical indices rather than duplicating it.
