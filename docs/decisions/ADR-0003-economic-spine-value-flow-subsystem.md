# ADR-0003: The Economic Spine is the Value-Flow Subsystem of the World Model

Status: Proposed
Date: 2026-08-03

## Context

The estate has two mature planes that were never bound to each other:

- **The world model (GAIA).** GAIA owns the WorldModelSubstrate *W*: geospatial
  substrate, ontology, evidence graph, biosphere / resource / carrying-capacity state,
  simulation, and the digital-twin hierarchy (`gaia/twins/**`). ADR-0002 established
  that world-model layers land here as contracts, schemas, examples, and validation
  hooks rather than as new repositories, and that GAIA remains the semantic and
  provenance home for those layers.
- **The economic spine (Economic Prophet).** `SocioProphet/economic-prophet` is the
  value engine. Its omnirisk/EP kernels are merged on `main`
  (`risk_measures`, `ftp`, `term_calculus`, `asset_ladder`, `flow_regime`); the
  **welfare-annealing** dynamics — carrying-capacity discount, the Jacob's-ladder
  natural-capital / renewable base, and the QoL welfare objective — are in flight on
  `economic-prophet@feat/welfare-annealing`.

`schemas/economy/economy_observation.v1.schema.json` already binds GAIA to Economic
Prophet by soft-ref for a *single observation* (`framework_ref:
SocioProphet/economic-prophet@<sha>`, EP as the canonical additive value measure). What
was missing is the **composition**: the economic spine as a *subsystem of the world
model*, placed in the twin hierarchy, with value flows as the exchange dynamics — and,
critically, with its ecological and human terms bound to world-model state **by
reference** rather than left as free parameters.

The failure mode being closed is a welfare/EP run whose carrying-capacity term is a
hand-picked constant, whose QoL objective is exogenous, and whose cross-scale value
flows create value out of nothing. That is the economic analog of GAIA's
"map-label-as-truth": numbers that *look* governed but read from nowhere.

## Decision

Establish the economic spine as the **value-flow subsystem of the world model**, and
place it in the twin hierarchy, as a **binding contract with teeth** landed in
`gaia-world-model` (consistent with ADR-0002). GAIA declares what the spine must READ
from *W*; the teeth reject spine runs that do not.

Home rationale — **gaia-world-model, not economic-prophet**:

1. The binding is *upward*: the world model owns the biosphere/resource state and the
   twin hierarchy that the spine READS. The contract is a world-model boundary
   contract; EP owns its own internal contracts (ALC-1, RFL-1, FRT-1, …).
2. ADR-0002 already names GAIA the home for world-model layer/composition contracts and
   forbids spinning up a new repo for them.
3. `schemas/economy/**` is the established soft-ref surface between the two planes.
4. Consume-not-fork: EP kernels and the welfare-annealing branch are referenced by
   pinned ref; nothing is vendored.

### The four bindings

1. **Carrying-capacity ⟷ Gaia biosphere.** The welfare-annealing carrying-capacity
   discount and the Jacob's-ladder natural-capital / renewable base are a READ of the
   GAIA biosphere/resource state, not a free parameter.
2. **Twin-hierarchy composition + value conservation.** The scale stack is
   `galactic_space_twin ⟷ world_economic_twin (this spine) ⟷ human_digital_twin`, with
   value flows as the cross-scale exchange dynamics. Value is conserved across a
   twin-scale aggregation (IC-1).
3. **QoL ⟷ human digital twin.** The welfare objective's life-length / health /
   education dimensions AGGREGATE from human-digital-twin state (population = Σ twins),
   not exogenous.
4. **Ecosystem assets ⟷ biosphere.** Jacob's-ladder ecosystem / natural-capital assets
   bind to the GAIA biosphere state; renewable regeneration rate is a world-model read.

### Teeth (both directions — a control that never fires is suspect)

