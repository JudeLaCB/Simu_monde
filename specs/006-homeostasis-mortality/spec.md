# Phase 1G — PID-inspired Homeostasis, Ageing, Death and Carcasses

**Status:** APPROVED FOR IMPLEMENTATION  
**Risk:** HIGH-RISK  
**Issue:** #18

## Goal

Replace threshold-only hunger/thirst arbitration with a small PID-inspired homeostasis controller whose implicit objective is survival, then add ageing and death.

The phase must produce this loop:

```text
energy + hydration state
        ↓
homeostatic error
        ↓
PID-inspired urgency
        ↓
food / water / exploration
        ↓
metabolism + movement
        ↓
ageing / starvation
        ↓
death
        ↓
persistent carcass
```

No reproduction, predator, decomposition or nutrient field is implemented yet.

## Modeling principle

The controller does not receive a scripted command such as "go to water" or "go to food".

It computes competing internal urgency signals from physiological state. The behavior layer only acts on currently perceived resources.

This is a regulation model, not an attempt to claim a biologically exact nervous system.

## Herbivore energy state

Remove the abstract hunger state and hunger-rate threshold model.

Replace with:

```python
energy_j: float
max_energy_j: float
basal_power_w: float
movement_energy_j_per_m: float
food_energy_j_per_kg: float
```

Validation:

- `max_energy_j > 0`;
- `0 <= energy_j <= max_energy_j`;
- all rates/coefficient values finite and >= 0;
- `food_energy_j_per_kg > 0`.

Expose:

```python
@property
def energy_fraction(self) -> float:
    return energy_j / max_energy_j
```

Clamp only for floating-point safety.

## Existing water state

Keep:

- `body_water_kg`;
- `max_body_water_kg`;
- `water_loss_kg_per_s`;
- `drinking_rate_kg_per_s`;
- `drinking_radius_m`;
- `thirst`.

Remove the old `drink_thirst_threshold` behavior switch from decision semantics.

If retaining the field temporarily for migration would complicate the public API, remove it in this phase and update all factories/tests.

Zero body water does **not** cause death in Phase 1G.

## Ageing

Add to both `Plant` and `Herbivore`:

```python
age_s: float
lifespan_s: float
```

Validation:

- age finite >= 0;
- lifespan finite > 0;
- initial age may equal lifespan; it will die at the mortality stage.

Age advances exactly once per completed simulation tick by `dt_seconds`.

## PID-inspired homeostasis state

Preferred module:

`src/simu_monde/core/homeostasis.py`

Each herbivore owns persistent state:

```python
@dataclass(slots=True)
class HomeostasisState:
    food_integral_s: float = 0.0
    water_integral_s: float = 0.0
    previous_food_error: float | None = None
    previous_water_error: float | None = None
```

These values are part of replay state.

## Controller parameters

Preferred system:

```python
class HomeostasisController:
    def __init__(
        self,
        *,
        kp: float,
        ki_per_s: float,
        kd_s: float,
        target_energy_fraction: float,
        target_water_fraction: float,
        integral_limit_s: float,
        action_activation_urgency: float,
    ) -> None:
        ...
```

V1 uses the same PID gains for food and water to avoid premature tuning complexity.

Validation:

- gains finite >= 0;
- targets in [0, 1];
- integral limit finite > 0;
- activation urgency finite >= 0.

Recommended demo values:

```text
kp = 1.0
ki_per_s = 0.05
kd_s = 0.20

target_energy_fraction = 0.80
target_water_fraction = 0.80

integral_limit_s = 8.0
action_activation_urgency = 0.12
```

These are controller calibration values, not biological measurements.

## Homeostatic errors

At each herbivore update:

```text
food_error =
    target_energy_fraction
    - current_energy_fraction

water_error =
    target_water_fraction
    - current_body_water_fraction
```

where:

```text
current_body_water_fraction =
    body_water_kg / max_body_water_kg
```

Errors are signed.

Thus an animal above the target reserve can have a negative error.

## Integral update

For each need:

```text
integral =
    clamp(
        integral + error * dt_seconds,
        -integral_limit_s,
        +integral_limit_s
    )
```

