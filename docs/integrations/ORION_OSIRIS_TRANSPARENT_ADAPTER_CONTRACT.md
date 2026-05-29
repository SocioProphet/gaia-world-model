# Orion / OSIRIS Transparent Adapter Contract

Status: adapter contract stub
Related issues:

- `SocioProphet/gaia-world-model#29`
- `SocioProphet/gaia-world-model#31`

## 1. Purpose

This contract defines how OSIRIS-discovered public feeds become Gaia-owned source adapters without importing OSIRIS route handlers or stealth/evasion behavior.

The adapter output is a `GaiaSourceRecord` or a bundle that can deterministically produce `GaiaSourceRecord` instances. Orion consumes only source-record references through Orion-owned events and markers.

## 2. Non-negotiable boundaries

Adapters must not:

- copy OSIRIS route handlers;
- use `stealthFetch`;
- randomize identity, headers, IPs, or browser fingerprints;
- require live credentials for validation;
- emit raw public-feed objects directly into Orion;
- mark public feeds as verified facts without provenance and evidence grade;
- trigger scanner, sweep, recon, or user-supplied target activity.

Adapters must:

- declare provider name and endpoint family;
- declare terms/license status;
- declare attribution requirements;
- declare rate-limit and cache/replay strategy;
- preserve observed time separately from ingested time;
- emit evidence grade and risk class;
- provide fixture-mode records;
- fail closed when required metadata is absent.

## 3. Adapter phases

### Phase 0: Candidate source record

A fixture-only `GaiaSourceRecord` records the source family, URL/API family, terms status, attribution requirement, risk class, and provenance note. No live fetch is performed.

### Phase 1: Transparent adapter stub

A small adapter module may exist, but validation must still run from fixtures only. The adapter declares fetch method, expected response family, normalization plan, and replay strategy.

### Phase 2: Recorded public fetch

A controlled public fetch may be introduced after terms/attribution review. The fetch must use a declared user agent where required and preserve a canonical response or hash.

### Phase 3: Orion event bridge

Only after Gaia records are stable may Orion create `OrionObservationEvent` instances referencing Gaia source ids.

## 4. Required adapter metadata

Each adapter must declare:

```yaml
adapter_id: string
provider_name: string
source_family: string
endpoint_family: string
terms_status: unknown | review_required | approved_for_demo | approved_for_production
attribution_required: boolean
rate_limit_strategy: string
cache_strategy: string
replay_fixture: string
output_schema: gaia_source_record.v0_1
prohibited_behaviors:
  - stealth_fetch
  - raw_feed_to_orion_marker
  - target_scanning
```

## 5. First passive world-event tranche

The first adapter tranche is:

- USGS earthquakes;
- NASA EONET natural events;
- NASA FIRMS fire/hotspot events;
- NOAA/NWS active alerts;
- GDACS disaster alerts;
- GDELT/global incident signals.

Each has a candidate source-record fixture under:

```text
fixtures/orion-osiris/source-records/
```

## 6. Acceptance criteria

The tranche is implementation-ready when:

- all six candidate source records exist;
- the validator requires all six candidate ids;
- terms/attribution status is explicitly recorded, even if still review-required;
- no adapter requires live credentials to validate;
- no OSIRIS runtime code is imported.
