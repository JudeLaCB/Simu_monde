# Phase 1A — Deterministic 2D World Kernel

**Status:** APPROVED FOR IMPLEMENTATION  
**Risk:** STANDARD  
**Issue:** #3

## Goal

Create the smallest executable and testable kernel of Simu_monde.

After this slice, the repository must be able to represent a configurable continuous 2D world, advance deterministic simulation time, and produce reproducible pseudo-random values.

No ecology exists yet.

## Approved semantics

### Space

- 2D continuous world.
- Coordinates are expressed in meters.
- Default dimensions are 1000 m × 1000 m.
- Dimensions are configurable.
- Initial domain is closed:

```text
0 <= x <= width_m
0 <= y <= height_m
```

- A point on a wall is inside the world.
- A point beyond a wall is outside.
- Borders are conceptually walls, but movement response is explicitly deferred.

### Time

- Simulation uses a fixed timestep.
- Wall-clock time never advances the simulation.
- Simulation time is derived from integer tick count:

```text
time_seconds = tick_index * dt_seconds
```

This avoids accumulating time by repeatedly adding floating-point `dt`.

### Randomness

- Simulation randomness is owned by the core.
- The first implementation may wrap Python `random.Random`.
- Same seed and same sequence of RNG calls must reproduce the same values.
- Domain code must not use module-global random functions.

## Intended module layout

```text
src/simu_monde/core/
├── __init__.py
├── config.py
├── geometry.py
├── clock.py
├── randomness.py
├── world.py
└── simulation.py
```

Do not add a generic framework, ECS, event bus, plugin layer or dependency injection container.

## Public API contract

### `SimulationConfig`

Location: `core/config.py`

Preferred shape:

```python
@dataclass(frozen=True, slots=True)
class SimulationConfig:
    dt_seconds: float
    seed: int
    width_m: float = 1000.0
    height_m: float = 1000.0
```

Validation:

- `width_m > 0`;
- `height_m > 0`;
- `dt_seconds > 0`;
- all three float values must be finite;
- `seed` must be an integer;
- booleans must not be silently accepted as seeds.

Raise `ValueError` for invalid numeric configuration values and `TypeError` for an invalid seed type.

No environmental or biological parameters belong here yet.

### `Position2D`

Location: `core/geometry.py`

Preferred shape:

```python
@dataclass(frozen=True, slots=True)
class Position2D:
    x_m: float
    y_m: float
```

Rules:

- both coordinates must be finite;
- negative coordinates are allowed as a mathematical position object, because `Position2D` itself does not define world membership;
- world membership is the responsibility of `WorldBounds`.

Invalid non-finite coordinates raise `ValueError`.

### `WorldBounds`

Location: `core/geometry.py`

Preferred shape:

```python
@dataclass(frozen=True, slots=True)
class WorldBounds:
    width_m: float
    height_m: float

    def contains(self, position: Position2D) -> bool: ...
```

Rules:

```text
0 <= x_m <= width_m
0 <= y_m <= height_m
```

Construction validates positive finite dimensions using the same semantics as `SimulationConfig`.

No clamp, bounce, wrap, penalty or collision-resolution method is authorized in this slice.

### `SimulationClock`

Location: `core/clock.py`

Preferred public shape:

```python
class SimulationClock:
    def __init__(self, dt_seconds: float) -> None: ...
    @property
    def tick_index(self) -> int: ...
    @property
    def time_seconds(self) -> float: ...
    def advance(self) -> None: ...
```

Rules:

- starts at tick 0;
- `time_seconds == tick_index * dt_seconds`;
- `advance()` advances exactly one tick;
- no wall-clock dependency;
- `dt_seconds` is read-only after construction.

Do not expose arbitrary tick mutation in this slice.

### `SeededRNG`

Location: `core/randomness.py`

Preferred minimal public shape:

```python
class SeededRNG:
    def __init__(self, seed: int) -> None: ...
    def random(self) -> float: ...
```

Implementation may delegate to a private `random.Random(seed)`.

Do not add distributions or APIs that are not yet needed. Future methods can be added when an actual model requires them.

### `World`

Location: `core/world.py`

