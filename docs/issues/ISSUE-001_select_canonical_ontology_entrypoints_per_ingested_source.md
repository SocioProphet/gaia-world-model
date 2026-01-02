# ISSUE-001: Select canonical ontology entrypoints per ingested source

**Labels:** ontology, v0.10

**Goal:** For each `gaia/cv/sources/<source>/`, select the authoritative ontology entrypoint(s) and promote them to `gaia/ontology/canonical/`.

**Acceptance:**
- `gaia/ontology/canonical/index.yaml` exists and lists, per source:
  - upstream license identifier + evidence file paths
  - selected entrypoints + import order
  - notes on deprecated/alternate files

**Notes:**
- Start with SWEET, Ocean Data Ontology, Environmental Exposure Ontology, OBOGraphs.
