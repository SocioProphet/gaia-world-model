# GAIA State-of-the-Art Integration Map

Status: v0 integration map
Date: 2026-04-26

## Purpose

This document consolidates the predecessor systems, open standards, active open-source projects, institutional programs, and SocioProphet workstreams that GAIA should integrate with or learn from.

The rule is not "adopt everything." The rule is:

1. Learn from mature systems.
2. Integrate with open standards where they reduce lock-in.
3. Use SocioProphet-native contracts where we need cross-domain evidence, governance, runtime provenance, and agentic execution.
4. Never collapse authority boundaries between world model, field events, runtime provenance, search, local state, and governance.

## SocioProphet-native authority map

| Capability | Authority |
| --- | --- |
| World model / geospatial / simulation / evidence | GAIA |
| Field events / sensor fusion / custody / comms / adversarial context | OFIF |
| Local state sampling and percolation | Lampstand |
| Search and discovery | Sherlock Search |
| Runtime/build/model provenance | Lattice Forge |
| Graph-native agent operation | MeshRush |
| Governed execution/replay | Agentplane |
| Host lifecycle / boot / recovery / update | SourceOS / nlboot |
| Governance / composition / fleet registration | SocioSphere |
| Platform services and control surfaces | prophet-platform |

## 1. Cloud-native geospatial and Earth observation

### Standards and projects

- STAC
- Cloud Optimized GeoTIFF
- Zarr
- NetCDF
- GRIB/GRIB2
- GeoParquet
- Apache Arrow / GeoArrow
- Open Data Cube
- Pangeo / Xarray / Dask
- Intake / Intake-STAC
- Kerchunk
- THREDDS / ERDDAP
- Rasdaman
- TileDB

### SocioProphet integration

GAIA owns catalog and data-cube semantics. Lattice Forge owns runtimes for processing. Sherlock indexes derived discovery records. Lampstand samples local files. OFIF contributes field observations.

### Required contracts

- `DataProductManifest`
- `CoverageAssetRecord`
- `STACBindingRecord`
- `DataCubeProductManifest`
- `GeoParquetFeatureSetManifest`

## 2. OGC and geospatial interoperability

### Standards

- OGC API - Features
- OGC API - Tiles
- OGC API - Processes
- OGC API - Records
- OGC API - Coverages / EDR where applicable
- OGC SensorThings API
- GeoSPARQL
- SOSA / SSN

### SocioProphet integration

GAIA Actions should expose OGC Processes-compatible operations. OFIF events should map to SensorThings/SOSA observation structures where useful. Gaia spatial entities should map to GeoSPARQL where RDF/semantic reasoning is needed.

### Required contracts

- `OGCProcessBinding`
- `SensorThingsBinding`
- `GeoSPARQLBinding`
- `CoverageTileManifest`

## 3. EO processing APIs and model validation

### Reference systems

- openEO
- Google Earth Engine
- Microsoft Planetary Computer
- NASA MAAP
- ESA openEO platform
- Digital Earth Africa / Australia
- CyberConnector / COVALI

### SocioProphet integration

CyberConnector/COVALI is a predecessor for model/data comparison, NetCDF/GRIB visualization, regridding, and scientific operators. Gaia should build a modern Gaia Model Validation Surface instead of adopting the old Tomcat/ncWMS stack.

### Required contracts

- `ModelValidationReport`
- `RegridRunManifest`
- `ScientificOperatorRunManifest`
- `CoverageStatisticsReport`

## 4. Geospatial and EO foundation models

### Reference models and efforts

- Prithvi
- TerraMind
- Clay
- SatMAE
- Scale-MAE
- DOFA
- Galileo
- other EO/multimodal remote-sensing foundation models

### SocioProphet integration

GAIA tracks models and tasks. Lattice Forge packages inference runtimes. Sherlock indexes model cards and run outputs. OFIF field observations calibrate or validate model outputs where applicable.

### Required contracts

- `FoundationModelRecord`
- `ModelCard`
- `ModelRunManifest`
- `FeatureSetManifest`
- `ValidationSplitManifest`

## 5. Institutional Earth digital twins and domain twins

### Reference programs

- Destination Earth
- NASA / ESA digital twin programs
- national digital twin programs
- climate twins
- urban flood twins
- heat/thermal comfort twins
- infrastructure twins

### SocioProphet integration

GAIA should define domain twin templates rather than one monolithic twin. Each domain twin has data products, models, actions, evidence, uncertainty, map surfaces, and decision cards.

### Domain twin templates

- soil
- flood
- heat
- wildfire
- crop
- watershed
- mobility
- transportation infrastructure
- grid
- water
- telecom
- facility
- supply chain

### Required contracts

