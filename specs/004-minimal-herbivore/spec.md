# Phase 1D — Minimal Herbivore

**Status:** APPROVED FOR IMPLEMENTATION  
**Risk:** STANDARD-HIGH  
**Issue:** #13

## Goal

Add the first autonomous animal and create the first ecological feedback loop in Simu_monde.

The herbivore should produce behavior from local rules only:

```text
hunger -> local perception -> movement -> feeding -> changed resource field
```

Memory, social behavior and water remain out of scope.

## Domain model

Preferred module:

`src/simu_monde/core/herbivore.py`

Preferred entity:

```python
@dataclass(slots=True)
class Herbivore:
    herbivore_id: int
    position: Position2D
    hunger: float
    heading_rad: float
    speed_m_per_s: float
    perception_radius_m: float
    feeding_radius_m: float
    hunger_rate_per_s: float
    feeding_rate_kg_per_s: float
    food_capacity_kg: float
    seek_food_hunger_threshold: float
```

### Meaning of hunger

- 0.0 = satiated;
- 1.0 = maximally hungry;
- clamp to [0, 1].

No health, energy reserve, body mass or death yet.

### Validation

IDs:
- integer, non-bool;
- >= 0.

Finite non-negative:
- speed;
- perception radius;
- feeding radius;
- hunger rate;
- feeding rate.

Strictly positive:
- food capacity.

Bounded:
- hunger in [0,1];
- seek threshold in [0,1].

Heading:
- finite float;
- normalization to [0, 2π) is allowed at construction/update.

Do not introduce custom exception hierarchies.

## World ownership

Extend `World` minimally:

```python
World(config, plants=(), herbivores=())
```

Requirements:

- ordered tuple ownership;
- unique herbivore IDs;
- every herbivore position inside bounds;
- no generic entity registry/ECS.

Expose:

```python
@property
def herbivores(self) -> tuple[Herbivore, ...]:
    ...
```

## Hunger accumulation

At each simulation tick:

```text
hunger = min(1.0, hunger + hunger_rate_per_s * dt_seconds)
```

This happens before decision/feeding.

## Food-seeking gate

An herbivore actively seeks food when:

```text
hunger >= seek_food_hunger_threshold
```

When below threshold, it explores and does not intentionally target or consume food.

This threshold is a simple behavioral switch, not a biological claim.

## Local perception

When seeking food, the herbivore may perceive only plants satisfying:

```text
plant.edible_biomass_kg > 0
distance(herbivore, plant) <= perception_radius_m
```

Use Euclidean distance in meters.

Do not inspect or target plants outside the radius.

### Target selection

Choose the visible edible plant minimizing:

```text
(distance_squared, plant_id)
```

Using squared distance avoids unnecessary square roots for comparison and provides deterministic tie-breaking.

Do not persist the target as memory between ticks. Recompute from current perception each tick.

## Feeding

If the chosen target is within:

```text
distance <= feeding_radius_m
```

the herbivore does not move that tick and may eat.

Potential bite:

```text
bite_kg = feeding_rate_kg_per_s * dt_seconds
```

Food needed to reach hunger 0:

```text
needed_kg = hunger * food_capacity_kg
```

Actual consumption:

```text
eaten_kg = min(
    bite_kg,
    plant.edible_biomass_kg,
    needed_kg,
)
```

Then:

```text
plant.edible_biomass_kg -= eaten_kg
hunger -= eaten_kg / food_capacity_kg
```

Clamp tiny floating residuals to the legal bounds when necessary.

Plant biomass lost through feeding is an explicit food-consumption sink in this simplified model. Do not add animal body-mass conservation yet.

## Movement toward food

If a visible target exists but is outside feeding radius:

- move directly toward its current position;
- maximum travel this tick = `speed_m_per_s * dt_seconds`;
- do not overshoot the point at which the animal reaches feeding radius if easy to avoid;
- position remains a new `Position2D`.

Because plants are in bounds and motion is directly toward one, food-seeking movement should naturally remain in bounds.

## Exploration

When no target is being sought:

- keep a persistent `heading_rad`;
- apply a small random turn each simulation tick from the **world-owned seeded RNG**;
- move at constant speed.

Approved turning rule:

```text
turn_delta =
    (2 * rng.random() - 1)
    * exploration_turn_rate_rad_per_s
    * dt_seconds
```

To avoid adding another per-animal model field, use a system-level parameter:

```text
exploration_turn_rate_rad_per_s = 0.8
```

This parameter belongs to the herbivore behavior system, not the renderer.

Then:

```text
heading = normalize(heading + turn_delta)
dx = cos(heading) * speed * dt
dy = sin(heading) * speed * dt
```

Draw order matters for replay: iterate herbivores in their stored world order and consume RNG exactly in that order.

## Wall behavior

V1 wall response is now defined because movement requires it.

Use axis reflection.

Conceptually:

- crossing left/right wall reflects X velocity component;
- crossing bottom/top wall reflects Y velocity component;
- final position remains inside the closed world bounds;
- reflect heading consistently with the reflected movement.

Implementation should support a step that may cross a wall without teleporting or resetting toward world center.

A compact reflection helper is preferred and should be unit-tested independently.

