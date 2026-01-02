# Integration Log (Narrative)

This file records *how* we’ve been developing GAIA: we integrate sources using a consistent pattern:
1) remote manifest
2) ontology extension
3) conservative alignments
4) adapters + action templates
5) curation vault (CV) ingestion with hashes + provenance

## Pattern: Source → Semantics → Actions → Audit

- **Source**: raw materials are ingested into `gaia/cv/sources/` and hashed in `gaia/cv/checklist.csv`.
- **Semantics**: domain primitives live in `gaia/ontology/domain/` and alignments in `gaia/ontology/`.
- **Actions**: `gaia/actions/templates/` defines declared objectives, constraints, risks, metrics.
- **Audit**: upcoming (v0.10): SHACL shapes + validation runs emitting machine-readable reports.

## What’s integrated so far (high-level)

- Urban forestry: OpenTreeMap (`otm-core`) → trees, plots, inspections
- Governance dynamics: Quantitative Realism → power stocks/flows; stability assessment templates
- Computational law: obligations/permissions/prohibitions → compliance checks
- Atmospheric QC: ARM-DOE ACT → timeseries QC flags and validation templates
- OSM infrastructure: `openstreetmap/chef` → cookbooks/roles/pins; deploy/backup/audit actions
- Geo stack:
  - OpenMapTiles (tilesets + layers) and MBTiles introspection
  - Nominatim (geocoding queries/results) and import adapter
  - RasterFrames (raster analytics) placeholder catalog + future Spark job templates
  - Region aggregation (GeoJSON+CSV join) adapter + planning template
