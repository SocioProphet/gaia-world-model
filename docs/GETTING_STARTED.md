# Getting Started

## Prerequisites
- git
- git-lfs
- python3

## Clone and fetch LFS content

    git clone https://github.com/SocioProphet/gaia-world-model.git
    cd gaia-world-model
    git lfs install
    git lfs pull

## Where to look first

CV / provenance
- gaia/cv/origins.csv
- gaia/cv/manifests/
- gaia/cv/checklist.csv
- gaia/cv/inventory.json

Ontology integration
- gaia/ontology/canonical/index.yaml
- gaia/ontology/imports_index.yaml

Reports
- gaia/reports/issue-001_entrypoints_report.md

## Typical workflow: add a new source (high level)
1. Add URL + pinned commit SHA to gaia/cv/origins.csv
2. Ingest into gaia/cv/source_archives/ and gaia/cv/sources/<SOURCE_ID>/...
3. Regenerate manifests + checklist + inventory
4. Select canonical entrypoint(s) in gaia/ontology/canonical/index.yaml
5. Add validation + import strategy iteratively (see Issues)
