# Lampstand Local State Sampling + Percolation Integration

Status: v0 integration contract

## Purpose

Lampstand integrates with GAIA, OFIF, Sherlock Search, and Lattice Forge as the local-state sampling substrate.

Lampstand is not the global search engine and not the world model. Lampstand samples local state, reconciles it, indexes it, exposes health/stats, and emits governed local-state records that can percolate upward into the broader SocioProphet mesh.

## Authority boundaries

| Domain | System of record |
| --- | --- |
| Local filesystem scan/inotify/reconciliation | Lampstand |
| Local metadata and FTS index | Lampstand |
| Local health/stats and reconcile state | Lampstand |
| Field sensor/event envelope | OFIF |
| World model and geospatial/evidence graph | GAIA |
| Global/distributed semantic retrieval | Sherlock Search |
| Runtime/build/model-ready surface packaging | Lattice Forge |

## What Lampstand samples

Lampstand should emit local-state observations for:

- file metadata;
- file content fingerprints;
- text snippets / FTS summaries;
- local media artifact references;
- project/repo/document roots;
- local build artifacts;
- local model outputs;
- local notebooks/reports;
- local sensor dumps or edge observation files;
- local health/stats for index freshness and reconciliation status.

## Percolation doctrine

Percolation means local state moves upward only through governed records.

```text
Local file or state change
  -> Lampstand local sample
  -> LocalStateRecord
  -> policy/classification gate
  -> Sherlock SearchRecord and/or GAIA EvidenceArtifact and/or OFIF EventEnvelope
  -> Lattice Forge RuntimeAsset / SurfaceRecord when reproducibility is required
```

Lampstand should not indiscriminately upload local data. It emits inspectable records with hashes, timestamps, handling tags, and policy context. Higher layers decide whether to index, enrich, retain, replicate, or discard.

## Required record families

### LocalStateRecord

Represents a sampled local object.

Required fields:

- `record_version`
- `record_id`
- `sampled_at`
- `lampstand_node_id`
- `local_path_ref` or redacted path reference
- `object_kind`
- `content_hash`
- `metadata_hash`
- `size_bytes`
- `mtime`
- `classification`
- `handling_tags`
- `source_root_id`

### LocalStateDelta

Represents a change detected by scan, inotify, or reconciliation.

Required fields:

- `delta_id`
- `previous_record_id`
- `current_record_id`
- `delta_type`
- `detected_by`
- `detected_at`
- `confidence`

### PercolationEnvelope

Represents a governed handoff from local state to another subsystem.

Required fields:

- `envelope_id`
- `source_record_ids`
- `target_system`
- `target_artifact_type`
- `policy_decision`
- `redaction_state`
- `provenance`
- `integrity`

## GAIA integration

Lampstand can feed GAIA when local files represent evidence or world-state material:

- local geospatial files;
- field observation logs;
- drone imagery manifests;
- sensor CSV/JSON dumps;
- generated reports;
- model outputs;
- notebooks that produce GAIA layers.

GAIA must treat Lampstand inputs as local evidence artifacts. They require provenance, classification, hashes, and optional redaction before entering the world model.

## OFIF integration

Lampstand can feed OFIF when local state corresponds to edge/field observations:

- sensor dump file observed locally;
- gateway log change;
- custody/tamper report file;
- media artifact captured at edge;
- local operator annotation.

Lampstand does not invent OFIF events. It can trigger creation of OFIF EventEnvelopes through a policy-approved adapter.

## Sherlock Search integration

Lampstand is the local sampler. Sherlock is the distributed/global search surface.

Lampstand should publish search records for approved local samples with:

- title/path label;
- snippet;
- content hash;
- object kind;
- source root;
- local freshness state;
- handling tags;
- evidence references;
- optional H3/geospatial tags if known;
- optional project/org/workspace tags.

Sherlock should be able to query across Lampstand-local records and GAIA/OFIF-derived records without erasing source authority.

## Lattice Forge integration

Lampstand contributes to Lattice Forge by sampling local runtime/build/model artifacts:

- lockfiles;
- notebooks;
- model outputs;
- generated features;
- local build products;
- local scan reports;
- package metadata.

When a local artifact becomes reproducible infrastructure, Lattice Forge packages it as a RuntimeAsset or surface/feature record with SBOM, lockfile, signature, scan record, and promotion evidence.

## Sampling modes

1. **One-shot scan**: explicit local sampling of roots.
2. **Incremental watcher**: inotify-driven local updates.
3. **Periodic reconciliation**: correctness pass that prevents watcher superstition.
4. **Policy-triggered percolation**: only approved records leave local scope.
5. **Health/stats emission**: local freshness and integrity posture.

## Privacy and handling rules

- Raw local content does not percolate by default.
- Hashes and metadata may percolate if policy allows.
- Snippets require classification and redaction checks.
- Sensitive paths should be redacted or path-tokenized.
- Percolated records must include handling tags and retention class.
- User or org policy may keep records local-only.

## World-class target

Lampstand should become the local-state sampling membrane for the SourceOS/SocioProphet stack:

- local-first by default;
- mesh-capable by governed percolation;
- inspectable through health/stats;
- reproducible through hashes and manifests;
- searchable through Sherlock;
- world-model-aware through GAIA;
- field-event-aware through OFIF;
- runtime/model-ready through Lattice Forge.