Do not add collision radius; treat the herbivore position as the movement point in V1.

## Herbivore behavior system

Preferred:

```python
class HerbivoreBehaviorSystem:
    def step(
        self,
        *,
        herbivores: Sequence[Herbivore],
        plants: Sequence[Plant],
        bounds: WorldBounds,
        rng: SeededRNG,
        dt_seconds: float,
    ) -> None:
        ...
```

The system may have the exploration turn-rate parameter.

Process herbivores sequentially in world order.

This means if two animals feed from the same plant during one tick, the earlier animal in deterministic world order sees the biomass first. This ordering bias is accepted for V1 and must be documented/tested rather than hidden.

Do not add scheduler infrastructure yet.

## Simulation order

One `Simulation.step()` becomes:

```text
1. PlantGrowthSystem.step(...)
2. HerbivoreBehaviorSystem.step(...)
3. clock.advance()
```

Thus plants first regrow over the interval, then herbivores perceive/consume/move, then the clock marks completion of the tick.

This order is explicit and deterministic.

## Deterministic initial herbivores

Provide a factory using caller-supplied `SeededRNG`.

Preferred:

```python
create_uniform_herbivores(...)
```

For each animal, consume RNG in this exact order:

1. x;
2. y;
3. heading.

Mapping:

```text
x = rng.random() * bounds.width_m
y = rng.random() * bounds.height_m
heading = rng.random() * 2π
```

IDs: 0..count-1.

Do not reseed internally.

The viewer scenario may use the same world RNG stream after plant placement, or an explicitly documented deterministic construction sequence. Do not create hidden unseeded RNGs.

## Default viewer demonstration

The executable should visibly show the feedback loop.

Recommended demo parameters:

```text
plants: existing 100

herbivores: 12
initial hunger: 0.60
speed: 15 m/s
perception radius: 150 m
feeding radius: 8 m
hunger rate: 0.003 /s
feeding rate: 0.05 kg/s
food capacity: 0.25 kg
seek threshold: 0.35
exploration turn rate: 0.8 rad/s
```

These are visualization/behavior demonstration parameters, not biological measurements.

Use the existing seed 42.

## Viewer

Render herbivores as simple primitive circles clearly distinct from plants.

The viewer may visually encode hunger, but only from core state and only as presentation.

Do not:

- move animals in renderer;
- choose targets in renderer;
- mutate hunger or biomass in renderer;
- use screen distance for perception.

Optionally show counts and aggregate plant biomass/hunger if trivial, but metrics are not required for acceptance.

## Tests

### Entity validation

Cover IDs, finite fields, legal hunger/threshold ranges and positive food capacity.

### Perception/targeting

Test:

- ignores depleted plants;
- ignores out-of-radius plants;
- picks nearest visible plant;
- ties by plant ID;
- no target when below hunger threshold.

### Hunger/feeding

Test:

- hunger increases by rate × dt;
- capped at 1;
- feeding removes plant biomass;
- feeding reduces hunger with correct conversion;
- consumption limited by bite rate;
- consumption limited by plant biomass;
- consumption limited by hunger need;
- no negative plant biomass/hunger.

### Movement

Test:

- moves toward target by correct distance;
- no FPS dependency;
- deterministic exploration with same seed;
- different representative seeds can diverge;
- wall reflections for each axis and a corner;
- final positions always inside bounds.

### Multi-animal ordering

Test deterministic sequential consumption from a shared plant.

### Replay

Construct two equal worlds with equal seed and verify multiple ticks produce equal:

- clock;
- plant biomass;
- animal positions;
- hunger;
- headings;
- RNG continuation where practical.

### Viewer

Test:

- default scenario has real core herbivores;
- render consumes core herbivore objects;
- resize has no core effects;
- no animal logic in adapter.

### Regression

Existing vegetation behavior, viewer tests and Windows executable build remain green.

## Acceptance criteria

1. Herbivores are core entities.
2. Local perception only.
3. Nearest visible edible plant selection is deterministic.
4. Feeding changes real plant biomass and hunger.
5. Exploration uses only project-owned seeded RNG.
6. Movement stays inside closed world bounds.
7. Wall response uses reflection.
8. No memory.
9. No social/group rule.
10. Same seed reproduces the same trajectory.
11. Pygame remains presentation-only.
12. Windows executable workflow remains green.
13. pytest, Ruff and mypy pass.

## Non-goals

- memory;
- learning;
- water;
- health/death;
- reproduction;
- predators;
- flocking;
- social interactions;
- animal collision/body radius;
- pathfinding;
- terrain;
- plant death;
- spatial indexing;
- optimization;
- ECS.

## STOP conditions

Return to the Primary Pilot if implementation requires changing:

- fixed timestep semantics;
- RNG ownership;
- plant growth rule;
- world coordinate convention;
- renderer/core boundary;
- approved system order;
- feeding conversion semantics;
- wall reflection rule;

or if implementation appears to need any non-goal above.

## Completion report

Codex reports:

1. files changed;
2. public herbivore API;
3. system execution order;
4. perception/feeding/movement behavior;
5. replay evidence;
6. test/check results;
7. Windows executable workflow status;
8. deviations;
9. PR link.