- `DigitalTwinCapabilityProfile`
- `DomainTwinTemplate`
- `ScenarioBranch`
- `SimulationRunManifest`

## 6. Hydrology, environment, climate, and engineering models

### Reference model families

- HEC-RAS
- SWAT / SWAT+
- WRF-Hydro
- LISFLOOD-FP
- MODFLOW
- Delft3D
- SUMMA
- Noah-MP
- CLM / CTSM
- Landlab
- ESMF / ESMPy
- CUAHSI / HydroShare patterns
- BMI model interface patterns

### SocioProphet integration

GAIA owns model semantics and validation outputs. Lattice Forge packages runtimes. Agentplane executes approved runs. Sherlock indexes results. MeshRush reasons over graph outputs.

### Required contracts

- `EnvironmentalModelAdapterRecord`
- `ModelInputRequirement`
- `CalibrationStateRecord`
- `UncertaintyMethodRecord`

## 7. Navigation and transportation intelligence

### Reference categories

- Valhalla
- OSRM
- GraphHopper
- OpenTripPlanner
- pgRouting
- GTFS / GTFS-Realtime
- NeTEx / Transmodel
- road HD-map platforms
- rail LiDAR/corridor perception platforms
- bridge/station/track asset inspection systems

### SocioProphet integration

GAIA owns transport asset graph, route plan contracts, LiDAR/corridor observations, route evidence, and decision cards. OFIF emits field/navigation anomaly events. Lattice Forge packages routing and LiDAR extraction runtimes. Sherlock indexes routes and infrastructure evidence.

### Current contracts

- `schemas/navigation/transport_infrastructure_asset.v1.schema.json`
- `schemas/navigation/route_plan.v1.schema.json`
- `schemas/navigation/lidar_corridor_observation.v1.schema.json`

### Required next contracts

- `InfrastructureDecisionCard`
- `NavigationSafetyCase`
- `RouteValidationRecord`
- `ClearanceValidationRecord`

## 8. Industrial IoT, asset management, and control towers

### Reference categories

- Watson IoT / Maximo-style connected asset management
- Sterling-style inventory/order/supply-chain visibility
- Envizi-style sustainability evidence
- ISO 55000 / 55001 / 55002 asset management
- Digital Twin Consortium capability framework
- OPC UA
- W3C Web of Things
- MQTT / Sparkplug B
- GS1 / EPCIS
- EDI / X12 / EDIFACT concepts

### SocioProphet integration

GAIA owns asset twins, inventory events, control tower decision cards, and world-state semantics. OFIF emits field/sensor events. Lampstand samples local files and exports. Lattice Forge owns runtimes. Sherlock owns discovery. SocioSphere owns governance.

### Required contracts

- `AssetTwinRecord`
- `AssetHealthObservation`
- `WorkOrderCandidate`
- `InventoryNodeRecord`
- `InventoryEvent`
- `ControlTowerDecisionCard`
- `RiskExposureRecord`
- `ComplianceRequirement`

## 9. Mesh, edge, home IoT, and distributed execution

### Reference systems

- Princeton PlanetLab
- Tinkerbell
- ioFog
- KubeEdge
- OpenYurt
- Open Horizon
- Home Assistant
- Matter
- Thread
- Zigbee / Z-Wave bridges
- MQTT
- NATS / Redpanda / Kafka for streams

### SocioProphet integration

PlanetLab informs MeshLab. KubeEdge is optional for Kubernetes-native edge fleets. Home Assistant/Matter/Thread represent the local-first home/facility IoT fabric. SourceOS/nlboot owns host lifecycle. SocioSphere governs nodes/fleets. OFIF wraps events. GAIA models assets/world state. MeshRush reasons over graph views.

### Required contracts

- `MeshNodeRecord`
- `SliceAllocationRecord`
- `MeshTelemetryEnvelope`
- `MeshExperimentManifest`
- `HomeFabricRecord`
- `DeviceTwinRecord`
- `AutomationPolicyRecord`

## 10. Workflow, reproducibility, and model operations

### Reference systems

- Snakemake
- Nextflow
- CWL
- WDL
- Argo Workflows
- Flyte
- Prefect
- Dagster
- MLflow
- DVC
- Pachyderm
- Feast
- OpenLineage / Marquez
- DataHub / OpenMetadata
- LakeFS / Iceberg / Delta / Nessie

### SocioProphet integration

Lattice Forge owns reproducible runtimes. Agentplane executes and replays. GAIA owns scientific/domain action semantics. Sherlock indexes outputs. SocioSphere gates promotion.

### Required contracts

- `RuntimeAsset` already exists in Lattice Forge
- `WorkflowRunManifest`
- `EvidenceBundle`
- `ResearchObjectPackage`
- `DataProductManifest`

## 11. Knowledge graph, semantic web, and publishing

