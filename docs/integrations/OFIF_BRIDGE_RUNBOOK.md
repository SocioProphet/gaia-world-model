# OFIF Bridge Runbook

Status: v0 proof path

## Purpose

This runbook proves the first GAIA ↔ OFIF integration path:

OFIF ObservationEvent envelope → GAIA world-state/evidence artifact → soil-intelligence decision card.

## Inputs

- `fixtures/ofif/observation-event.sample.v1.json`
- `contracts/mappings/ofif-to-gaia.v1.json`
- `docs/integrations/OFIF_INTEGRATION.md`

## Bridge command

From the repository root:

```bash
python3 scripts/ofif_to_gaia_bridge.py \
  fixtures/ofif/observation-event.sample.v1.json \
  /tmp/gaia-ofif-output.json
```

Expected output:

```text
wrote /tmp/gaia-ofif-output.json
```

## Expected derived artifact shape

The bridge emits a `gaia.world_state_feature.from_ofif_observation` artifact containing:

- `source_event_ids`
- `world_state_feature`
- H3 spatial index
- optional GeoJSON point
- observed and ingested timestamps
- environmental observation context
- detections
- link state
- custody state
- provenance
- integrity
- classification
- adversarial metadata
- derived confidence
- invariants

A committed sample target is available at:

- `fixtures/gaia/ofif-observation-world-state.sample.v1.json`

## Decision-card fixture

The first evidence-backed decision card is available at:

- `fixtures/gaia/decision-cards/soil-intelligence-decision-card.sample.v1.json`

It proves that the integration can cite:

- OFIF event IDs;
- GAIA feature IDs;
- model version IDs;
- confidence adjustments;
- custody/comms context;
- policy constraints.

## Required invariants

1. Raw OFIF events are not mutated by GAIA bridge output.
2. Source event IDs are preserved.
3. `observed_at` and `ingested_at` remain distinct.
4. Provenance, integrity, classification, and adversarial metadata survive the transform.
5. Derived confidence never overwrites raw detection confidence.
6. Decision cards cite evidence IDs and model/version IDs.

## Next implementation step

Add a CI check that runs the bridge against the fixture and compares structural invariants. Exact timestamp comparison should be avoided because `created_at` is produced at run time.
