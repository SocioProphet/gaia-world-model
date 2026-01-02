# CV Storage Policy

We keep GAIA's Curation Vault (CV) reproducible and attributable while preserving repo usability.

## What lives in normal git
- `gaia/cv/origins.csv` (pinned upstream URLs + commit SHAs)
- `gaia/cv/manifests/*.json` (per-source provenance + license evidence pointers)
- `gaia/cv/checklist.csv` (file-level hashes)
- `gaia/cv/inventory.json` (source inventory summary)

## What lives in Git LFS
Large immutable artifacts:
- `gaia/cv/source_archives/*.zip`
- large ontology/data artifacts (currently tracked): `*.zip`, `*.obo`, `*.owl`

## Rationale
- Normal git stays fast for clones, PRs, and CI.
- LFS preserves exact artifacts without hitting GitHub size recommendations.
- Provenance remains checkable from hashes/manifests even without fetching all LFS blobs.

## Notes
If LFS becomes undesirable, we can move `source_archives/` to GitHub Release assets while keeping manifests + hashes in normal git.
