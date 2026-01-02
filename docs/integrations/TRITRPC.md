# TritRPC v1 Integration (GAIA) — Path A (Avro Binary)

We treat TritRPC as a first-class wire protocol for distributed (fog → cluster) execution.
Path A is the current, simplest, deterministic-enough baseline: **ternary64 framing + Avro binary payloads**.

## Schema source of truth (Schema Salad)
- We vendor the TritRPC **Schema Salad** file as the authoring schema:
  - `vendor/tritrpc/spec/salad/tritrpc_salad.yml`
- That SALAD schema is what compilers use to derive:
  - an **Avro schema** (binary encoding contract)
  - a **JSON-LD context** (semantic predicates / graph mapping)

## IDs (Path A fixtures vs production)
- TritRPC fixtures currently pin IDs as sha3-256 over stable labels:
  - `schema_id = sha3-256("HG_AVRO_v1") = b2ab814588f99c875d37bb7546d0df4369c28bc5f60ce38a6607dac468034352`
  - `context_id = sha3-256("HG_JSONLD_v1") = e6572c0e618f18d572d4c2969db4909659f09eaef32ec66fbb804bad9d89aacd`
- **Path B (second pass)** will replace these with content-addressed IDs derived from canonicalized Avro/JSON-LD outputs.

## Wire naming + directions
- Service: `hyper.v1`
- Unary examples:
  - `hyper.v1.AddVertex_a.REQ`  → HGRequest(op=AddVertex)
  - `hyper.v1.AddVertex_a.RSP`  → HGResponse
- Stream examples:
  - `hyper.v1.GetSubgraphStream.OPEN`  → HGStreamChunk(kind=OPEN)
  - `hyper.v1.GetSubgraphStream.DATA<n>`→ HGStreamChunk(kind=DATA)
  - `hyper.v1.GetSubgraphStream.CLOSE` → HGStreamChunk(kind=CLOSE)

## Determinism footguns (important)
- **Avro maps are unordered**; some language runtimes iterate maps nondeterministically.
- Until all ports enforce canonical map ordering:
  - GAIA canonical payloads MUST set `attr = {}` (empty) OR sort keys lexicographically during encoding.

## Registry contract mapping
- `protocols[]` includes `tritrpc` + `encoding=avro-binary` + `service` + method patterns
- `schema_bundle` references the vendored SALAD and the (currently fixture) `schema_id/context_id`

