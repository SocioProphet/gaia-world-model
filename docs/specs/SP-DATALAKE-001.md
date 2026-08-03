# SP-DATALAKE-001 — Community Data Lake / AI-Analytics Hub
### Roadmap Phase 5 build spec: a sovereign, governed equivalent of the GCP data/AI stack, over open standards.

| Field | Value |
|---|---|
| Spec ID | `SP-DATALAKE-001` |
| Version | `v0.1.0` DRAFT |
| Evidence grade | **E1** (reasoned from estate repos + the IBM open-stack teardown; every repo/interface reference is a binding point, not a claim about current code) |
| Depends on | `prophet-core-catalog` (DatasetCatalogEntry v1), `gaia-world-model` (data plane), Crystal Atlas (`graph-upsert-request.v0`), `sherlock-search/caps/semantic-search-bi`, the unified **DecisionLedgerEntry** (verdict/promotion spine), sovereign MinIO/Zot |
| Consumers | Phase 6 (Model Zoo / `model-router`), Phase 7 (Community Prophet / EBA), the domain workspaces (`socioprophet-web`) |

## 0. Agent protocol (read first)
Bind before build. Do not implement types from this spec's prose — read the real `prophet-core-catalog`, `gaia-world-model`, and Crystal Atlas contracts first and emit `BINDING.md`. One WO, one PR, dependency-ordered. Every layer gates the next; a layer with no governance receipt is a failed layer, not a fast one.

## 1. Objective
Recreate the GCP data/AI capability surface as a **sovereign, community-owned lake** where:
- the ~70 sources already in the **catalog seed** become materializable governed tables (not just link-only entries);
- every read/query is **wall_guard-checked and ledgered** (a query is a promotion under evidence);
- **data-sharing is a governed promotion**, not a copy — gated by the same consent/k-anon invariants (`INV-PRIV`) the hardened decision-ledger already defines;
- the lake feeds Crystal Atlas (graph), `semantic.search` (discovery), and `model-router` (Phase 6) through contracts that **already exist**.

Not greenfield: this is "make the catalog + Crystal Atlas real over Iceberg/Trino, governed by the ledger."

## 2. The GCP → sovereign mapping (target)
| GCP | Sovereign target | Estate anchor |
|---|---|---|
| GCS | MinIO + **Apache Iceberg** tables | sovereign registry (MinIO/Zot) |
| BigQuery | **Trino** (server) / DuckDB (edge) over Iceberg | new |
| Dataproc | Spark (batch) | new |
| **Dataflow** | **Apache Beam** — unified batch + streaming, on the **Spark runner** (NOT Flink, per estate "no Flink" rule); Kafka/SSB source | new |
| Data Catalog | `prophet-core-catalog` + **OpenMetadata** | DatasetCatalogEntry v1 + catalog seed |
| Vertex AI | `model-router` + KServe/vLLM + Model Zoo | Phase 6 |
| Pub/Sub | Kafka / SSB (already the estate event bus) | event bus |
| Analytics Hub | governed data-sharing over `wall_guard` + DecisionLedger | verdict/promotion spine |

**Beam is the unified ingest/transform engine**, not just batch: one pipeline definition runs release-pinned batch materializations (WO_DL_002) *and* streaming CDC/enrichment into the lake + Crystal Atlas (WO_DL_005), with per-record `wall_guard` + ledger emission carried through the pipeline. Runner = Spark (batch) / Spark-streaming or Direct (dev); Flink is explicitly out.

## 3. Work orders (phased; each gates the next)
| WO | Title | Depends | Acceptance |
|---|---|---|---|
| `WO_DL_001` | **Binding.** Read prophet-core-catalog / gaia-world-model / Crystal Atlas contracts; emit `BINDING.md` mapping DatasetCatalogEntry, graph-upsert-request.v0, and the DecisionLedgerEntry to real types. | — | 100% symbol coverage; CI asserts later WOs import from BINDING.md. |
| `WO_DL_002` | **Table layer.** MinIO + Iceberg; a `materialize(source_id)` that turns a catalog `admitted` source into a governed Iceberg table. Refresh honors `snapshot_gcs => release-pinned` catalog invariant. | 001 | A catalog `admitted` source materializes to a pinned Iceberg table; `fixture_only` sources refuse to materialize. |
| `WO_DL_003` | **Query layer.** Trino over Iceberg (DuckDB profile for edge). Every query passes a `wall_guard.visible(ctx)` check and emits a **DecisionLedgerEntry** (surface=`catalog`, action per gate). | 002 | Restricted-source query without grant → `NEG`/deny + ledger entry; permitted query → `POS` + row set + ledger entry. |
| `WO_DL_004` | **Live catalog.** Promote the catalog seed to an OpenMetadata-backed live catalog; the **fail-closed invariant gate** (copyleft⇒¬public, NC⇒commercial-gate) is the lake admission control. Self-checker excludes itself. | 002 | The 5 catalog invariants fail-closed in CI; a copyleft-public misconfig blocks admission. |
| `WO_DL_005` | **Discovery + graph.** Wire `semantic.search` (Behavioral Indexing) over the lake; project results into Crystal Atlas via the existing `crystal-atlas-graph.binding.v0`. | 003, 004 | A search over lake tables returns hits + upserts nodes/edges into Crystal Atlas with evidence. |
| `WO_DL_006` | **Governed data-sharing (Analytics Hub).** Sharing a dataset is a `PROMOTE_CANONICAL` gated by `INV-PRIV` (consent + k-anon for any reidentification-risk feature) + license attestation. | 003 | A mobility/PII dataset cannot be shared without consent + k-anon; a public dataset shares with a receipt. |
| `WO_DL_007` | **AI-hub bridge (→ Phase 6).** Expose lake tables to `model-router` / Model Zoo as governed training/eval inputs; every read ledgered. | 005 | A Model-Zoo job reads a lake table under a policy and emits a decision-ledger entry. |

## 4. Invariants (machine-checkable)
- **DL-INV-1 (admission).** Only catalog `admitted` sources materialize; `wall_guard=restricted` requires a grant.
- **DL-INV-2 (ledgered access).** Every query/read/share emits a signed DecisionLedgerEntry; a read with no entry is a failed read.
- **DL-INV-3 (invariant gate).** The 5 catalog invariants fail closed (no copyleft-public, NC⇒commercial gate) — the lake's admission control.
- **DL-INV-4 (sharing = privacy-gated promotion).** Any reidentification-risk dataset requires consent + k-anon before `PROMOTE_CANONICAL` (INV-PRIV).
- **DL-INV-5 (pinned freshness).** `snapshot` materializations are release-pinned (immutable version hash); no silent drift.

## 5. Why this is the critical path
Phases 6 (Model Zoo) and 7 (Community Prophet/EBA) both read the lake. The lake's governance (admission, ledgered access, privacy-gated sharing) is *already specified* by the decision-ledger + catalog invariants + Crystal Atlas binding merged this session — so SP-DATALAKE-001 is mostly *wiring existing contracts over Iceberg/Trino*, not inventing a data platform. Build order 002→003→004 is the minimum viable lake; 005→006→007 make it a governed community hub.
