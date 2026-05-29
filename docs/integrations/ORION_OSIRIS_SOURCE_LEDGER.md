# Orion / OSIRIS Source Ledger

Status: initial Gaia-owned source ledger
Related issue: `SocioProphet/gaia-world-model#29`
Source quarantine repo: `mdheller/osiris`

## 1. Purpose

This ledger records source candidates discovered during OSIRIS excavation and classifies which are eligible for Gaia-owned transparent source adapter work.

The source ledger is intentionally separate from the MIT code-license posture of OSIRIS. MIT licensing of code does not grant unrestricted rights to external feeds, APIs, imagery, camera streams, intelligence assertions, or third-party datasets.

## 2. Promotion states

| State | Meaning |
|---|---|
| `fixture_only` | May be represented by synthetic fixtures only. No live source use. |
| `adapter_candidate` | May become a Gaia adapter after terms/attribution/rate-limit review. |
| `hold_review` | Useful concept but live use requires deeper review. |
| `blocked_this_tranche` | Not eligible for this Gaia tranche. |
| `scope_d_only` | Action/recon behavior belongs to SCOPE-D, not Gaia. |

## 3. Evidence grades

Use provisional grades from `ORION_OSIRIS_SOURCE_ADAPTERS.md`:

- `fixture.synthetic`
- `public_source.unverified`
- `public_source.versioned`
- `public_source.attributed`
- `operator_report.unverified`
- `fused.inferred`
- `policy_gated.action`

For Gaia source records in this tranche, prefer:

- `fixture.synthetic`
- `public_source.unverified`
- `public_source.versioned`
- `public_source.attributed`

## 4. Source candidates

| Source | OSIRIS route/family | Gaia role | Terms status | Attribution | Risk | Promotion state | Notes |
|---|---|---|---|---|---|---|---|
| USGS Earthquake GeoJSON | `/api/earthquakes` | Seismic source record | Review required | Review required | low | `adapter_candidate` | Best first live adapter candidate; reimplement transparently. |
| NASA EONET | `/api/weather`, `/api/fires` volcano enrichment | Natural-event source record | Review required | Review required | low/medium | `adapter_candidate` | Useful for severe storms, volcanoes, sea ice, natural events. |
| NASA FIRMS | `/api/fires` | Fire/hotspot source record | Review required | Review required | medium | `adapter_candidate` | Requires terms/API-key/rate-limit posture before live mode. |
| NOAA/NWS active alerts | `/api/weather` | Weather-alert source record | Review required | Review required | low/medium | `adapter_candidate` | Use transparent fetch and declared user agent. |
| Synthetic facility asset registry | fixture only | Facility source record | Approved fixture | No | low | `fixture_only` | Represents Orion MVP asset leg. |
| Synthetic operator field report | fixture only | Field-report source record | Approved fixture | No | low | `fixture_only` | Human report remains unverified until reviewed. |
| Synthetic passive CVE exposure | fixture only | Cyber exposure source metadata | Approved fixture | No | low | `fixture_only` | Passive metadata only; no scan/sweep execution. |
| CCTV/camera providers | `/api/cctv` | Possible visual context later | Mixed/unknown | Provider-specific | high | `hold_review` | Requires per-provider terms, privacy, retention, and attribution review. |
| ADSB/flight feed | `/api/flights` | Possible mobility source later | Unknown | Review required | medium/high | `hold_review` | Classification and GPS-jamming inference require claim boundaries. |
| AIS/maritime stream | `/api/maritime` | Possible vessel source later | Unknown/API-key | Review required | medium/high | `hold_review` | Static ports and live AIS must be separated. |
| Static ports/chokepoints/naval data | `/api/maritime` | Possible static reference data | Unknown provenance | Review required | medium | `hold_review` | No evidence claim without provenance. |
| Telegram public previews | README/unknown route | Possible public social signal later | Terms-sensitive | Review required | high | `blocked_this_tranche` | No live scraping in this tranche. |
| Crypto wallet lookup | OSINT panel | Possible public ledger lookup later | Review required | Review required | medium/high | `blocked_this_tranche` | Not required for Orion map MVP. |
| Sanctions/OpenSanctions | OSINT panel | Possible compliance source later | Review required / attribution likely | Yes | medium | `blocked_this_tranche` | Needs source version, match method, false-positive caveat. |
| Scanner proxy | `/api/scanner` | Not Gaia-owned | Not applicable | Not applicable | critical | `scope_d_only` | Active target behavior. |
| IP sweep/Shodan InternetDB | `/api/osint/sweep` | Not Gaia-owned | External terms required | Review required | critical | `scope_d_only` | Enumerates host ranges and classifies devices. |
| `stealthFetch` helper | shared utility | Forbidden fetch pattern | Not applicable | Not applicable | critical | `blocked_this_tranche` | Do not copy or emulate stealth/evasion semantics. |

## 5. Gaia adapter admission checklist

A source may become a Gaia adapter only when:

- source URL/API family is documented,
- terms/license posture is recorded,
- attribution requirement is recorded,
- commercial-use posture is recorded or marked unknown/review-required,
- rate-limit strategy is recorded,
- canonicalization/hash strategy is recorded,
- fixture replay exists,
- output can produce or support `GaiaSourceRecord`,
- live mode is not required for validation,
- no stealth/evasion fetch behavior is used.

## 6. Initial tranche admission

Admitted for fixture-backed Gaia work now:

- synthetic fire/weather source record,
- synthetic facility asset source record,
- synthetic passive CVE exposure source record,
- synthetic operator field report source record.

Admitted for future transparent adapter design after terms review:

- USGS earthquake feed,
- NASA EONET,
- NASA FIRMS,
- NOAA/NWS active alerts.

Everything else remains held, blocked, or SCOPE-D-only.

## 7. Cross-repo boundaries

- Gaia owns source records and source adapter discipline.
- Orion owns event map, event envelope, selected event drawer, decision cards, and operator UX.
- SCOPE-D owns scanner, sweep, recon, and active target behavior.
- Ontogenesis may later stabilize vocabulary.
- SocioSphere records lane topology and dependency direction.