This permits accumulated urgency to unwind after a reserve has been restored.

Do not integrate only positive error; that would create permanent windup.

## Derivative

For the first update where previous error is `None`:

```text
derivative = 0
```

Otherwise:

```text
derivative =
    (current_error - previous_error) / dt_seconds
```

Then store the current error as previous error.

## Urgency

For each need:

```text
urgency =
    max(
        0,
        kp * error
        + ki_per_s * integral
        + kd_s * derivative
    )
```

The urgency is a dimensionless internal control score used only to arbitrate actions.

It is not a probability.

## Resource perception

Perception remains strictly local.

### Food candidate

The existing nearest visible edible plant rule remains:

```text
plant biomass > 0
distance <= perception_radius
min(distance_squared, plant_id)
```

### Water candidate

The existing nearest visible non-empty water-source rule remains:

```text
source water > 0
distance <= perception_radius
min(distance_squared, water_source_id)
```

No resource outside the perception radius may influence the chosen action.

## Action arbitration

The behavior system computes food and water urgency first.

Then build only **feasible perceived actions**:

- food action is feasible only if an edible plant is currently visible;
- water action is feasible only if a non-empty water source is currently visible.

A need is considered active only when:

```text
urgency >= action_activation_urgency
```

Decision:

1. collect active feasible needs;
2. choose the need with greatest urgency;
3. exact urgency tie-break: **water before food**;
4. if no active feasible need exists, explore.

The water tie-break is an explicit deterministic V1 convention, not a biological claim.

Important consequence:

If water urgency is high but no water is perceived while food is perceived and food urgency is active, the animal may eat rather than blindly wander.

This replaces the previous hard-coded "thirst blocks food" behavior.

## Basal energy cost

At the beginning of each herbivore behavior update:

```text
basal_cost_j =
    basal_power_w * dt_seconds

energy_j =
    max(0, energy_j - basal_cost_j)
```

Then apply the existing body-water loss:

```text
animal body water -> atmosphere
```

If energy reaches zero at this point, the herbivore performs no action during this tick and is converted to a carcass by the mortality stage.

## Movement energy cost

Every actual movement has an energy cost:

```text
movement_cost_j =
    actual_distance_travelled_m
    * movement_energy_j_per_m
```

Deduct after movement:

```text
energy_j =
    max(0, energy_j - movement_cost_j)
```

This applies to:

- exploration;
- seeking food;
- seeking water.

The movement helper should return or make available the actual distance travelled so cost is based on actual movement, not intended movement.

Reflection at walls remains deterministic.

## Feeding and energy

Remove the old hunger-reduction conversion.

Potential bite:

```text
bite_kg =
    feeding_rate_kg_per_s * dt_seconds
```

Food required to fill the energy reserve:

```text
food_needed_kg =
    (max_energy_j - energy_j)
    / food_energy_j_per_kg
```

Actual eaten biomass:

```text
eaten_kg =
    min(
        bite_kg,
        plant.edible_biomass_kg,
        food_needed_kg
    )
```

Then:

```text
plant.edible_biomass_kg -= eaten_kg
energy_j += eaten_kg * food_energy_j_per_kg
```

Clamp for floating-point safety.

If energy is already full, no biomass is eaten.

No mass-conservation claim is added for food in Phase 1G.

The nutrient transfer associated with feeding is introduced in Phase 1H.

## Drinking

The current drinking transfer remains:

```text
surface source -> herbivore body water
```

limited by:

- drinking rate;
- source stock;
- body-water capacity.

The PID controller, rather than a fixed thirst threshold, decides whether drinking remains the selected action.

This intentionally permits hysteresis-like behavior through the integral term.

## Herbivore lifespan and starvation death

An herbivore dies when, at the mortality stage:

```text
energy_j <= 0
OR
age_s >= lifespan_s
```

Death causes:

```python
class DeathCause(Enum):
    STARVATION = "starvation"
    OLD_AGE = "old_age"
```

If both are true, use `STARVATION` as the deterministic V1 tie-break.

Do not add dehydration death yet.

## Plant lifespan

