# smart-economy domain

The `smart-economy` domain is GAIA's first non-geospatial domain. It does **not**
define its own economics — it **binds GAIA's world model to the Economic Prophet
framework** (`SocioProphet/economic-prophet`), which is the canonical economic
engine for the SocioProphet stack. GAIA supplies the world-model envelope,
provenance, and Earth/geo binding; Economic Prophet supplies value, profitability,
and policy simulation.

It plugs into the standard GAIA pipeline:

**CV (sources) → canonical ontology → validation → actions (observe/audit/plan/actuate) → reports**

## Why bind, not reinvent

An earlier draft of this domain introduced a parallel `value_model_record`
(`V = N + L + C`). That was withdrawn: Economic Prophet already formalizes the
same economics, and the SocioProphet stack standardizes on it. The founding
world-model design notes map onto Economic Prophet constructs as follows.

| Founding notes (`drive-download-20260510T173010Z-3-001`) | Economic Prophet construct |
|---|---|
| `V = N + L + C` value algebra; "value" | **Economic Profit (EP)** — UVMC's canonical additive value measure (`ep_output.schema.json`) |
| Compositional `V = N(L)+L(C)+N(L(C))`, factor partitions | EP components + **UVMC** dimensions / industry overlays / KPI trees |
| Law as a friction operator on flows | **policy_simulation_profile** (actors, planner, reward functionals, triparty faces) |
| "All stats/models public"; open logic engine; provenance | **UVMC lineage** (`input_hash`/`output_hash`) + `uvmc_calculation_receipt` + policy `donor_corpus` license/attribution |
| Census/tax/demographics, demand, barriers | UVMC measured entities + governed `uvmc_dimension` reference records |
| `g2.gif` evidence decision tree | A declarative `audit` action over a `policy_simulation_profile` |

## Canonical value identity

Economic Profit is the additive backbone (UVMC design rule 1):

```
economic_profit = revenue - expected_loss - expense
                  - funding_costs + funding_credits - taxes - capital_charge
```

The bundled sample uses Economic Prophet's own synthetic numbers
(`examples/lineage_ep_output.json`): `1000 - 100 - 50 - 200 + 10 - 40 - 496.55 = 123.45`.
The validator enforces this identity and rejects the negative fixture
(`economic_profit = 999.99`).

> The founding notes' conserved-residual sketch `r = n mod M` has no native
> Economic Prophet counterpart and was **not** carried into the schema; the EP
> additive identity is the real conservation law. The `r = n mod M` idea is
> preserved only in the founding-notes synthesis as an open question for the model
> author (see Open gaps).

## Record shape

A `EconomyObservation` (`schemas/economy/economy_observation.v1.schema.json`) is a
GAIA envelope wrapping Economic Prophet outputs:

- `economic_prophet.ep_output` — conforms to economic-prophet `ep_output.schema.json`.
- `economic_prophet.measurement_context` — conforms to economic-prophet
  `uvmc_measurement_context.schema.json` (object/period/scenario/model/parameter/
  formula + lineage).
- `economic_prophet.policy_simulation_profile_ref` — optional link to the law/policy layer.
- Standard GAIA `source` / `provenance` / `governance` / `classification`.

## Law-as-action (policy audit)

The `g2.gif` evidence-admissibility decision tree is realized as a GAIA `audit`
action over an Economic Prophet `policy_simulation_profile`:

- `fixtures/economy/action-intent.policy-audit.v1.json` — a GAIA `ActionIntent`
  (`verb=audit`) whose `constraints.decision_steps` encode the admissibility tree
  (relevance → hearsay → opinion → tendency → credibility → identification →
  privilege → discretionary-exclusion).
- `fixtures/economy/policy-decision.policy-audit.v1.json` — the resulting GAIA
  `PolicyDecision` (`review`), citing the profile, its audit receipt, the triparty
  face, and the audit action as `evidence_refs`.

Law is thus a friction operator: the audit never self-releases when the triparty
face residual sits above threshold and the reward functional is advisory-only.

## Network-of-networks topology

The founding notes' coupled networks are schematized in
`schemas/economy/economy_network_topology.v1.schema.json`:

- `networks` — the eight founding-notes networks (resource, distribution, labor,
  capital, political, information, time, geographic).
- `nodes` — each binds to an Economic Prophet `economic_object_type` + `object_ref`
  (and, for geographic nodes, a GAIA `geo_ref`); the political network's
  `friction_model` points at a `policy_simulation_profile`.
- `edges` — typed flows (value, labor, capital, authority, location).

The sample (`fixtures/economy/economy-network-topology.sample.v1.json`) is derived
from Economic Prophet's `examples/object_graph.json` (entity → line-of-business →
relationship → account → instrument) plus the political and geographic bindings.

## Artifacts in this domain

- `docs/DOMAIN_MATRIX.md` — `smart-economy` row + summary.
- `schemas/economy/economy_observation.v1.schema.json` — EP/UVMC binding schema.
- `schemas/economy/economy_network_topology.v1.schema.json` — network-of-networks schema.
- `fixtures/economy/economy-observation.sample.v1.json` — positive observation fixture.
- `fixtures/economy/economy-network-topology.sample.v1.json` — topology fixture.
- `fixtures/economy/action-intent.policy-audit.v1.json` + `…/policy-decision.policy-audit.v1.json` — law-as-action.
- `fixtures/economy/negative/economy-observation.broken-ep-identity.v1.json` — negative fixture.
- `scripts/validate_economy_fixtures.py` — validator (EP identity + UVMC context + topology
  referential integrity + policy-audit; cross-validates against a sibling
  `economic-prophet` checkout when present).

Run validation:

```bash
python3 scripts/validate_economy_fixtures.py
```

## Open gaps (carried from the founding-notes synthesis)

- **No growth/rate dynamics in GAIA's binding.** Economic Prophet is period/horizon
  aware (EP per period, cadence), so time-evolution lives there; GAIA currently
  records point-in-time observations and does not yet drive a multi-period roll-up.
- **Network-of-networks topology not yet schematized.** The founding notes' resource/
  distribution/labor/capital/political/information networks map to Economic Prophet's
  object graph + UVMC dimensions, but GAIA has no topology record yet.
- **policy_simulation binding is by-reference only.** The law-as-friction layer is
  linked, not embedded; a GAIA action template over `policy_simulation_profile`
  (the `g2.gif` pattern) is the next artifact.
- **CV ingestion of real calibration data** (census/tax/land-sales) is not wired; the
  sample fixture reuses Economic Prophet's synthetic example.
- **Conserved-quantity `r = n mod M`** from the notes is unmapped by design pending
  author intent.
