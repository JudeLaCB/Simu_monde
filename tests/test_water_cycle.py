"""Integration and replay tests for the closed water cycle."""

from __future__ import annotations

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.simulation import Simulation
from simu_monde.core.vegetation import Plant, PlantGrowthSystem
from simu_monde.core.water import EvaporationSystem, RainfallSystem, WaterSource, WaterState
from simu_monde.core.world import World


def make_simulation(seed: int = 17) -> Simulation:
    plant = Plant(
        plant_id=0,
        position=Position2D(10.0, 10.0),
        edible_biomass_kg=0.5,
        max_edible_biomass_kg=2.0,
        growth_rate_kg_per_s=0.2,
    )
    herbivore = Herbivore(
        herbivore_id=0,
        position=Position2D(10.0, 10.0),
        hunger=0.8,
        heading_rad=0.0,
        speed_m_per_s=1.0,
        perception_radius_m=20.0,
        feeding_radius_m=1.0,
        hunger_rate_per_s=0.01,
        feeding_rate_kg_per_s=0.05,
        food_capacity_kg=0.5,
        seek_food_hunger_threshold=0.3,
        body_water_kg=0.4,
        max_body_water_kg=1.0,
        water_loss_kg_per_s=0.01,
        drinking_rate_kg_per_s=0.1,
        drinking_radius_m=1.0,
        drink_thirst_threshold=0.2,
    )
    source = WaterSource(0, Position2D(10.0, 10.0), 0.3)
    water = WaterState(5.0, 2.0, (source,))
    world = World(
        SimulationConfig(
            dt_seconds=0.1,
            seed=seed,
            width_m=20.0,
            height_m=20.0,
        ),
        plants=(plant,),
        herbivores=(herbivore,),
        water_state=water,
    )
    return Simulation(
        world,
        rainfall_system=RainfallSystem(0.03, 0.5),
        plant_growth_system=PlantGrowthSystem(0.2),
        evaporation_system=EvaporationSystem(0.01, 0.02),
    )


def snapshot(simulation: Simulation) -> tuple[object, ...]:
    world = simulation.world
    herbivore = world.herbivores[0]
    return (
        world.clock.tick_index,
        world.clock.time_seconds,
        tuple(plant.edible_biomass_kg for plant in world.plants),
        herbivore.position,
        herbivore.heading_rad,
        herbivore.hunger,
        herbivore.body_water_kg,
        herbivore.thirst,
        world.water.atmosphere_water_kg,
        world.water.soil_water_kg,
        tuple(source.water_kg for source in world.water.surface_sources),
    )


def test_one_tick_conserves_water_while_plant_grows_and_herbivore_drinks() -> None:
    simulation = make_simulation()
    initial_total = simulation.world.total_water_kg
    initial_biomass = simulation.world.plants[0].edible_biomass_kg
    initial_body_water = simulation.world.herbivores[0].body_water_kg

    simulation.step()

    assert simulation.world.total_water_kg == pytest.approx(initial_total, abs=1e-8)
    assert simulation.world.plants[0].edible_biomass_kg > initial_biomass
    assert simulation.world.herbivores[0].body_water_kg > initial_body_water


def test_hundreds_of_ticks_conserve_water_and_keep_reservoirs_non_negative() -> None:
    simulation = make_simulation()
    initial_total = simulation.world.total_water_kg

    for _ in range(500):
        simulation.step()
        world = simulation.world
        assert world.total_water_kg == pytest.approx(initial_total, abs=1e-8)
        assert world.water.atmosphere_water_kg >= 0.0
        assert world.water.soil_water_kg >= 0.0
        assert all(source.water_kg >= 0.0 for source in world.water.surface_sources)
        assert all(herbivore.body_water_kg >= 0.0 for herbivore in world.herbivores)


def test_equal_seed_replays_full_water_and_ecology_state_and_rng() -> None:
    first = make_simulation(seed=91)
    replay = make_simulation(seed=91)

    for _ in range(300):
        first.step()
        replay.step()

    assert snapshot(first) == snapshot(replay)
    assert first.world.rng.random() == replay.world.rng.random()


def test_drought_like_accessible_shortage_keeps_total_water() -> None:
    herbivore = Herbivore(
        herbivore_id=0,
        position=Position2D(5.0, 5.0),
        hunger=0.0,
        heading_rad=0.0,
        speed_m_per_s=0.0,
        perception_radius_m=10.0,
        feeding_radius_m=1.0,
        hunger_rate_per_s=0.0,
        feeding_rate_kg_per_s=0.0,
        food_capacity_kg=1.0,
        seek_food_hunger_threshold=1.0,
        body_water_kg=0.1,
        max_body_water_kg=1.0,
        water_loss_kg_per_s=0.1,
        drinking_rate_kg_per_s=1.0,
        drinking_radius_m=1.0,
        drink_thirst_threshold=0.0,
    )
    world = World(
        SimulationConfig(dt_seconds=1.0, seed=1, width_m=10.0, height_m=10.0),
        herbivores=(herbivore,),
        water_state=WaterState(0.0, 0.0, ()),
    )
    simulation = Simulation(world)
    initial_total = world.total_water_kg

    for _ in range(10):
        simulation.step()

    assert herbivore.body_water_kg == 0.0
    assert world.water.atmosphere_water_kg == pytest.approx(0.1)
    assert world.total_water_kg == pytest.approx(initial_total, abs=1e-8)
