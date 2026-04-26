# Open Industrial IoT + Supply Chain Control Tower

Status: v0 successor strategy

## Purpose

This document defines how GAIA, OFIF, Lampstand, Sherlock Search, Lattice Forge, SourceOS, Agentplane, and SocioSphere should integrate into an open, forward-looking successor to IBM Watson IoT / Maximo-style asset intelligence and IBM Sterling-style supply-chain visibility/control-tower capabilities.

The goal is not to clone IBM products. The goal is to preserve the durable architecture patterns:

- connected assets;
- sensor/event ingestion;
- asset health and maintenance intelligence;
- work/order/task flows;
- supply-demand visibility;
- inventory and fulfillment state;
- disruption detection;
- control-tower decision cards;
- audit-ready evidence and provenance;
- AI-assisted operations with governed human review.

## Why successor, not direct clone

IBM Watson IoT Platform lineage has shifted toward embedded industrial capabilities, especially Maximo Application Suite and other IBM industrial solutions. The forward-looking open equivalent should be built from modern event, evidence, ontology, runtime, search, and mesh primitives.

## Stack alignment

| Capability | SocioProphet system |
| --- | --- |
| World/asset model | GAIA |
| Field/sensor event envelope | OFIF |
| Local state sampling | Lampstand |
| Search/discovery/control tower query | Sherlock Search |
| Reproducible runtimes/model pipelines | Lattice Forge |
| Host/edge boot, update, recovery | SourceOS / nlboot |
| Governed execution/replay | Agentplane |
| Composition, registration, policy gates | SocioSphere |
| Platform services and UI | prophet-platform |

## Capability families

### 1. Asset intelligence

Open Maximo-style capabilities:

- asset registry;
- asset hierarchy;
- sensor binding;
- health state;
- risk score;
- condition monitoring;
- predictive maintenance;
- work order / task recommendation;
- maintenance history;
- parts/material dependency;
- downtime and reliability metrics;
- emissions/sustainability context.

### 2. Field event intelligence

OFIF supplies:

- signed field observations;
- custody/tamper state;
- link/comms state;
- adversarial/confidence impacts;
- edge detector outputs;
- gateway health;
- operator annotations.

### 3. Supply chain / Sterling-style visibility

Open Sterling-style capabilities:

- inventory nodes;
- supply events;
- demand events;
- reservations;
- allocations;
- in-transit supply;
- supplier/customer/order context;
- fulfillment promises;
- disruption events;
- shortage/imbalance detection;
- alternate source recommendations;
- control-tower dashboards and decision cards.

### 4. Sustainability / Envizi-style evidence

Open sustainability capabilities:

- activity data capture;
- emissions factors;
- ESG data product manifests;
- supplier data evidence;
- audit-ready traceability;
- scenario forecasts;
- decarbonization planning context;
- model/card outputs tied to source evidence.

### 5. Transportation / navigation link

Navigation and infrastructure intelligence contributes:

- route/corridor availability;
- rail/road/bridge/station asset status;
- disruption and closure events;
- travel-time reliability;
- infrastructure condition evidence;
- LiDAR/point-cloud inspection evidence;
- multimodal routing constraints.

## Core data objects to add

### AssetTwinRecord

Represents a physical, digital, transport, field, or supply-chain asset.

Required concepts:

- asset ID;
- asset type;
- hierarchy parent/child refs;
- location/spatial refs;
- owner/operator;
- sensor bindings;
- current health state;
- evidence refs;
- maintenance/work refs;
- supply-chain refs;
- runtime/model refs;
- policy/handling tags.

### AssetHealthObservation

Represents condition/health evidence for an asset.

Required concepts:

- observed asset;
- observed_at / ingested_at;
- metric family;
- measurements;
- confidence;
- source event IDs;
- model version;
- custody/comms/adversarial flags;
- recommended action.

### WorkOrderCandidate

Represents a proposed action, not automatic actuation.

Required concepts:

