# ISSUE-005: Integrate remote repo ingestion into CV (optional vendoring + hashing)

**Labels:** cv, provenance, v0.11

**Goal:** For referenced remote repos (OTM, Nominatim, etc.), support optional vendoring into CV with commit hash + archive hash.

**Acceptance:**
- `gaia/cv/externals/` structure and manifests for remote snapshots
- Policy: when to vendor vs reference only
