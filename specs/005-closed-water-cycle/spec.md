# Phase 1F — Closed Water Cycle V1

**Status:** APPROVED FOR IMPLEMENTATION  
**Risk:** HIGH-RISK  
**Issue:** #2

## Goal

Add a strictly conserved modeled water cycle and a second competing herbivore need: thirst.

The purpose is to observe how a closed material loop changes the current plant/herbivore dynamics without yet adding memory, lifecycle, death or realistic hydrology.

## Central invariant

At every simulation tick:

```text
W_total =
    atmosphere_water_kg
  + soil_water_kg
  + sum(surface_source.water_kg)
  + sum(herbivore.body_water_kg)
```

must remain constant within:

```text
WATER_CONSERVATION_ABS_TOL_KG = 1e-8
```

No water reservoir may become negative.

If one simulation step violates the invariant beyond tolerance, raise a `RuntimeError` from the simulation layer with before/after totals.

Do not use `assert` for the runtime invariant.

## Scientific scope

Modeled water is conserved.

Biomass is **not** modeled as water. Plant growth still represents a simplified carbon/light/nutrient process, but water availability limits how much of the potential growth may occur.

Energy is not a water reservoir and does not create/destroy modeled water.

## Water domain

Preferred module:

`src/simu_monde/core/water.py`

### WaterSource

```python
@dataclass(slots=True)
class WaterSource:
    water_source_id: int
    position: Position2D
    water_kg: float
```

Validation:

- ID integer, non-bool, >= 0;
- position is `Position2D`;
- water finite and >= 0.

No capacity, depth, radius or shape yet.

### WaterState

```python
@dataclass(slots=True)
class WaterState:
    atmosphere_water_kg: float
    soil_water_kg: float
    surface_sources: tuple[WaterSource, ...]
```

Validation:

- atmosphere finite >= 0;
- soil finite >= 0;
- source IDs unique;
- source positions validated by `World` against world bounds.

The tuple is structurally immutable; source water amounts remain mutable domain state.

## World ownership

Extend `World` with water state.

Preferred:

```python
World(
    config,
    plants=(),
    herbivores=(),
    water_state: WaterState | None = None,
)
```

If omitted, create an empty state:

```text
atmosphere = 0
soil = 0
surface_sources = ()
```

Expose:

```python
@property
def water(self) -> WaterState:
    ...

@property
def total_water_kg(self) -> float:
    ...
```

`total_water_kg` must include herbivore body water.

World validates every water source position lies in bounds.

Do not build a generic ledger framework.

## Deterministic surface-water placement

Provide a factory using caller-supplied `SeededRNG`:

```python
create_uniform_water_sources(
    *,
    rng: SeededRNG,
    bounds: WorldBounds,
    count: int,
    water_kg_per_source: float,
) -> tuple[WaterSource, ...]
```

For each source, consume RNG in exact order:

1. x;
2. y.

IDs are `0..count-1`.

Do not reseed internally.

For the default viewer scenario, preserve existing plant/herbivore initial placement by consuming the existing placement sequence first, then create water sources after herbivores.

## Rainfall system

Preferred class:

```python
class RainfallSystem:
    def __init__(
        self,
        rain_rate_kg_per_s: float,
        soil_fraction: float,
    ) -> None:
        ...
```

Validation:

- rain rate finite >= 0;
- soil fraction finite in [0,1].

Per step:

```text
potential_rain = rain_rate_kg_per_s * dt_seconds
rain = min(atmosphere_water_kg, potential_rain)
```

If there are one or more surface sources:

```text
to_soil = rain * soil_fraction
to_surface_total = rain - to_soil
each source receives to_surface_total / source_count
```

If there are no surface sources:

```text
all rain -> soil
```

Then reduce atmosphere by exactly the amount transferred.

No random rainfall yet.

## Plant water limitation and transpiration

The existing `PlantGrowthSystem` changes semantics.

Add a system parameter:

```text
water_kg_per_biomass_kg > 0
```

Recommended default for the demo:

```text
0.2 kg water / kg biomass
```

For each plant, in stored order:

```text
potential_growth_kg =
    min(
        growth_rate_kg_per_s * dt_seconds,
        max_edible_biomass_kg - edible_biomass_kg
    )
```

Required water:

```text
required_water_kg =
    potential_growth_kg * water_kg_per_biomass_kg
```

Actual water used:

```text
used_water_kg =
    min(required_water_kg, soil_water_kg)
```

