# ISSUE-004: Executable pipelines for actions: tiles, geocoding audit, raster indices, region aggregation

**Labels:** actions, pipelines, v0.11

**Goal:** Convert action templates into runnable pipelines (even minimal).

**Acceptance:**
- `scripts/run_action.py` executes selected templates with parameters
- Outputs include provenance + hashes
- Example: OpenMapTiles build with pinned container digests
