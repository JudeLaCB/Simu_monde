"""Tests for the minimal headless simulation."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.herbivore import Herbivore, HerbivoreBehaviorSystem
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.simulation import Simulation
from simu_monde.core.vegetation import Plant, PlantGrowthSystem
from simu_monde.core.world import World


def make_plant(*, biomass: float = 0.5, growth_rate: float = 0.2) -> Plant:
    return Plant(
        plant_id=0,
        position=Position2D(1.0, 2.0),
        edible_biomass_kg=biomass,
        max_edible_biomass_kg=1.0,
        growth_rate_kg_per_s=growth_rate,
    )


def test_step_advances_exactly_one_tick() -> None:
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.25, seed=1)))

    simulation.step()

    assert simulation.world.clock.tick_index == 1
    assert simulation.world.clock.time_seconds == 0.25


def test_multiple_steps_advance_expected_tick_count() -> None:
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.25, seed=1)))

    for _ in range(6):
        simulation.step()

    assert simulation.world.clock.tick_index == 6
    assert simulation.world.clock.time_seconds == 6 * 0.25


def test_stepping_preserves_world_config_and_bounds() -> None:
    config = SimulationConfig(dt_seconds=0.25, seed=1, width_m=30.0, height_m=40.0)
    world = World(config)
    simulation = Simulation(world)
    initial_bounds = world.bounds

    simulation.step()

    assert world.config is config
    assert world.bounds is initial_bounds
    assert world.bounds.width_m == 30.0
    assert world.bounds.height_m == 40.0


def test_equal_configurations_replay_equal_rng_and_step_sequences() -> None:
    config_a = SimulationConfig(dt_seconds=0.125, seed=1234)
    config_b = SimulationConfig(dt_seconds=0.125, seed=1234)
    simulation_a = Simulation(World(config_a))
    simulation_b = Simulation(World(config_b))

    for _ in range(5):
        assert simulation_a.world.rng.random() == simulation_b.world.rng.random()
        simulation_a.step()
        simulation_b.step()

    assert simulation_a.world.clock.tick_index == simulation_b.world.clock.tick_index
    assert simulation_a.world.clock.time_seconds == simulation_b.world.clock.time_seconds


def test_one_step_grows_plant_by_rate_times_fixed_timestep() -> None:
    plant = make_plant()
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.25, seed=1), plants=(plant,)))

    simulation.step()

    assert plant.edible_biomass_kg == pytest.approx(0.55)
    assert simulation.world.clock.tick_index == 1


def test_multiple_steps_grow_plant_until_cap() -> None:
    plant = make_plant(biomass=0.8, growth_rate=0.3)
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.5, seed=1), plants=(plant,)))

    for _ in range(5):
        simulation.step()

    assert plant.edible_biomass_kg == 1.0
    assert simulation.world.clock.tick_index == 5


class ObservingPlantGrowthSystem(PlantGrowthSystem):
    def __init__(self, world: World) -> None:
        self._world = world
        self.tick_seen: int | None = None

    def step(self, plants: Sequence[Plant], dt_seconds: float) -> None:
        self.tick_seen = self._world.clock.tick_index
        super().step(plants, dt_seconds)


def test_simulation_grows_plants_before_advancing_clock() -> None:
    world = World(
        SimulationConfig(dt_seconds=0.25, seed=1),
        plants=(make_plant(),),
    )
    growth_system = ObservingPlantGrowthSystem(world)

    Simulation(world, plant_growth_system=growth_system).step()

    assert growth_system.tick_seen == 0
    assert world.clock.tick_index == 1


class RecordingPlantGrowthSystem(PlantGrowthSystem):
    def __init__(self, events: list[str]) -> None:
        self._events = events

    def step(self, plants: Sequence[Plant], dt_seconds: float) -> None:
        self._events.append("growth")
        super().step(plants, dt_seconds)


class RecordingHerbivoreBehaviorSystem(HerbivoreBehaviorSystem):
    def __init__(self, events: list[str]) -> None:
        super().__init__()
        self._events = events

    def step(
        self,
        *,
        herbivores: Sequence[Herbivore],
        plants: Sequence[Plant],
        bounds: WorldBounds,
        rng: SeededRNG,
        dt_seconds: float,
    ) -> None:
        self._events.append("behavior")
        assert plants[0].edible_biomass_kg == pytest.approx(0.55)
        assert rng is not None
        assert bounds is not None
        assert herbivores == ()


def test_simulation_order_is_growth_then_behavior_then_clock() -> None:
    events: list[str] = []
    world = World(
        SimulationConfig(dt_seconds=0.25, seed=1),
        plants=(make_plant(),),
    )
    simulation = Simulation(
        world,
        plant_growth_system=RecordingPlantGrowthSystem(events),
        herbivore_behavior_system=RecordingHerbivoreBehaviorSystem(events),
    )

    simulation.step()

    assert events == ["growth", "behavior"]
    assert world.clock.tick_index == 1