Actual biomass growth:

```text
actual_growth_kg =
    used_water_kg / water_kg_per_biomass_kg
```

State transition:

```text
soil_water_kg -= used_water_kg
plant.edible_biomass_kg += actual_growth_kg
atmosphere_water_kg += used_water_kg
```

This is simplified same-tick transpiration.

Consequences:

- no soil water -> no growth;
- partial water -> proportional partial growth;
- full plant -> no water transfer;
- water is conserved.

Do not add plant water storage.

## Herbivore water state

Extend `Herbivore` with:

```python
body_water_kg: float
max_body_water_kg: float
water_loss_kg_per_s: float
drinking_rate_kg_per_s: float
drinking_radius_m: float
drink_thirst_threshold: float
```

Validation:

- body water finite >= 0 and <= max;
- max body water finite > 0;
- loss rate finite >= 0;
- drinking rate finite >= 0;
- drinking radius finite >= 0;
- threshold finite in [0,1].

Expose computed thirst:

```python
@property
def thirst(self) -> float:
    return 1.0 - body_water_kg / max_body_water_kg
```

Clamp only for floating-point safety.

No health/death behavior occurs at zero body water.

That limitation is intentional and should be observable.

## Herbivore water loss

At the beginning of each herbivore update, after hunger accumulation:

```text
water_lost =
    min(
        body_water_kg,
        water_loss_kg_per_s * dt_seconds
    )

body_water_kg -= water_lost
atmosphere_water_kg += water_lost
```

This single transfer represents all unmodeled bodily water loss.

## Herbivore need priority

After hunger accumulation and body-water loss:

### 1. Thirst priority

If:

```text
thirst >= drink_thirst_threshold
```

the herbivore is in water-seeking mode.

It may perceive only surface sources where:

```text
source.water_kg > 0
distance <= perception_radius_m
```

Use the existing perception radius.

Target selection:

```text
min(distance_squared, water_source_id)
```

If target within `drinking_radius_m`, drink.

Otherwise move toward it using the existing direct-seek movement rule.

If thirsty but no water source is visible, explore.

While in thirst-priority mode, do not intentionally seek/eat plants.

### 2. Hunger

If thirst is below threshold, existing hunger behavior applies unchanged.

### 3. Exploration

Otherwise explore.

Do not persist water targets between ticks.

## Drinking

Potential drink:

```text
potential_drink_kg =
    drinking_rate_kg_per_s * dt_seconds
```

Needed:

```text
needed_kg =
    max_body_water_kg - body_water_kg
```

Actual:

```text
drunk_kg =
    min(
        potential_drink_kg,
        source.water_kg,
        needed_kg
    )
```

Transfer:

```text
source.water_kg -= drunk_kg
body_water_kg += drunk_kg
```

No water disappears.

## Passive evaporation

Preferred class:

```python
class EvaporationSystem:
    def __init__(
        self,
        soil_evaporation_rate_kg_per_s: float,
        surface_evaporation_rate_kg_per_s_per_source: float,
    ) -> None:
        ...
```

Both rates finite >= 0.

Per tick:

### Soil

```text
soil_evap =
    min(
        soil_water_kg,
        soil_evaporation_rate_kg_per_s * dt_seconds
    )

soil -= soil_evap
atmosphere += soil_evap
```

### Surface

For each source in stored order:

```text
surface_evap =
    min(
        source.water_kg,
        surface_rate * dt_seconds
    )

source -= surface_evap
atmosphere += surface_evap
```

No temperature model yet.

## Simulation order

The exact global order becomes:

```text
1. record total water before tick
2. RainfallSystem
3. PlantGrowthSystem (water-limited + transpiration)
4. HerbivoreBehaviorSystem
   - hunger accumulation
   - body-water loss
   - thirst/hunger decision
   - drinking/feeding/movement/exploration
5. EvaporationSystem
6. verify total-water invariant
7. clock.advance()
```

This supersedes the previous plant -> herbivore -> clock order.

Do not add a generic scheduler yet.

## Default demo scenario

These are demonstration parameters, not biological claims.

### Initial water

```text
atmosphere_water_kg = 200.0
soil_water_kg = 120.0

surface sources:
count = 3
water per source = 40.0 kg

herbivores:
body_water_kg = 0.70
max_body_water_kg = 1.00
```

With 12 herbivores, initial total modeled water is:

```text
200 + 120 + 3*40 + 12*0.70 = 448.4 kg
```

The executable should make this total observable.

