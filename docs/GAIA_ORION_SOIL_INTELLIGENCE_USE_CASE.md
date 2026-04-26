# GAIA + Orion Soil Intelligence Use Case

Status: v0 flagship integration scenario

## Objective

Build the first flagship GAIA + OFIF integration around soil intelligence: estimating, forecasting, and explaining soil temperature and related soil-state indicators by fusing Earth-observation context with local field observations.

This use case proves the core doctrine:

- satellite and reanalysis data provide broad spatial/temporal coverage;
- OFIF field events provide local truth, custody, communications, and sensor-fusion context;
- GAIA integrates both into a provenance-backed world model, map layer, model output, and decision card.

## Core question

For a selected field, property, H3 cell set, watershed, farm, parcel, or ecological area:

- What is the estimated soil temperature now?
- What is the forecast over the next horizon?
- What is the uncertainty?
- Which evidence supports the estimate?
- Which local observations are trustworthy enough to calibrate the model?
- What operational decision follows from the result?

## GAIA data inputs

Initial GAIA-side source families:

- satellite land-surface temperature;
- soil moisture products;
- weather/reanalysis products;
- vegetation indices;
- elevation, slope, aspect;
- land cover;
- soil taxonomy;
- precipitation;
- snow and irrigation indicators where available;
- OSM/contextual geography for roads, parcels, waterways, and nearby assets.

## OFIF data inputs

Initial OFIF-side source families:

- ObservationEvent envelopes;
- local temperature/moisture observations;
- camera or multimodal detections;
- gateway and link-state events;
- custody/tamper/calibration metadata;
- adversarial indicators affecting observation confidence;
- derivation events from local/edge models.

## Required outputs

The v0 use case must emit:

1. A soil state feature layer keyed by H3 and time.
2. A map/tile layer for estimated soil temperature and confidence.
3. A model-run manifest with source data IDs, model version, run time, and parameters.
4. A decision card with evidence IDs and model IDs.
5. A validation report comparing model output against held-out or later-arriving OFIF observations.

## Minimal model ladder

Start conservative and measurable:

1. Baseline physical/statistical model.
2. Gradient boosting or random forest over engineered geospatial features.
3. Temporal model with weather/reanalysis sequence inputs.
4. Hybrid model with local OFIF calibration.
5. Physics-informed or graph/transformer model only after baseline evidence exists.

## Evidence requirements

Every output must preserve:

- source dataset IDs;
- OFIF event IDs;
- H3 cells and original coordinates;
- model version IDs;
- confidence and uncertainty values;
- custody and adversarial degradation signals;
- provenance references and content hashes where available.

## Decision-card template

A soil intelligence decision card includes:

- scope: area, H3 cells, time interval, scenario ID;
- observation summary;
- model estimate;
- forecast horizon;
- uncertainty interval;
- confidence explanation;
- field evidence IDs;
- satellite/reanalysis source IDs;
- custody/comms concerns;
- suggested action;
- policy constraints;
- audit/provenance links.

## Demo path

The first working demo should:

1. Ingest one OFIF observation event with location, environment, media/detection metadata, link state, and custody state.
2. Bind it to a GAIA H3 cell and world-state feature.
3. Attach at least one satellite/reanalysis context placeholder or fixture.
4. Produce a soil-state estimate fixture with uncertainty.
5. Render a map layer contract.
6. Generate a decision card.

## Non-goals for v0

- No black-box foundation model without a baseline.
- No claim of agronomic correctness without validation.
- No destructive or autonomous field actuation.
- No erasure of raw event provenance.
