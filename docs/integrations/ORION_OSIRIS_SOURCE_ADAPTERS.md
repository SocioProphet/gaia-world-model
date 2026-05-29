# Orion / OSIRIS Source Adapter Boundary

Status: initial Gaia-owned implementation plan
Related issue: `SocioProphet/gaia-world-model#29`
Source quarantine repo: `mdheller/osiris`

## 1. Purpose

This document moves the safe source-ingestion side of the OSIRIS excavation into Gaia ownership.

`mdheller/osiris` is a quarantine/excavation carcass. It may inform adapter design, source-ledger requirements, and map UX references. It is not a trusted runtime dependency and is not a Gaia product source.

Gaia owns the source/provenance side of the Orion map MVP:

```text
transparent source fetch -> GaiaSourceRecord -> Orion consumes source refs through OrionObservationEvent
```

Orion owns the event-map and operator decision surface. SCOPE-D owns scanner, sweep, recon, and active target behavior.

## 2. Controlling rule

Do not copy inherited OSIRIS route handlers into Gaia.

Do not copy or use `stealthFetch`.

Do not import inherited scanner, sweep, CCTV, Telegram, crypto, sanctions, aviation, or maritime live-feed behavior in this tranche.

Gaia source ingestion must be:

- transparent,
- attributable,
- terms-aware,
- rate-limit-aware,
- provenance-bearing,
- fixture-replayable,
- safe to validate without live credentials.

## 3. Initial source candidates

| Source | Candidate status | Gaia role | Notes |
|---|---|---|---|
| USGS earthquake feed | first-pass candidate | public seismic source record | Direct public GeoJSON feed observed in OSIRIS excavation. |
| NASA EONET | first-pass candidate | public natural-event source record | Useful for storms, volcanoes, and other natural events. |
| NASA FIRMS | review-required candidate | fire/hotspot source record | Terms/attribution and API-key posture must be recorded before live mode. |
| NOAA/NWS alerts | review-required candidate | weather-alert source record | Use transparent fetch and declared user agent. |

Held sources:

- CCTV/camera feeds.
- Telegram/public-preview scraping.
- Aviation/ADSB feeds.
- Maritime/AIS feeds.
- Crypto/sanctions lookup.
- Scanner/sweep/recon routes.
- Any route that used stealth/evasion semantics.

## 4. GaiaSourceRecord v0.1 fields

The first Gaia-owned source record captures:

- `source_record_id`
- `source_name`
- `source_family`
- `route_family`
- `source_url`
- `observed_at`
- `ingested_at`
- `license_status`
- `attribution_required`
- `commercial_use_status`
- `evidence_grade`
- `risk_class`
- `provenance`
- optional `confidence_contribution`
- optional `notes`

This is intentionally narrower than a production source registry. It gives Orion enough source/provenance discipline for the map MVP without making Gaia own Orion UI.

## 5. Evidence-grade draft

Use these provisional grades until Ontogenesis stabilizes vocabulary:

- `fixture.synthetic`
- `public_source.unverified`
- `public_source.versioned`
- `public_source.attributed`
- `operator_report.unverified`
- `fused.inferred`
- `policy_gated.action`

Gaia should avoid promoting `fused.inferred` as a raw source grade except when representing a downstream fusion object. The normal Gaia source-record grades for this tranche are `fixture.synthetic`, `public_source.unverified`, `public_source.versioned`, and `public_source.attributed`.

## 6. Transparent fetch posture

A Gaia source adapter may declare a source-specific user agent and may respect rate limits. It must not randomize identity, spoof residential IPs, bypass source restrictions, or present stealth/evasion semantics.

Required metadata for live adapters:

- provider name,
- API endpoint family,
- terms/license status,
- attribution requirement,
- rate-limit strategy,
- cache/replay strategy,
- canonicalization/hash method,
- failure mode,
- evidence grade.

## 7. Fixture-first MVP

The first Orion/OSIRIS migration slice should be fixture-backed. Gaia should provide source-record fixtures corresponding to:

1. fire/weather hazard source,
2. facility asset source,
3. passive cyber exposure source,
4. operator field report source.

The passive cyber exposure source is source/provenance metadata only. Scanner/sweep execution remains SCOPE-D-owned and unavailable in this tranche.

## 8. Acceptance criteria for this Gaia tranche

- A Gaia-owned source-record schema exists.
- Facility-risk source-record fixtures exist.
- A Gaia validator checks required fields and rejects missing provenance/evidence grade/source family.
- Docs explicitly reject OSIRIS runtime-code import and `stealthFetch`.
- Source candidates are classified before live adapters exist.
- Orion can reference Gaia source record ids without Gaia owning Orion UI.

## 9. Cross-repo links

- `SocioProphet/orion-field-intelligence#2` owns the Orion event-map MVP.
- `SocioProphet/SCOPE-D:docs/osiris-scanner-sweep-quarantine.md` owns scanner/sweep quarantine.
- `SocioProphet/sociosphere#406` coordinates the lane.
