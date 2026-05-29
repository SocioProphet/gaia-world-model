# Orion / OSIRIS Held Source Backlog

Status: captured backlog, not live enablement
Related issue: `SocioProphet/gaia-world-model#29`
Source quarantine repo: `mdheller/osiris`

## 1. Purpose

This document captures the OSIRIS-discovered feeds and source families that were deliberately held out of the first fixture-backed Gaia/Orion MVP.

Held does not mean discarded. The intent is to eventually recover as much useful feed coverage as possible, but under Gaia source/provenance discipline, Orion event semantics, SCOPE-D action governance, and SocioSphere coordination.

The rule remains:

```text
capture everything -> classify risk -> ledger terms/provenance -> reimplement in owned repos -> validate -> enable by policy
```

Do not import inherited OSIRIS route handlers as authority.

Do not copy `stealthFetch` or any stealth/evasion semantics.

Do not run live feeds with credentials from the quarantine repo.

## 2. Admission classes

| Class | Meaning | Next owner |
|---|---|---|
| `source_adapter_candidate` | Feed can likely become a transparent Gaia source adapter after terms/provenance review. | Gaia |
| `context_layer_candidate` | Useful map/context layer but needs provenance, claims, and UI semantics before use. | Gaia + Orion |
| `policy_gated_candidate` | Useful capability but requires SCOPE-D policy before any execution/action. | SCOPE-D |
| `terms_privacy_review` | Feed may be useful but needs terms, privacy, jurisdiction, or retention review. | Gaia + policy owner |
| `blocked_pattern` | Implementation pattern is not allowed, though the product need may be reimplemented safely. | Owning repo after redesign |

## 3. Natural hazard and world-event feeds

| Feed/source | OSIRIS route/family | Class | Capture decision | Gates before enablement |
|---|---|---|---|---|
| USGS earthquakes | `/api/earthquakes` | `source_adapter_candidate` | Already admitted as first-pass candidate. | Terms/attribution record, transparent fetch, source hash/replay. |
| NASA EONET | `/api/weather`, `/api/fires` volcano enrichment | `source_adapter_candidate` | Already admitted as first-pass candidate. | Terms/attribution record, transparent fetch, event-family mapping. |
| NASA FIRMS | `/api/fires` | `source_adapter_candidate` | Capture for live fire/hotspot layer. | API key/rate-limit/terms, attribution, sampling disclosure. |
| NOAA/NWS alerts | `/api/weather` | `source_adapter_candidate` | Capture for weather-alert layer. | Transparent declared user agent, terms/attribution, alert geometry handling. |
| GDACS / disaster alerts | README/route inventory | `source_adapter_candidate` | Capture for later disaster-alert adapter. | Confirm concrete route, terms, source version, evidence grade. |
| GDELT / global incidents | `/api/gdelt` / global incidents | `source_adapter_candidate` | Capture for news/event signal layer. | Terms, event extraction caveats, geoparsing confidence, false-positive caveats. |
| GPS jamming inference | `/api/flights` derived output | `context_layer_candidate` | Capture as inference candidate, not source truth. | Claim boundary, source confidence, derivation record, no direct safety claim. |

## 4. Mobility and infrastructure feeds

| Feed/source | OSIRIS route/family | Class | Capture decision | Gates before enablement |
|---|---|---|---|---|
| ADSB/adsb.lol flight positions | `/api/flights` | `source_adapter_candidate` | Capture for aviation layer. | Terms/rate limits, transparent fetch, observed-vs-inferred separation. |
| Commercial/private/military classification | `/api/flights` derived classification | `context_layer_candidate` | Capture as derived classification only. | Claim caveats, confidence, no proof of intent/identity. |
| AIS stream / aisstream.io | `/api/maritime` | `source_adapter_candidate` | Capture for maritime/vessel layer. | API key governance, terms, bounding-box scope, replay/cache strategy. |
| Static ports | `/api/maritime` static list | `context_layer_candidate` | Capture as static reference dataset candidate. | Provenance/source citations, update cadence, license status. |
| Chokepoints | `/api/maritime` static list | `context_layer_candidate` | Capture as strategic-context layer candidate. | Provenance, risk-score methodology, no unsupported geopolitical claim. |
| Naval bases/static military infrastructure | `/api/maritime` static list | `terms_privacy_review` | Capture but hold. | Provenance, public-source status, sensitive-geo policy review. |
| Nuclear infrastructure | map/source inventory | `terms_privacy_review` | Capture but hold. | Source provenance, sensitive infrastructure policy, display controls. |
| SCM suppliers | layer inventory | `context_layer_candidate` | Capture as supply-chain asset/context lane. | Asset source model, entity provenance, commercial data rights. |

## 5. Camera, media, and public social feeds

