# Getting Started

## Prerequisites
- git
- git-lfs
- python3

## Clone and fetch LFS content

```bash
git clone https://github.com/SocioProphet/gaia-world-model.git
cd gaia-world-model
git lfs install
git lfs pull
```

## Orientation

Start with these:

**Provenance / Curation Vault (CV)**
- gaia/cv/origins.csv (upstream URLs + pinned commit SHAs)
- gaia/cv/manifests/ (per-source provenance + license evidence pointers)
- gaia/cv/checklist.csv (file-level hashes)
- gaia/cv/inventory.json (inventory summary)

**Storage policy and releases**
- docs/CV_STORAGE_POLICY.md
- docs/RELEASES.md

**Reports**
- gaia/reports/issue-001_entrypoints_report.md

## Typical workflow: add a new source (high level)
1. Add URL + pinned commit SHA to gaia/cv/origins.csv
2. Ingest snapshot under gaia/cv/source_archives/ and gaia/cv/sources/
3. Regenerate manifests + checklist + inventory
4. Produce/update reports and entrypoint recommendations under gaia/reports/
5. Tag a release when the vault state is stable
