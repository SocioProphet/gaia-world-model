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
| `BiosphereState` | `schemas/biosphere/biosphere_state.v1.schema.json` | A declared snapshot of substrate-*W* biosphere/resource state (carrying-capacity index, reserves + floors, regeneration rates, planetary boundaries). The **resolution target** for a binding's `world_model_read` refs. Fixtures under `examples/biosphere/**`. |
| `TwinHierarchyComposition` | `schemas/economy/twin_hierarchy_composition.v1.schema.json` | The first-class declaration of the twin hierarchy (`gaia/twins/composition.v1.json`): ordered stack + explicit parent/child scale edges. The authority a transfer's `scale_stack` and parent/child scales must be consistent with. |

## Resolution — reads must point at something

A `world_model_read` is not a claim, it is a **resolvable reference**. Every `read_ref` a
binding declares (carrying-capacity, renewable regeneration, reserve floor) MUST resolve
to a declared `BiosphereState` entry — a canonical `gaia://biosphere/<path>@<as_of>`
reference answered by `examples/biosphere/**`. This is what makes `T1-CONST` /
`T1-RESERVE` / `T4-REGEN` load-bearing: a source may not merely *declare*
`kind: world_model_read`, its ref must land on substrate-*W* state that actually exists
at that `@<as_of>` (see tooth `T5-RESOLVE`).

Likewise the twin hierarchy is not an ad-hoc array: every `TwinScaleValueTransfer` is
checked against the declared `TwinHierarchyComposition` record (see tooth `T6-COMPOSE`).

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
- **`T5-RESOLVE` → REJECT.** A carrying-capacity / regeneration / reserve `read_ref`
  that does not resolve to a declared `BiosphereState` entry is a read pointing at
  nothing, and is rejected.

### Binding 2 — Twin-hierarchy composition + value conservation (IC-1)

The scale stack is declared explicitly, backed by a first-class `TwinHierarchyComposition`
record, and value flows are its exchange dynamics.

- **`T2-CONSERVE` → REJECT.** Value is conserved across a twin-scale aggregation:
  `parent.value == Σ children + Σ declared_sinks − Σ declared_sources` (within
  `conservation.tolerance`). A cross-scale flow that creates value out of nothing —
  children exceeding the parent with no receipted source — is rejected. Injections and
  removals are legal only when receipted as `declared_sources` / `declared_sinks`.
- **`T6-COMPOSE` → REJECT.** A transfer whose `scale_stack` is not the declared
  `ordered_stack`, or whose parent→child scales are not an adjacent parent→child edge in
  the composition record, is rejected (e.g. a galactic→human transfer that skips the
  world-economic scale).

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
- **`T5-RESOLVE`** (above) also applies: a renewable regeneration `read_ref` must
  resolve to a declared `BiosphereState` regeneration entry.

### Concept governance — vocabulary binds to governed concepts (ontogenesis#141)

Every governed bare enum (`carrying_capacity`, the three rungs, `qol_index` + its
`life_length` / `health` / `education` dimensions, and the three twin-scale terms) carries
a `concept_ref` — the Systema Concept Entry ID registered in **ontogenesis#141** (registry
`Platform/Systema/`, `systema:concept:*`). The 11 governed IDs are the authority; this
contract references them, it does not define vocabulary.

- **`T7-CONCEPT` → FLAG.** A governed bare enum used **without** its `concept_ref` (where
  one of the 11 exists) is flagged — prefer-governed-ID (the transition nudge).
- **`T7-CONCEPT` → REJECT.** A `concept_ref` that is **not** one of the 11 governed IDs,
  or is the **wrong** governed concept for its enum, is rejected.

## Verdict semantics

| Decision | Meaning |
| --- | --- |
| `admit` | Binding/transfer reads from *W*, conserves value, and its governed vocabulary carries correct `concept_ref`s; no tooth fired. |
| `admit_with_flag` | Admissible, but a receipt is raised: a planetary-boundary breach (`T1-RESERVE`) or a missing-but-governable `concept_ref` (`T7-CONCEPT`). |
| `reject` | A tooth fired; the run is not admissible as a value-flow subsystem run. |

## Consumed soft-refs (by reference, never vendored)

- `SocioProphet/economic-prophet@a51a23f52dfe7b0e984a42a19a762dabe714a583` — the
  welfare-annealing dynamics (WEA-1), merged to main: carrying-capacity discount, QoL
  welfare objective, and `welfare_annealing/gaia_binding.py`, which emits the
  `value_flow_binding.v1` / `twin_scale_transfer.v1` records this contract governs
  (pinned soft-ref; its files are never edited here).
- `SocioProphet/economic-prophet` `asset_ladder` (ALC-1) — the rung ontology
  (`natural_capital` / `extractive_nonrenewable` / `renewable_harvest`).
- `SocioProphet/economic-prophet` `risk_measures` — expected-shortfall tail measure.
- `gaia/twins/human/twin-schema.json` — human-digital-twin state dimensions.
- `schemas/economy/economy_observation.v1.schema.json` — the pre-existing GAIA↔EP
  observation soft-ref this contract composes with.

## Cross-references — ontogenesis concept governance (sibling agent), ENFORCED

The vocabulary this contract uses is governed by the ontogenesis / **Systema Concept
Entry** concept lifecycle, owned by the sibling integration agent. The governed IDs are
**merged in ontogenesis#141** (registry `Platform/Systema/`, resolve against
`systema:concept:*`). This contract **references** those governed concepts by
`concept_ref`; it does not duplicate them. The 11 governed IDs:

| Bare enum | Governed Systema Concept Entry ID |
| --- | --- |
| `carrying_capacity` | `systema:concept:carrying-capacity` |
| `natural_capital` | `systema:concept:natural-capital` |
| `extractive_nonrenewable` | `systema:concept:extractive-nonrenewable` |
| `renewable_harvest` | `systema:concept:renewable-harvest` |
| `qol_index` | `systema:concept:qol-index` |
| `qol_index.life_length` | `systema:concept:qol-dim-life-length` |
| `qol_index.health` | `systema:concept:qol-dim-health` |
| `qol_index.education` | `systema:concept:qol-dim-education` |
| `galactic_space_twin` | `systema:concept:galactic-space-twin` |
| `world_economic_twin` | `systema:concept:world-economic-twin` |
| `human_digital_twin` | `systema:concept:human-digital-twin` |

Enforced by tooth `T7-CONCEPT` (above): the `concept_ref` sits beside each governed bare
enum in `value_flow_binding.v1` / `twin_scale_transfer.v1` and the composition record;
missing-but-governable is flagged, ungoverned/wrong is rejected.

## Enforcement

`scripts/validate_value_flow_subsystem.py` (deterministic, Python stdlib only) loads the
declared `BiosphereState` (`examples/biosphere/**`) and `TwinHierarchyComposition`
(`gaia/twins/composition.v1.json`), judges every fixture, asserts each fixture's
`_expected` verdict and tooth, and fails if any declared tooth is never exercised in the
firing direction (no dead teeth). Wired into CI by
`.github/workflows/value-flow-subsystem.yml`.
