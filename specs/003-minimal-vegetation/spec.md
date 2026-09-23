# Phase 1C — Minimal Spatial Vegetation

**Status:** APPROVED FOR IMPLEMENTATION  
**Risk:** STANDARD  
**Issue:** #10

## Goal

Add the first ecological entity to Simu_monde: a plant that occupies a real 2D position, stores edible biomass, and regrows deterministically over simulation time.

This phase creates the resource landscape for the next herbivore experiment. It must remain intentionally simple.

## Scientific simplification

The V1 plant does not model:

- water;
- sunlight;
- carbon;
- nutrients;
- roots;
- reproduction;
- death;
- competition;
- seasons.

Its biomass regrowth is treated as an **explicit simplified external input**.

Therefore this phase must not claim physical biomass conservation.

## Domain model

### Plant

Preferred location:

`src/simu_monde/core/vegetation.py`

Preferred shape:

```python
@dataclass(slots=True)
class Plant:
    plant_id: int
    position: Position2D
    edible_biomass_kg: float
    max_edible_biomass_kg: float
    growth_rate_kg_per_s: float
```

### Validation

`plant_id`:

- integer;
- boolean is invalid;
- >= 0.

`position`:

- valid finite `Position2D`;
- world membership is checked when plants enter a world/scenario, not by `Plant` itself.

`edible_biomass_kg`:

- finite;
- >= 0;
- <= `max_edible_biomass_kg`.

`max_edible_biomass_kg`:

- finite;
- > 0.

`growth_rate_kg_per_s`:

- finite;
- >= 0.

Invalid domain numeric values raise `ValueError`; invalid ID type raises `TypeError`.

Do not introduce a project-wide custom exception hierarchy.

## Growth rule

For one simulation tick:

```text
new_biomass =
    min(
        max_edible_biomass_kg,
        edible_biomass_kg + growth_rate_kg_per_s * dt_seconds
    )
```

Growth is deterministic.

No randomness is used during growth.

### PlantGrowthSystem

Preferred shape:

```python
class PlantGrowthSystem:
    def step(self, plants: Sequence[Plant], dt_seconds: float) -> None:
        ...
```

The system mutates only `edible_biomass_kg`.

It must not:

- move plants;
- create plants;
- delete plants;
- use RNG;
- access Pygame;
- know about animals.

## World ownership

Extend `World` with a minimal vegetation collection.

Preferred constructor evolution:

```python
class World:
    def __init__(
        self,
        config: SimulationConfig,
        plants: Iterable[Plant] = (),
    ) -> None:
        ...
```

The world owns its plant objects.

Expose them read-only structurally:

```python
@property
def plants(self) -> tuple[Plant, ...]:
    ...
```

The tuple prevents external structural append/remove operations while allowing the domain system to mutate plant biomass through the owned `Plant` objects.

On world construction:

- every plant position must lie inside `WorldBounds`;
- plant IDs must be unique;
- preserve input order;
- do not silently clamp invalid positions.

Out-of-bounds plants or duplicate IDs raise `ValueError`.

Do not build a generic entity registry or ECS.

## Simulation integration

Extend the existing `Simulation` directly and explicitly.

Preferred:

```python
class Simulation:
    def __init__(
        self,
        world: World,
        plant_growth_system: PlantGrowthSystem | None = None,
    ) -> None:
        ...
```

If not supplied, create the default `PlantGrowthSystem`.

One `Simulation.step()` must execute in this exact order:

```text
1. grow plants using current fixed dt
2. advance clock by one tick
```

Rationale:

- state transition occurs over `[t, t + dt]`;
- clock then marks completion of the transition.

Do not add a generic scheduler yet.

## Deterministic plant placement

Provide a dedicated helper/factory in the core, for example:

```python
def create_uniform_plants(
    *,
    rng: SeededRNG,
    bounds: WorldBounds,
    count: int,
    initial_biomass_kg: float,
    max_biomass_kg: float,
    growth_rate_kg_per_s: float,
) -> tuple[Plant, ...]:
    ...
```

Rules:

- `count >= 0`;
- IDs are deterministic: `0 .. count-1`;
- for each plant, draw X then Y from the supplied RNG;
- position mapping:

```text
x = rng.random() * bounds.width_m
y = rng.random() * bounds.height_m
```

- generated positions are therefore inside the half-open interior `[0,width) × [0,height)`;
- do not create another RNG;
- do not seed internally;
- caller owns the RNG and therefore the replay contract.

Do not use rejection sampling, clustering, Poisson-disc placement or spatial noise yet.

## Viewer scenario

Replace the current visual-only sample markers with actual core `Plant` objects.

The viewer default scenario may create a deterministic field such as:

- seed: existing default seed 42;
- plant count: 100;
- initial biomass: 0.5 kg;
- max biomass: 1.0 kg;
- growth rate: 0.02 kg/s.

These values are **demonstration parameters**, not biological claims.

The viewer reads `simulation.world.plants` and draws them.

Suggested rendering:

- green primitive circle;
- fixed radius is acceptable;
- optionally scale a small visual property by biomass if kept purely presentational.

Pygame must never own or mutate plant biomass.

## Interaction with pause/run

Existing viewer behavior remains:

- paused -> no `Simulation.step()` -> no growth;
- single-step -> exactly one growth update + one clock tick;
- running -> controller determines how many fixed core ticks are executed from accumulated real elapsed time;
- FPS does not change `dt_seconds`.

## Tests

### Plant validation

Test:

- valid plant;
- zero biomass accepted;
- biomass == max accepted;
- negative biomass rejected;
- biomass > max rejected;
- zero/negative max rejected;
- negative growth rejected;
- NaN/Inf rejected;
- bool/non-int plant ID rejected;
- negative integer plant ID rejected.

### Growth tests

Test:

- exact linear growth below cap;
- growth capped at maximum;
- zero growth rate leaves biomass unchanged;
- already-full plant stays full;
- one simulation step grows exactly `rate * dt`;
- N steps produce expected capped result.

Use suitable float comparison where required.

### World tests

Test:

- world accepts valid plants;
- plants property is structurally immutable tuple;
- duplicate IDs rejected;
- out-of-bounds position rejected;
- exact boundary position accepted;
- original world configuration/bounds behavior remains unchanged.

### Placement tests

Test:

- count zero returns empty tuple;
- correct count and IDs;
- all positions in bounds;
- same seed -> identical positions;
- different representative seeds -> different positions;
- RNG draw order/replay remains deterministic.

Do not hard-code CPython random numeric outputs; compare same-seed instances.

### Viewer tests

Test without opening a real window where possible:

- default viewer scenario contains actual plants from core;
- rendering input derives from `world.plants`;
- resize does not mutate biomass;
- viewer modules do not move plant domain logic out of core.

Do not add brittle GUI pixel screenshots.

## Architecture protections

The core must not import:

- pygame;
- PyInstaller;
- renderer code.

The vegetation module must not import adapter modules.

The adapter may import `Plant` and read its state.

## Acceptance criteria

1. Core contains a minimal `Plant` entity.
2. Plants have stable IDs and continuous positions.
3. World owns a deterministic plant collection.
4. Initial placement is seed-replayable.
5. Growth occurs only through simulation ticks.
6. Growth is capped.
7. Viewer displays actual core plants.
8. Pause/single-step visibly preserve simulation semantics.
9. No water, animals, memory, reproduction or generic ECS added.
10. Existing Windows executable build remains green.
11. pytest, Ruff and mypy pass.

## Non-goals

- feeding/eating;
- plant removal;
- animal perception;
- movement;
- memory;
- plant reproduction;
- death;
- water;
- climate;
- nutrients;
- competition;
- spatial indexing;
- performance optimization.

## STOP conditions

Stop and return to the Primary Pilot if implementation appears to require:

- generic entity framework/ECS;
- scheduler/event-bus architecture;
- water/nutrient semantics;
- plant reproduction or death;
- feeding semantics;
- animal rules;
- memory;
- spatial partitioning;
- changing deterministic RNG semantics;
- moving ecological logic into Pygame.

## Completion report

Codex should report:

1. files changed;
2. public vegetation API;
3. simulation order;
4. deterministic placement behavior;
5. viewer changes;
6. tests/checks;
7. Windows executable workflow status;
8. deviations, if any;
9. PR link.