Plants continue to grow and may be eaten during the tick.

At the mortality stage:

```text
age_s += dt_seconds
if age_s >= lifespan_s:
    plant dies
```

Dead plants are removed from the living plant collection.

Phase 1G does not yet create plant detritus or recycle plant nutrients.

That begins in Phase 1H.

## Carcass

Preferred module:

`src/simu_monde/core/lifecycle.py`

```python
@dataclass(slots=True)
class Carcass:
    carcass_id: int
    source_herbivore_id: int
    position: Position2D
    death_cause: DeathCause
    water_kg: float
    recoverable_nutrient_kg: float
    age_s: float = 0.0
```

Validation:

- IDs integer, non-bool, >= 0;
- position is `Position2D`;
- water finite >= 0;
- recoverable nutrient finite >= 0;
- age finite >= 0.

Add to `Herbivore`:

```python
recoverable_nutrient_kg: float
```

In Phase 1G this stock is initialized and remains constant through life.

Feeding does not change it yet.

Phase 1H will connect nutrient transfers.

## Death transfer

When a herbivore dies:

```text
living herbivore
    ↓
removed from world.herbivores

body_water_kg
    ↓
carcass.water_kg

recoverable_nutrient_kg
    ↓
carcass.recoverable_nutrient_kg
```

The carcass is created at exactly the herbivore position.

The dead herbivore must not remain active or rendered as living.

## Carcass IDs

World owns a monotonic next-carcass ID.

Existing carcass IDs must be unique.

When creating a new carcass:

```text
carcass_id = next_carcass_id
next_carcass_id += 1
```

No RNG is used.

## World lifecycle mutation

Do not introduce an ECS or generic entity registry.

World may gain explicit lifecycle methods such as:

```python
replace_plants(...)
replace_herbivores(...)
add_carcasses(...)
```

or one narrowly-scoped lifecycle mutation method.

Requirements:

- public properties still expose tuples;
- IDs remain unique;
- all positions remain in bounds;
- lifecycle changes are deterministic;
- mutation API is explicit and tested.

World owns:

```text
plants
herbivores
carcasses
```

## Water conservation update

`World.total_water_kg` must now include:

```text
atmosphere
+ soil
+ surface sources
+ living herbivore body water
+ carcass water
```

Herbivore death is therefore a water transfer, not a water sink.

The existing per-tick `1e-8 kg` water invariant remains mandatory.

## Mortality system

Preferred:

```python
class MortalitySystem:
    def step(
        self,
        *,
        world: World,
        dt_seconds: float,
    ) -> None:
        ...
```

Responsibilities:

1. increment plant age;
2. increment living herbivore age;
3. identify old plants;
4. identify starved/old herbivores;
5. remove dead plants;
6. convert dead herbivores to carcasses.

Do not decompose carcasses.

## Global simulation order

The approved order becomes:

```text
1. record total water before tick
2. RainfallSystem
3. PlantGrowthSystem
4. HerbivoreBehaviorSystem
   - basal energy loss
   - body-water loss
   - homeostasis controller
   - perceive
   - arbitrate
   - eat / drink / move / explore
   - movement energy cost
5. MortalitySystem
   - increment ages
   - plant old-age death
   - herbivore starvation / old-age death
   - create carcasses
6. EvaporationSystem
7. verify water conservation
8. clock.advance()
```

No generic scheduler.

## Default demo parameters

These are chosen for observable behavior, not biological realism.

Keep existing world, vegetation and water placement/rates unless changed below.

### Plants

```text
initial age = 0 s
lifespan = 300 s
```

For the default deterministic factory, all plants may start at age 0 in Phase 1G.

### Herbivores

```text
initial energy = 3500 J
max energy = 5000 J
basal power = 4 J/s
movement cost = 1 J/m
food energy = 2500 J/kg

initial age = 0 s
lifespan = 600 s

recoverable nutrient = 0.02 kg
```

Existing movement/perception/feeding/water values remain unless incompatible with the removed hunger/thirst-threshold fields.

### Controller

Use the recommended gains defined above.

## Viewer

Render:

