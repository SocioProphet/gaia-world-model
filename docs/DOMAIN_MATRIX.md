# Domain matrix

| Domain | Primary assets | Control surface | Status |
|---|---|---|---|
| smart-home | rooms, devices, routines | observe / plan / actuate | draft |
| smart-building | floors, HVAC, occupancy, safety | observe / plan / actuate | draft |
| smart-car | vehicle, telemetry, route, driver-agent | observe / plan / actuate | draft |
| smart-fleet | vehicles, depot, dispatch, maintenance | observe / plan / actuate | draft |
| smart-grid | circuits, batteries, meters, tariffs | observe / plan / actuate | draft |
| smart-factory | machines, lines, jobs, safety zones | observe / plan / actuate | draft |
| smart-campus | buildings, utilities, incidents, mobility | observe / plan / actuate | draft |
| cloud-network | hosts, services, links, policies | observe / plan / actuate | draft |
| robot-drone | robot, workspace, mission, hazard | observe / plan / actuate | draft |
| warehouse-logistics | pallets, docks, robots, shipments | observe / plan / actuate | draft |
| farm-watershed | fields, soil, irrigation, forecast | observe / plan / actuate | draft |
| hospital-clinic | rooms, devices, protocols, orders | observe / plan / actuate | draft |
| smart-economy | legal entities, lines of business, relationships, accounts, instruments | observe / audit / plan / actuate | draft |

## smart-economy domain

The `smart-economy` domain is GAIA's first non-geospatial domain. It does not
define its own economics — it **binds GAIA to the Economic Prophet framework**
(`SocioProphet/economic-prophet`), the canonical economic engine for the stack.

- Value: **Economic Profit (EP)** — UVMC's canonical additive value measure.
- Measurement: Economic Prophet **UVMC measurement context** (period/scenario/model/lineage).
- Law/policy: Economic Prophet **policy simulation** (law modeled as friction on flows).
- GAIA contributes the world-model envelope, provenance, governance, and geo binding.

See `docs/SMART_ECONOMY_DOMAIN.md` for the full design, the founding-notes mapping,
and source provenance.
