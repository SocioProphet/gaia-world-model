# GAIA Value-Flow Subsystem Contract

Status: v1 (binding, with teeth)
Date: 2026-08-03
Decision: [ADR-0003](../decisions/ADR-0003-economic-spine-value-flow-subsystem.md)

## Scope

This contract binds the estate's **economic spine** (Economic Prophet omnirisk/EP + the
in-flight welfare-annealing dynamics) UPWARD into the **GAIA world model** as its
**value-flow subsystem**, and places it in the digital-twin hierarchy. It does not
redefine value (UVMC/EP remains the additive measure). It declares what the spine must
READ from the world-model substrate *W*, and enforces it with teeth in both directions.

Consume-not-fork: economic-prophet kernels and the welfare-annealing branch are
referenced by pinned ref; nothing is vendored. The contract validates static fixtures
only — no live or shared-state read/write.

## Objects

| Object | Schema | Purpose |
| --- | --- | --- |
| `ValueFlowSubsystemBinding` | `schemas/economy/value_flow_binding.v1.schema.json` | A welfare/EP run's declaration of how its carrying-capacity, ecosystem assets, and QoL objective READ from *W*. |
| `TwinScaleValueTransfer` | `schemas/economy/twin_scale_transfer.v1.schema.json` | A value flow across an adjacent boundary of the twin hierarchy, carrying the IC-1 conservation rule. |

## The twin hierarchy

```
galactic_space_twin  ⟷  world_economic_twin (this spine)  ⟷  human_digital_twin
        (SpaceTwin.vue / 5D cube)   (economic-prophet)         (prophet-health / gaia twins)
```

Value flows are the exchange dynamics across this stack. Every `TwinScaleValueTransfer`
declares the full `scale_stack` and moves value between two adjacent scales.

## The four bindings and their teeth

A control that never fires is suspect. Each tooth is exercised in BOTH directions by the
committed fixtures under `examples/economy/value_flow/`: at least one admitted fixture
where the tooth stays silent, and at least one fixture where it fires.

### Binding 1 — Carrying-capacity ⟷ Gaia biosphere

The welfare-annealing carrying-capacity discount and the Jacob's-ladder natural-capital /
renewable base MUST be a READ of the GAIA biosphere/resource state
(`carrying_capacity.source.kind == "world_model_read"` with a resolvable `read_ref`).

- **`T1-CONST` → REJECT.** A binding whose carrying-capacity source is `constant` is a
  hardcoded free parameter — the free-parameter smell — and is rejected.
- **`T1-RESERVE` → FLAG.** A value-flow that draws a non-renewable stock below the
  world-model's declared reserve floor (`current − non_renewable_draw < reserve.floor`)
  is flagged as a planetary-boundary breach — the "paper-inductance false-growth"
  analog: growth booked against a stock the world model says isn't there. The run is
  admitted **with a flag** (the flag is the receipt), not rejected.

### Binding 2 — Twin-hierarchy composition + value conservation (IC-1)

The scale stack is declared explicitly and value flows are its exchange dynamics.

- **`T2-CONSERVE` → REJECT.** Value is conserved across a twin-scale aggregation:
  `parent.value == Σ children + Σ declared_sinks − Σ declared_sources` (within
  `conservation.tolerance`). A cross-scale flow that creates value out of nothing —
  children exceeding the parent with no receipted source — is rejected. Injections and
  removals are legal only when receipted as `declared_sources` / `declared_sinks`.

### Binding 3 — QoL ⟷ human digital twin

The welfare objective's life-length / health / education dimensions MUST AGGREGATE from
human-digital-twin state (population = Σ twins). Each dimension carries
`derivation.kind == "twin_aggregate"` and a `from_twin_dimension` reference into
`gaia/twins/human/**`.

- **`T3-QOL` → REJECT.** A population QoL index with any `exogenous` dimension, or a
  `twin_aggregate` dimension missing its `from_twin_dimension`, is not derivable from
  its constituent human twins and is rejected.

### Binding 4 — Ecosystem assets ⟷ biosphere

Jacob's-ladder ecosystem / natural-capital assets bind to the GAIA biosphere state
(`biosphere_ref`); renewable regeneration rate is a world-model read.

- **`T4-REGEN` → REJECT.** A `renewable_harvest` rung whose `regeneration.source.kind`
  is `constant` (or `none`) instead of `world_model_read` is rejected. Depleting rungs
  (`natural_capital`, `extractive_nonrenewable`) may carry `none`.

## Verdict semantics

| Decision | Meaning |
| --- | --- |
| `admit` | Binding/transfer reads from *W* and conserves value; no tooth fired. |
| `admit_with_flag` | Admissible, but a planetary-boundary breach is receipted (`T1-RESERVE`). |
| `reject` | A tooth fired; the run is not admissible as a value-flow subsystem run. |

## Consumed soft-refs (by reference, never vendored)

- `SocioProphet/economic-prophet@feat/welfare-annealing` — carrying-capacity discount,
  QoL welfare objective (forward soft-ref; the branch's files are never edited here).
- `SocioProphet/economic-prophet` `asset_ladder` (ALC-1) — the rung ontology
  (`natural_capital` / `extractive_nonrenewable` / `renewable_harvest`).
- `SocioProphet/economic-prophet` `risk_measures` — expected-shortfall tail measure.
- `gaia/twins/human/twin-schema.json` — human-digital-twin state dimensions.
- `schemas/economy/economy_observation.v1.schema.json` — the pre-existing GAIA↔EP
  observation soft-ref this contract composes with.
- Ontogenesis / Systema Concept Entry (sibling agent) — governs the vocabulary; this
  contract references governed concepts, it does not duplicate them.

## Enforcement

`scripts/validate_value_flow_subsystem.py` (deterministic, Python stdlib only) judges
every fixture, asserts each fixture's `_expected` verdict and tooth, and fails if any
declared tooth is never exercised in the firing direction. Wired into CI by
`.github/workflows/value-flow-subsystem.yml`.