Preferred shape:

```python
class World:
    def __init__(self, config: SimulationConfig) -> None: ...
    @property
    def config(self) -> SimulationConfig: ...
    @property
    def bounds(self) -> WorldBounds: ...
    @property
    def clock(self) -> SimulationClock: ...
    @property
    def rng(self) -> SeededRNG: ...
```

`World` owns one bounds object, one clock and one RNG derived from the config.

No entity collection, water, plants, animals or memory is authorized yet.

### `Simulation`

Location: `core/simulation.py`

Preferred shape:

```python
class Simulation:
    def __init__(self, world: World) -> None: ...
    @property
    def world(self) -> World: ...
    def step(self) -> None: ...
```

For Phase 1A, `step()` does exactly one observable state transition:

```text
world.clock.advance()
```

That deliberately tiny behavior proves the tick boundary that later systems will plug into.

Do not build a scheduler yet.

## Initialization flow

```text
SimulationConfig
      ↓
    World
  ┌───┼────┐
Bounds Clock RNG
      ↓
 Simulation
      ↓
    step()
      ↓
tick_index + 1
```

## Validation and exceptions

Keep validation local and deterministic.

Required invalid cases:

- zero/negative width;
- zero/negative height;
- zero/negative timestep;
- NaN;
- positive or negative infinity;
- non-integer seed;
- boolean seed;
- non-finite Position2D coordinate.

Do not create a project-wide custom exception hierarchy yet.

## Determinism contract

The following must hold:

```python
config_a == config_b

sim_a = Simulation(World(config_a))
sim_b = Simulation(World(config_b))

# same steps and same RNG call order
# => same tick/time and same RNG outputs
```

Phase 1A does not promise deterministic equivalence across different Python implementations or future major algorithm migrations. It promises reproducibility inside the supported runtime contract.

## Test matrix

Create focused tests, not one monolithic test file.

Suggested files:

```text
tests/
├── test_config.py
├── test_geometry.py
├── test_clock.py
├── test_randomness.py
└── test_simulation.py
```

### Config tests

- defaults are 1000 × 1000;
- custom dimensions accepted;
- positive finite timestep accepted;
- invalid dimensions rejected;
- invalid timestep rejected;
- seed type validation.

### Geometry tests

- origin is contained;
- exact four wall/corner boundaries are contained;
- representative interior point contained;
- values just below 0 are outside;
- values just above width/height are outside;
- non-finite Position2D rejected.

Use Hypothesis where it improves coverage, especially for the containment property. Do not use property tests merely to add ceremony.

### Clock tests

- starts at tick 0 / time 0;
- one advance -> tick 1;
- N advances -> tick N and time N × dt;
- no wall-clock calls are used.

### RNG tests

- same seed -> same sequence;
- different representative seeds -> different sampled sequence;
- values from `random()` satisfy `0 <= x < 1`.

Do not assert Python's exact hard-coded numeric sequence unless necessary; assert replay equivalence between instances.

### Simulation tests

- `step()` advances exactly one tick;
- multiple steps advance exactly N ticks;
- world config/bounds remain unchanged by stepping;
- two simulations with same config and same RNG-call/step sequence remain observationally equivalent.

## Architecture protections

The implementation must not import:

- pygame;
- Godot bindings;
- Panda3D;
- physics engines;
- NumPy solely for these trivial primitives;
- any renderer.

Standard library + existing dev dependencies are sufficient.

## Non-goals

- water;
- ecology;
- entities;
- movement;
- boundary response;
- perception;
- memory;
- decision making;
- environmental grids;
- persistence;
- rendering;
- scheduler;
- events;
- optimization.

## STOP conditions

Stop and return to the Primary Pilot if implementation appears to require:

- a wall collision policy;
- entity size/radius;
- coordinate wrapping;
- environmental cell/grid semantics;
- resource semantics;
- an event/scheduler architecture;
- a new runtime dependency;
- any behavior intended to represent intelligence, memory or ecology.

## Completion evidence

Codex completion report should contain only:

1. files changed;
2. public API implemented;
3. tests/checks run and outcomes;
4. any deviation from this spec;
5. PR link.