- asset ref;
- issue/risk;
- priority;
- evidence refs;
- suggested task;
- required materials/skills;
- policy constraints;
- approval state;
- rollback/cancellation semantics.

### InventoryNodeRecord

Represents a store, depot, warehouse, vehicle, supplier, station, field cache, or other supply node.

Required concepts:

- node ID;
- node type;
- location/spatial refs;
- inventory scopes;
- capacity;
- owner/operator;
- trust/policy refs.

### InventoryEvent

Represents supply/demand movement.

Required concepts:

- item/SKU/material/asset class;
- supply or demand type;
- quantity/unit;
- node ref;
- order/reservation/allocation refs;
- timestamp;
- source system;
- confidence/provenance;
- handling tags.

### ControlTowerDecisionCard

Represents an explainable operational recommendation.

Required concepts:

- situation summary;
- affected assets/nodes/routes;
- evidence refs;
- model/runtime refs;
- confidence/uncertainty;
- recommended actions;
- policy constraints;
- human approval state;
- audit/provenance links.

## Event flow

```text
Sensor / system / file / operator event
  -> OFIF EventEnvelope or Lampstand LocalStateRecord
  -> GAIA AssetTwinRecord / InventoryEvent / WorldStateFeature
  -> model or rule evaluation via Lattice Forge runtime
  -> ControlTowerDecisionCard
  -> Sherlock discovery / dashboard query
  -> Agentplane governed execution if approved
  -> SocioSphere policy and fleet governance
```

## Open standards to align with

- OGC SensorThings and SOSA/SSN for sensor observations;
- OPC UA and W3C WoT Thing Description for industrial asset integration;
- MQTT / Sparkplug B for field telemetry patterns;
- EPCIS / GS1 where supply-chain traceability is relevant;
- PROV-O for provenance;
- DCAT / data product manifests for cataloging;
- OpenTelemetry for operational traces;
- TUF / Sigstore / SLSA / in-toto for update and runtime provenance;
- OPA/Rego or Cedar for policy decisions.

## Control tower views

Initial views:

1. Asset health and risk.
2. Field/sensor trust posture.
3. Inventory visibility and supply-demand imbalance.
4. Route/corridor disruption impact.
5. Sustainability/emissions data evidence.
6. Work order candidates and approval queue.
7. Runtime/model provenance and replay.
8. Local/mesh/cloud node health.

## AI role

AI is assistive and evidence-bound:

- summarize situation;
- classify event/asset/supply-chain anomalies;
- propose actions;
- rank risks;
- generate decision-card drafts;
- explain confidence and uncertainty;
- identify missing evidence;
- produce replayable model/run manifests.

AI does not bypass policy approval for destructive actions, work orders, procurement, route safety, or asset actuation.

## First implementation targets

1. `schemas/control-tower/asset_twin_record.v1.schema.json`
2. `schemas/control-tower/asset_health_observation.v1.schema.json`
3. `schemas/control-tower/inventory_event.v1.schema.json`
4. `schemas/control-tower/control_tower_decision_card.v1.schema.json`
5. `fixtures/control-tower/navigation-asset-health-card.sample.v1.json`
6. Sherlock result fixture for a control tower decision card.
7. Lattice Forge runtime fixture for control-tower anomaly scoring.
8. OFIF event fixture for an asset health observation.

## Non-goals

- Do not copy IBM proprietary product internals.
- Do not depend on discontinued Watson IoT services.
- Do not make automatic actuation the default.
- Do not treat inventory/search visibility as permission to access restricted operational data.
- Do not conflate asset state with model confidence.

## Summary

The open successor to Watson IoT / Maximo / Sterling is a governed operational digital twin:

- GAIA models assets, routes, inventory, and world state;
- OFIF emits trusted field events;
- Lampstand samples local state;
- Lattice Forge proves runtimes;
- Sherlock discovers evidence and decisions;
- SourceOS and Agentplane run governed edge/agent operations;
- SocioSphere enforces registration, composition, policy, and promotion.