| Tooth | Binding | Fires when | Verdict |
| --- | --- | --- | --- |
| `T1-CONST` | 1 | carrying-capacity source is a hardcoded constant, not a world-model read | REJECT (free-parameter smell) |
| `T1-RESERVE` | 1 / 4 | a non-renewable draw takes a stock below the world-model's declared reserve floor | FLAG (planetary-boundary breach; the paper-inductance false-growth analog) |
| `T2-CONSERVE` | 2 | a cross-scale flow creates value out of nothing (`parent ≠ Σchildren + Σsinks − Σsources`) | REJECT |
| `T3-QOL` | 3 | a population QoL dimension is not derivable from human-twin dimensions | REJECT (exogenous-QoL smell) |
| `T4-REGEN` | 4 | a renewable-harvest regeneration rate is a constant, not a world-model read | REJECT |
| `T5-RESOLVE` | 1 / 4 | a `world_model_read` `read_ref` does not resolve to a declared biosphere-state entry | REJECT (a read pointing at nothing) |
| `T6-COMPOSE` | 2 | a transfer's `scale_stack` / parent→child scales are inconsistent with the declared twin-hierarchy composition | REJECT |

`T5-RESOLVE` is what makes `T1-CONST` / `T1-RESERVE` / `T4-REGEN` load-bearing: a source
may not merely *claim* to be a world-model read — its ref must resolve to declared
substrate-*W* biosphere state at that `@<as_of>`. The checker also fails CI if any
declared tooth is **never** exercised in the firing direction (no dead teeth), and
asserts the admitted fixtures fire **no** tooth.

A follow-up tooth `T7-CONCEPT` is documented (not yet enforced): once the ontogenesis
concept-governance PR provides stable Systema Concept Entry IDs, reject vocabulary terms
that do not resolve to a governed concept ID (bare-string → concept-ID).

## Consequences

- The economic spine acquires a machine-checkable place in the world model: a
  value-flow run is admissible only if its ecological and human terms READ from *W*.
- GAIA remains the semantic/provenance home; EP remains the value engine. Neither is
  forked into the other.
- The welfare-annealing files are **not edited** by this ADR; they are consumed by
  branch-ref as a forward soft-ref.

## Non-goals

- No new repository is created.
- No welfare-annealing source file is modified; no economic-prophet code is vendored.
- No live/shared-state read or write is performed; the contract validates static
  fixtures only.
- This ADR does not redefine value (UVMC/EP remains the additive measure) and does not
  claim GAIA is a complete Earth simulator.

## Initial implementation package

- `docs/decisions/ADR-0003-economic-spine-value-flow-subsystem.md` (this file)
- `docs/contracts/VALUE_FLOW_SUBSYSTEM_CONTRACT.md`
- `schemas/economy/value_flow_binding.v1.schema.json`
- `schemas/economy/twin_scale_transfer.v1.schema.json`
- `schemas/biosphere/biosphere_state.v1.schema.json` (the substrate-*W* resolution target)
- `schemas/economy/twin_hierarchy_composition.v1.schema.json`
- `examples/economy/value_flow/**` (valid + invalid + flag fixtures, one per tooth,
  both directions)
- `examples/biosphere/**` (declared biosphere/resource state the reads resolve to)
- `gaia/twins/composition.v1.json` (the first-class twin-hierarchy composition record)
- `scripts/validate_value_flow_subsystem.py` (deterministic, stdlib only)
- `.github/workflows/value-flow-subsystem.yml`

## Cross-references

- **Ontogenesis (sibling agent).** The concept lifecycle / Systema Concept Entry
  governs the *vocabulary* used here (`carrying_capacity`, `natural_capital`,
  `renewable_harvest`, `qol_index`, twin-scale terms). This ADR *references* those
  governed concepts and does not duplicate them; the terms should resolve against the
  ontogenesis concept-governance PR once landed.
- **economic-prophet**: `asset_ladder` (ALC-1) rung ontology; `risk_measures`
  (expected-shortfall) tail measure; `feat/welfare-annealing` dynamics.
- **prophet-workspace** ADR-0003 (RCS/4D) — the WorldModelSubstrate *W* naming.
- ADR-0002 — GAIA as the home for world-model layer contracts.
