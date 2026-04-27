# OpenStreetMap Integration

Status: v0 integration contract

## Purpose

OpenStreetMap is GAIA's first open base-map, feature, and topology substrate. GAIA uses OSM as a source of open geospatial features and route topology, while preserving OSM identity, attribution, and provenance.

OSM is not the canonical GAIA world model. OSM-derived features become GAIA evidence-backed spatial/entity bindings.

## Authority boundaries

| Concern | Authority |
| --- | --- |
| OSM source feature IDs and tags | OpenStreetMap source data |
| Canonical GAIA world entity IDs | GAIA |
| Field observations tied to map features | OFIF |
| Local extract sampling | Lampstand |
| Tile/routing/runtime provenance | Lattice Forge after runtime boundary |
| Search/discovery | Sherlock Search |
| Attribution/governance validation | SocioSphere |

## Integration flow

```text
OSM extract/query result
  -> OSM feature binding
  -> GAIA world/spatial entity link
  -> H3 and geometry refs
  -> map/tile/route layer manifest
  -> Sherlock discovery record
  -> SocioSphere validation gate
```

## Required invariants

1. Preserve source OSM IDs: node, way, relation.
2. Preserve source OSM tags as source metadata.
3. Do not mutate OSM refs when deriving GAIA features.
4. Derived GAIA features must cite OSM source refs.
5. OSM attribution and license metadata must travel with layers and reports.
6. OSM-only route outputs are advisory unless validated by additional evidence.
7. HD/safety-critical navigation requires LiDAR/HD-map/field validation evidence.

## Initial source forms

- `.osm.pbf` extracts;
- Overpass-style JSON/XML results;
- planet/region extracts;
- incremental diffs;
- local extracts sampled by Lampstand;
- curated internal overlays as separate GAIA layers.

## Initial target surfaces

- GAIA spatial features;
- route graph inputs;
- MapLibre vector-tile layer manifests;
- Sherlock search records;
- control-tower route/infrastructure decision cards.

## Runtime boundary

No Lattice Forge runtime asset should be added until the OSM ingestion/tile/routing executable boundary is defined.

Candidate future runtimes:

- `gaia-osm-ingestion-runtime`
- `gaia-osm-route-graph-runtime`
- `gaia-osm-tile-export-runtime`

## First proof slice

The first proof should bind a demo OSM way to a GAIA transport feature, assign H3 refs, expose a MapLibre-compatible layer manifest, and emit a Sherlock discovery record.