### Reference standards and systems

- W3C PROV-O
- DCAT
- schema.org
- SOSA / SSN
- GeoSPARQL
- OWL / RDF / SHACL
- LinkML
- RO-Crate
- DataCite
- ORCID
- Zenodo / OSF patterns
- Wikidata / EntitySchema
- OpenReview / PubPub / Jupyter Book

### SocioProphet integration

GAIA and OFIF evidence must be publishable, reviewable, and reproducible. Ontology changes should be proposed, validated, reviewed, and linked to evidence. Sherlock indexes research objects. Lattice Forge packages runtimes. SocioSphere governs review flows.

### Required contracts

- `ResearchObjectPackage`
- `OntologyChangeProposal`
- `EvidenceReview`
- `ModelReview`
- `DatasetReview`
- `ReproducibilityReview`

## 12. Search and retrieval

### Reference systems

- Lucene / Solr
- OpenSearch / Elasticsearch
- Vespa
- Meilisearch / Typesense
- Qdrant / Weaviate / Milvus / LanceDB
- DuckDB / Parquet
- GraphRAG patterns

### SocioProphet integration

Sherlock is a federated discovery layer, not a database. It should support lexical, semantic, graph, spatial, temporal, evidence, and runtime-aware ranking.

### Current contracts

- `SocioProphet/sherlock-search/schemas/sherlock_geospatial_result.v1.schema.json`

### Required next contracts

- `SherlockRankingEvidenceProfile`
- `SpatialTemporalQueryContract`
- `RuntimeAwareSearchRecord`

## 13. Security, identity, and supply chain

### Reference systems and standards

- Sigstore / cosign
- SLSA
- in-toto
- TUF / Uptane
- SPDX / CycloneDX
- GUAC
- OpenSSF Scorecard
- OPA / Rego
- Cedar
- SPIFFE / SPIRE
- OIDC
- TPM / FIDO / WebAuthn / passkeys
- OpenTelemetry

### SocioProphet integration

Every significant artifact should carry identity, integrity, provenance, policy, and replay hooks. SourceOS/BootReleaseSet, Lattice RuntimeAsset, OFIF EventEnvelope, GAIA EvidenceArtifact, Sherlock SearchRecord, and Agentplane execution records should converge on compatible integrity vocabulary.

### Required contracts

- `EvidenceIntegrityRecord`
- `PolicyDecisionRecord`
- `AttestationRecord`
- `OpenTelemetryEvidenceBinding`
- `SupplyChainGraphBinding`

## 14. Privacy, safety, ethics, and compliance

### Needed areas

- privacy impact assessment;
- surveillance risk classification;
- bystander privacy;
- safety cases;
- legal holds;
- retention policy;
- data processing purpose;
- exception waivers;
- audit findings;
- human approval state.

### SocioProphet integration

Privacy and safety are not afterthoughts. They are policy-bound artifacts that must travel with field imagery, local sampling, navigation decisions, asset observations, and control-tower outputs.

### Required contracts

- `PrivacyImpactAssessment`
- `SurveillanceRiskClassification`
- `BystanderPrivacyPolicy`
- `RedactionPlan`
- `UseRestrictionPolicy`
- `ApprovalRecord`
- `OverrideJustification`
- `NavigationSafetyCase`

## 15. Evaluation and benchmarks

### Needed benchmark families

- soil intelligence benchmark;
- field event trust benchmark;
- navigation routing benchmark;
- LiDAR feature extraction benchmark;
- asset health anomaly benchmark;
- inventory imbalance benchmark;
- search relevance benchmark;
- runtime reproducibility benchmark;
- mesh telemetry benchmark.

### Required contracts

- `BenchmarkManifest`
- `EvaluationRunRecord`
- `GoldenFixtureSet`

## Build priority

1. Control tower schemas.
2. Mesh / home IoT / KubeEdge schemas.
3. Model/simulation/data-product schemas.
4. Privacy/safety/evaluation schemas.
5. Cross-repo issues and validation gates.

## Summary doctrine

CyberConnector teaches model/data validation.
PlanetLab teaches slices and mesh governance.
STAC/OpenDataCube/Pangeo teach cloud-native EO.
openEO/OGC teach interoperability.
H3/GeoParquet teach scalable spatial joins.
Tinkerbell/KubeEdge/ioFog teach edge lifecycle and fleet operations.
Home Assistant/Matter/Thread teach local-first home/facility IoT.
MLflow/DVC/OpenLineage teach reproducibility.
PROV-O/GeoSPARQL/SOSA teach semantic evidence.

SocioProphet turns these into one governed platform: GAIA, OFIF, Lampstand, Sherlock, Lattice Forge, MeshRush, Agentplane, SourceOS, SocioSphere, and Prophet Platform.
