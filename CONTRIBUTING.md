# Contributing

We welcome issues and PRs.

## Development setup
- This repo uses Git LFS for large, immutable CV artifacts.

```bash
git lfs install
git lfs pull
```

## What we require for new CV sources
When adding a new upstream source to the Curation Vault (gaia/cv):
1. Pin provenance: add upstream URL + commit SHA to gaia/cv/origins.csv
2. Snapshot content into gaia/cv/source_archives/ and/or gaia/cv/sources/
3. Regenerate:
   - gaia/cv/manifests/*.json
   - gaia/cv/checklist.csv
   - gaia/cv/inventory.json
4. Ensure licensing evidence is recorded in the per-source manifest
5. If artifacts are large (zip/obo/owl), they must be tracked by LFS

## PR hygiene
- Keep normal git lean; large artifacts belong in LFS (see docs/CV_STORAGE_POLICY.md)
- Prefer small, reviewable commits with clear messages
- If you change provenance or ingestion outputs, include a short note in docs/RELEASES.md

## Code of conduct
Be civil. Assume good faith. Focus on evidence and reproducibility.
