# ISSUE-003: Upgrade license detection to evidence-backed SPDX mapping

**Labels:** governance, license, v0.10

**Goal:** Replace heuristic `license_guess` with SPDX identifiers where possible.

**Acceptance:**
- Each `gaia/cv/manifests/*.yaml` includes:
  - `license.spdx_id`
  - `license.evidence` (file path + hash)
- Add `docs/LICENSE_HYGIENE.md`
