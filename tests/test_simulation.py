"""Tests for the minimal headless simulation."""

from __future__ import annotations

from simu_monde.core.config import SimulationConfig
from simu_monde.core.simulation import Simulation
from simu_monde.core.world import World


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