| Feed/source | OSIRIS route/family | Class | Capture decision | Gates before enablement |
|---|---|---|---|---|
| TfL JamCams | `/api/cctv` | `terms_privacy_review` | Capture for camera-source ledger. | Provider terms, attribution, retention/display policy. |
| WSDOT / Caltrans / 511 feeds | `/api/cctv` | `terms_privacy_review` | Capture for camera-source ledger. | Per-provider terms, rate limits, privacy/retention policy. |
| European camera modules | `/api/cctv` helpers | `terms_privacy_review` | Capture for per-country camera review. | Country/provider terms, privacy/jurisdiction review. |
| Japan/Australia/other camera modules | `/api/cctv` helpers | `terms_privacy_review` | Capture for per-provider review. | Terms, attribution, retention/display policy. |
| Live news feeds | `/api/news`, `live_news` layer | `source_adapter_candidate` | Capture for media signal layer. | Source terms, attribution, excerpt/link-only policy, event extraction caveats. |
| RSS/SIGINT-style news | `sigint-news` layer | `source_adapter_candidate` | Capture as public-source signal candidate. | Source list, terms, labels avoiding unsupported intelligence claims. |
| Telegram public previews | README/route inventory | `terms_privacy_review` | Capture but hold. | ToS review, public-source status, geoparsing confidence, privacy/jurisdiction review. |

## 6. Cyber, sanctions, crypto, and OSINT lookup feeds

| Feed/source | OSIRIS route/family | Class | Capture decision | Gates before enablement |
|---|---|---|---|---|
| NVD CVE | `/api/osint/cve`, cyber layer | `source_adapter_candidate` | Capture for passive CVE enrichment. | Terms/rate limits, source version, no exploitation workflow. |
| Shodan InternetDB | `/api/osint/sweep` | `policy_gated_candidate` | Capture as SCOPE-D-only passive/enrichment candidate. | SCOPE-D EngagementPolicy, source terms, no unauthenticated sweep. |
| DNS lookup | `/api/osint/dns` | `policy_gated_candidate` | Capture as passive lookup candidate. | Scope, rate limits, evidence receipt, no target action without policy. |
| WHOIS | `/api/osint/whois` | `policy_gated_candidate` | Capture as passive lookup candidate. | Terms, privacy, stale-data caveats, receipt. |
| Certificates/CT | `/api/osint/certs` | `source_adapter_candidate` | Capture as public certificate intelligence. | Source terms, evidence version, match caveats. |
| Headers/SSL/Tech detect | `/api/scanner`, `/api/osint/*` | `policy_gated_candidate` | Capture, but SCOPE-D-gated if touching target. | TargetScope, AuthorizationRef, receipt, non-destructive constraints. |
| Subdomains | `/api/scanner`/lookup | `policy_gated_candidate` | Capture. | Passive-source-only distinction vs active enumeration. |
| BGP route | `/api/osint/bgp` | `source_adapter_candidate` | Capture as public network context. | Source terms, attribution, confidence. |
| MAC address lookup | `/api/osint/mac` | `source_adapter_candidate` | Capture as passive manufacturer lookup. | Source terms and privacy caveats. |
| Phone intelligence | `/api/osint/phone` | `terms_privacy_review` | Capture but hold. | Privacy, jurisdiction, lawful basis, no doxxing workflow. |
| Data leaks | `/api/osint/leaks` | `terms_privacy_review` | Capture but hold. | Legal/privacy review, breach-data handling policy. |
| GitHub recon | `/api/osint/github` | `source_adapter_candidate` | Capture as public profile/repo context. | API terms, rate limits, no credential/secrets harvesting. |
| Crypto wallet lookup | `/api/osint/crypto` | `source_adapter_candidate` | Capture for public ledger context. | Chain-source terms, attribution, no identity proof claim. |
| OpenSanctions / OFAC cross-check | OSINT panel | `source_adapter_candidate` | Capture for sanctions/compliance context. | License/attribution, dataset version, match confidence, false-positive caveats. |

## 7. Explicitly blocked implementation patterns

| Pattern | Capture decision | Replacement path |
|---|---|---|
| `stealthFetch` identity/randomization/spoofing semantics | Block implementation, preserve risk note. | Transparent Gaia source fetch with declared user agent and rate-limit discipline. |
| OSIRIS scanner proxy as product runtime | Block direct import. | SCOPE-D-governed capability after EngagementPolicy/TargetScope/AuthorizationRef. |
| OSIRIS IP sweep route as product runtime | Block direct import. | SCOPE-D policy-gated passive fixture first; no unauthenticated sweep. |
| OSIRIS OSINT panel execution behavior | Block direct import. | Split UI into passive lookup, source context, and SCOPE-D-gated action states. |
| Raw public feed -> map marker as authority | Block authority model. | GaiaSourceRecord -> OrionObservationEvent -> OrionMapMarker. |

## 8. Recovery order

1. Complete fixture-backed Gaia/Orion seam and CI.
2. Add passive public-source adapters: USGS, EONET, FIRMS, NWS.
3. Add public media/event signal adapters: GDELT, GDACS, RSS/news.
4. Add mobility context: ADSB, AIS, ports/chokepoints with provenance and claim caveats.
5. Add passive cyber sources: NVD, CT/certs, BGP, sanctioned-list datasets.
6. Add camera feeds only after provider/jurisdiction/privacy review.
7. Add Telegram/social only after ToS/privacy/public-source policy review.
8. Add scanner/sweep/recon only through SCOPE-D policy gates, never as Orion/Gaia runtime.

## 9. Completion definition

This backlog is captured when every OSIRIS-discovered feed or feature has one of:

- a Gaia source-adapter candidate path,
- an Orion context/layer path,
- a SCOPE-D policy-gated path,
- a terms/privacy review path,
- or an explicit blocked-pattern replacement path.

No item should disappear merely because it is unsafe to enable immediately.
