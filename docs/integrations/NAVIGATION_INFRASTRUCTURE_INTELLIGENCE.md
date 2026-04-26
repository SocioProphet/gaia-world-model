# Navigation + Transportation Infrastructure Intelligence

Status: v0 integration strategy

## Purpose

GAIA should support proper navigation services and transportation infrastructure intelligence across roads, rail, bridges, stations, depots, ports, airports, transit corridors, and multimodal travel networks.

This is not just routing. It is an evidence-backed transportation digital twin that combines:

- OSM and public transport network topology;
- GTFS/NeTEx/transit schedules where available;
- LiDAR point clouds and imagery;
- HD map features;
- corridor scans;
- field events from OFIF;
- local state samples from Lampstand;
- model/runtime provenance from Lattice Forge;
- search/discovery through Sherlock;
- governance and fleet state through SocioSphere.

## Reference systems and market signals

Current industry efforts show the shape of the domain:

- rail LiDAR/corridor platforms such as Cordel;
- road HD-map platforms such as Nexar and Jakarto;
- rail corridor LiDAR/perception efforts such as Sotereon.AI + Brightline;
- inspection systems such as Tetra Tech RailAI CrossVu;
- transportation asset inspection platforms covering rail, roads, bridges, and airports.

These systems prove demand for continuous corridor perception, HD mapping, geometry extraction, clearance assessment, vegetation/encroachment analysis, asset inventory, and maintenance prioritization.

GAIA should learn from the category while remaining open, provenance-first, and stack-aligned.

## Core doctrine

```text
Transportation observation or map source
  -> Gaia transport asset catalog
  -> topology / route graph / corridor geometry
  -> LiDAR / imagery / point-cloud evidence
  -> asset condition + clearance + risk models
  -> multimodal routing / navigation services
  -> decision cards and map layers
  -> Sherlock discovery records
  -> Lattice Forge reproducible runtimes
```

## Domain boundaries

| Capability | Authority |
| --- | --- |
| World model and transport asset graph | GAIA |
| Local file/state sampling | Lampstand |
| Field observation events | OFIF |
| Runtime/build/model provenance | Lattice Forge |
| Discovery/search | Sherlock Search |
| Fleet/workspace/governance | SocioSphere |
| Edge/host lifecycle | SourceOS / nlboot |

## Data families

### Network topology

- OSM roads, paths, crossings, restrictions;
- OSM rail lines, stations, platforms, crossings, signals where available;
- GTFS static and realtime;
- NeTEx / Transmodel where available;
- agency feeds;
- traffic/closure feeds;
- timetable and headway data;
- bike/pedestrian accessibility networks.

### Corridor evidence

- mobile LiDAR;
- terrestrial LiDAR;
- trainborne LiDAR;
- aerial/drone LiDAR;
- imagery and video;
- photogrammetry;
- point clouds;
- asset inventories;
- clearance envelopes;
- vegetation/encroachment;
- bridge/track/road condition reports.

### Navigation and operations context

- travel-time observations;
- speed profiles;
- delay patterns;
- disruption events;
- weather and hazard context;
- maintenance windows;
- construction zones;
- incident reports;
- accessibility state;
- safety constraints.

## Navigation service layers

### 1. Base routing graph

A routable graph built from OSM, transit feeds, agency data, and internal curated corrections.

Possible engines to interoperate with:

- Valhalla;
- OSRM;
- GraphHopper;
- OTP/OpenTripPlanner;
- pgRouting;
- RAPTOR-style transit routing.

GAIA should not hardcode one engine as the only truth. It should define a route graph and route result contract.

### 2. HD infrastructure layer

High-detail lane/corridor/track/station/asset geometry derived from LiDAR and imagery.

Targets:

- road lane geometry;
- signs/signals/markings;
- rail centerline and trackside assets;
- bridge and tunnel clearances;
- platform/station geometry;
- vegetation/encroachment;
- grade/slope/curvature;
- risk or maintenance features.

### 3. Dynamic condition layer

Live or recent state:

- closures;
- service disruptions;
- delays;
- weather/hazard impacts;
- temporary speed restrictions;
- maintenance state;
- field-observed anomalies;
- confidence and freshness.

### 4. Decision and safety layer

Decision cards for:

- route advisories;
- accessibility warnings;
- clearance risk;
- maintenance prioritization;
- inspection follow-up;
- corridor degradation;
- delay explanations;
- multimodal alternatives.

## Asset object model

Initial asset classes:

- RoadSegment;
- LaneSegment;
- RailSegment;
- TrackAsset;
- BridgeAsset;
- TunnelAsset;
- StationAsset;
- PlatformAsset;
- CrossingAsset;
- SignalAsset;
- SignAsset;
- CorridorVegetationFeature;
- ClearanceEnvelope;
- SurfaceConditionFeature;
- AccessibilityFeature;
- DisruptionEvent;
- RoutePlan;
- NavigationInstruction;
- InfrastructureDecisionCard.

## LiDAR and point-cloud handling

GAIA should support point cloud assets as evidence, not just visualization.

Required metadata:

- acquisition platform;
- sensor type;
- capture time;
- trajectory / pose reference;
- coordinate reference system;
- density / resolution;
- classification status;
- derived feature outputs;
- uncertainty / accuracy;
- source hash;
- processing runtime asset;
- handling tags.

Formats to support or reference:

- LAS / LAZ;
- COPC;
- EPT;
- Potree-style tiles;
- 3D Tiles where useful;
- GeoParquet-derived feature extractions.

## Integration with OFIF

OFIF can emit field events for:

- detected road/rail obstruction;
- asset anomaly;
- sensor capture event;
- custody/tamper event for mobile sensor rig;
- link-state degradation;
- operator annotation;
- adversarial or confidence-degrading signal.

GAIA converts these into transport world-state features and route/asset risk context.

## Integration with Lampstand

Lampstand samples local transport artifacts:

- LiDAR files;
- route graph files;
- GTFS archives;
- GeoJSON/GeoParquet outputs;
- notebooks;
- model outputs;
- inspection reports;
- route advisories.

Percolation to GAIA/Sherlock/Lattice requires policy approval and redaction where needed.

## Integration with Sherlock

Sherlock should index:

- route plans;
- infrastructure assets;
- inspection reports;
- point-cloud evidence records;
- decision cards;
- disruption events;
- runtime/model artifacts.

Queries should support:

- route + time + condition;
- asset + evidence;
- H3/corridor/station scope;
- confidence/freshness;
- model/runtime provenance.

## Integration with Lattice Forge

Lattice Forge packages reproducible runtimes for:

- route graph building;
- GTFS/OSM ingestion;
- LiDAR feature extraction;
- point-cloud tiling;
- clearance analysis;
- traffic/travel-time modeling;
- multimodal routing benchmarks;
- map layer export.

## First implementation targets

1. `schemas/navigation/transport_infrastructure_asset.v1.schema.json`
2. `schemas/navigation/route_plan.v1.schema.json`
3. `schemas/navigation/lidar_corridor_observation.v1.schema.json`
4. `fixtures/navigation/rail-corridor-lidar-observation.sample.v1.json`
5. `fixtures/navigation/multimodal-route-plan.sample.v1.json`
6. Sherlock record fixture for infrastructure decision card.
7. Lattice Forge runtime fixture for route graph + LiDAR feature extraction.

## Non-goals

- Do not pretend OSM is sufficient for HD navigation.
- Do not treat LiDAR-derived features as facts without provenance and uncertainty.
- Do not provide safety-critical navigation claims without validation and policy approval.
- Do not erase accessibility, equity, or operational constraints from route decisions.
- Do not make one routing engine the sole system of record.

## Summary

GAIA should become capable of transportation intelligence: open navigation, corridor perception, LiDAR-backed infrastructure evidence, route planning, multimodal travel context, and decision support.

The map is not enough. The target is a governed transportation digital twin with search, evidence, runtime provenance, and route-aware reasoning.