- living plants;
- living herbivores;
- water sources;
- carcasses as a distinct neutral primitive.

Do not render dead herbivores as living.

Add minimal read-only metrics:

```text
Living plants: N
Living herbivores: N
Carcasses: N
Average herbivore energy: X %
Average herbivore hydration: X %
```

Existing water metrics remain.

Viewer must never calculate mortality or urgency.

## Expected qualitative behavior

Do not test these as exact outcomes, but make them observable:

- animals should no longer leave a water source immediately because one threshold crossed;
- accumulated need may make an animal continue restoring a reserve;
- a rapidly worsening reserve gets extra urgency from the derivative term;
- an unavailable urgent resource does not prevent exploiting another perceived active resource;
- animals eventually die from starvation or age;
- carcasses remain where death occurred.

## Tests

### Homeostasis

Test:

- signed error above/below target;
- integral accumulation;
- integral unwinding;
- anti-windup clamp;
- first derivative = 0;
- derivative positive when reserve worsens;
- urgency clamped >= 0;
- deterministic water-before-food exact tie;
- action activation floor.

### Energy

Test:

- basal cost;
- movement cost uses actual travelled distance;
- energy floors at zero;
- feeding increases energy correctly;
- bite limited by rate/biomass/energy need;
- full-energy animal does not eat.

### Arbitration

Test:

- higher active visible food urgency selects food;
- higher active visible water urgency selects water;
- unavailable high-urgency need does not block another visible active need;
- no active visible need -> exploration;
- perception remains local.

### Ageing/mortality

Test:

- plant and herbivore age exactly once per tick;
- age threshold death;
- starvation death;
- starvation wins exact cause tie;
- dead entity does not act next tick;
- dead plant no longer grows/is eaten.

### Carcasses

Test:

- death creates one carcass at exact position;
- body water transfers exactly;
- recoverable nutrient transfers exactly;
- carcass IDs monotonically increase;
- carcass persists unchanged without decomposition.

### Water conservation

Test:

- herbivore death conserves water;
- repeated deaths conserve water;
- long run with mortality remains within `1e-8 kg`.

### Replay

Same seed + same initial state must replay equal:

- living plant IDs/state;
- living herbivore IDs/state;
- homeostasis integrals/previous errors;
- carcasses;
- water reservoirs;
- RNG continuation;
- clock.

### Viewer

Test:

- renderer reads real carcasses;
- population metrics are read-only;
- resizing/rendering does not mutate lifecycle or controller state.

### Regression

- rain/evaporation/water invariants remain green;
- wall reflection remains green;
- plant water-limited growth remains green;
- Windows executable build remains green.

## Acceptance criteria

1. Hunger scalar/threshold behavior is replaced by explicit energy.
2. Food and water compete via PID-inspired urgency.
3. Need integrals can unwind; no permanent one-sided windup.
4. Only locally perceived resources can become targets.
5. Energy pays basal and movement costs.
6. Feeding restores energy.
7. Plants age and die.
8. Herbivores age and die from starvation/old age.
9. Herbivore death creates persistent carcasses.
10. Dead entities no longer participate as living entities.
11. Water contained in a dying herbivore moves into the carcass.
12. Total modeled water remains conserved.
13. Same seed replays the same lifecycle history.
14. No decomposition/nutrient field yet.
15. No reproduction/predator/memory.
16. Pygame stays presentation-only.
17. pytest, Ruff, mypy and Windows build pass.

## STOP conditions

Stop and return to the Primary Pilot if implementation appears to require:

- decomposition;
- nutrient-field semantics;
- reproduction;
- predators;
- dehydration death;
- memory;
- generic scheduler;
- ECS/entity registry;
- changing water conservation tolerance or reservoir semantics;
- hidden randomness;
- rendering-owned ecology.

## Completion report

Codex reports:

1. files changed;
2. migration from hunger to energy;
3. controller API and exact urgency formula;
4. lifecycle API;
5. mortality causes;
6. carcass API;
7. updated water-total definition;
8. replay/conservation evidence;
9. tests/checks;
10. Windows artifact status;
11. deviations;
12. PR link.