### Rates

```text
rain_rate = 0.10 kg/s
rain soil fraction = 0.50

soil evaporation = 0.05 kg/s
surface evaporation = 0.02 kg/s per source

plant water coefficient = 0.20 kg water / kg biomass

herbivore water loss = 0.002 kg/s
herbivore drinking rate = 0.05 kg/s
herbivore drinking radius = 8 m
drink thirst threshold = 0.35
```

Existing hunger/food parameters remain unchanged.

These values are intended to make competition between accessibility, rainfall, evaporation and use observable at human timescales.

## Viewer

Render actual `WaterSource` objects as simple blue primitives clearly distinct from plants and herbivores.

Do not render rain particles/clouds.

Display at minimum:

```text
Total water: X.XX kg
Atmosphere: X.XX kg
Soil: X.XX kg
Surface: X.XX kg
Animal body water: X.XX kg
```

These values come from core state.

Viewer must not transfer water.

## Tests

### Water domain

Cover validation for all water values, IDs, duplicate IDs and bounds.

### Rain

Test:

- exact transfer amount;
- capped by atmosphere;
- soil/surface split;
- equal surface distribution;
- no-source fallback to soil;
- zero rate;
- conservation.

### Plant-water coupling

Test:

- enough soil water -> full potential growth;
- insufficient water -> proportional growth;
- zero soil -> zero growth;
- full plant -> no transfer;
- exact soil decrease equals atmospheric increase;
- plant biomass never exceeds max.

### Herbivore thirst

Test:

- thirst computed correctly;
- water loss transfers body -> atmosphere;
- body water never negative;
- thirst priority overrides hunger;
- thirsty + no visible water -> exploration, no plant targeting;
- nearest visible non-empty source selected;
- ties by source ID;
- drinking limited by rate/source/need;
- drinking conserves water;
- empty water sources ignored.

### Evaporation

Test soil and surface transfers, source depletion floor, zero rates and conservation.

### Global conservation

For representative scenarios:

- one tick;
- hundreds of ticks;
- same-seed replay;
- drinking while plants grow;
- source depletion;
- drought-like accessible-water shortage.

Assert:

```text
abs(total_after - total_initial) <= 1e-8 kg
```

### Replay

Equal seed + equal configuration must replay equal:

- plants;
- herbivore positions/headings;
- hunger;
- body water/thirst;
- atmosphere water;
- soil water;
- source water;
- RNG continuation;
- clock.

### Viewer

Test actual water sources are rendered from core state and resize/render does not mutate water.

### Regression

Existing vegetation/herbivore behavior remains valid except where plant growth is intentionally water-limited.

Windows executable workflow must remain green.

## Acceptance criteria

1. Total modeled water is conserved each tick.
2. No water reservoir becomes negative.
3. Plant growth requires soil water.
4. Plant water use transfers soil -> atmosphere.
5. Rain transfers atmosphere -> soil/surface.
6. Evaporation transfers soil/surface -> atmosphere.
7. Herbivores lose body water to atmosphere.
8. Herbivores drink surface water into body water.
9. Thirst has priority over hunger above threshold.
10. No memory is introduced.
11. Water sources are spatial and visible.
12. Same seed replays same water/ecology trajectory.
13. Pygame remains presentation-only.
14. Windows executable workflow remains green.
15. pytest, Ruff and mypy pass.

## Non-goals

- local soil moisture;
- realistic rainfall stochasticity;
- clouds;
- rivers;
- groundwater;
- runoff;
- infiltration physics;
- water-source geometry;
- dehydration damage/death;
- excretion model;
- water contained inside plants;
- carbon/mass conservation of biomass;
- memory;
- reproduction;
- climate;
- temperature;
- spatial indexing;
- ECS.

## STOP conditions

Stop and return to the Primary Pilot if implementation requires:

- creating/destroying modeled water;
- changing total-water definition;
- adding a new water reservoir not specified here;
- changing fixed timestep semantics;
- adding stochastic rain;
- adding memory;
- adding death/lifecycle;
- adding realistic hydrology;
- moving any water/ecology rule into Pygame;
- adding a generic scheduler/ECS;
- changing RNG ownership.

## Completion report

Codex reports:

1. files changed;
2. water state/public API;
3. exact simulation order;
4. total-water invariant implementation;
5. plant-water coupling;
6. thirst/drinking behavior;
7. replay evidence;
8. test/check results;
9. Windows executable artifact status;
10. deviations;
11. PR link.
