"""Tests for world ownership of the vegetation collection."""

from __future__ import annotations

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.lifecycle import Carcass, DeathCause
from simu_monde.core.vegetation import Plant
from simu_monde.core.water import WaterSource, WaterState
from simu_monde.core.world import World


def make_plant(plant_id: int, position: Position2D) -> Plant:
    return Plant(
        plant_id=plant_id,
        position=position,
        edible_biomass_kg=0.5,
        max_edible_biomass_kg=1.0,
        growth_rate_kg_per_s=0.2,
        age_s=0.0,
        lifespan_s=100.0,
    )


def make_herbivore(herbivore_id: int, position: Position2D) -> Herbivore:
    return Herbivore(
        herbivore_id=herbivore_id,
        position=position,
        heading_rad=0.0,
        speed_m_per_s=1.0,
        perception_radius_m=10.0,
        feeding_radius_m=1.0,
        feeding_rate_kg_per_s=0.2,
        body_water_kg=1.0,
        max_body_water_kg=1.0,
        water_loss_kg_per_s=0.0,
        drinking_rate_kg_per_s=0.2,
        drinking_radius_m=1.0,
        energy_j=50.0,
        max_energy_j=100.0,
        basal_power_w=1.0,
        movement_energy_j_per_m=2.0,
        food_energy_j_per_kg=100.0,
        age_s=0.0,
        lifespan_s=100.0,
        recoverable_nutrient_kg=0.02,
    )


def test_world_accepts_plants_and_preserves_input_order() -> None:
    first = make_plant(3, Position2D(1.0, 2.0))
    second = make_plant(1, Position2D(3.0, 4.0))
    source = [first, second]

    world = World(SimulationConfig(dt_seconds=0.1, seed=1), plants=source)
    source.clear()

    assert world.plants == (first, second)
    assert isinstance(world.plants, tuple)


def test_world_without_plants_preserves_original_behavior() -> None:
    config = SimulationConfig(dt_seconds=0.1, seed=1, width_m=30.0, height_m=40.0)
    world = World(config)

    assert world.config is config
    assert world.bounds.width_m == 30.0
    assert world.bounds.height_m == 40.0
    assert world.plants == ()
    assert world.herbivores == ()
    assert world.carcasses == ()
    assert world.water == WaterState(0.0, 0.0, ())
    assert world.total_water_kg == 0.0


def test_world_rejects_duplicate_plant_ids() -> None:
    plants = (
        make_plant(1, Position2D(1.0, 2.0)),
        make_plant(1, Position2D(3.0, 4.0)),
    )

    with pytest.raises(ValueError, match="duplicate plant_id"):
        World(SimulationConfig(dt_seconds=0.1, seed=1), plants=plants)


def test_world_rejects_out_of_bounds_plant_position() -> None:
    plant = make_plant(1, Position2D(-0.1, 2.0))

    with pytest.raises(ValueError, match="outside world bounds"):
        World(SimulationConfig(dt_seconds=0.1, seed=1), plants=(plant,))


@pytest.mark.parametrize(
    "position",
    [Position2D(0.0, 0.0), Position2D(1000.0, 1000.0)],
)
def test_world_accepts_plants_on_exact_boundary(position: Position2D) -> None:
    plant = make_plant(1, position)

    world = World(SimulationConfig(dt_seconds=0.1, seed=1), plants=(plant,))

    assert world.plants == (plant,)


def test_world_accepts_herbivores_and_preserves_input_order() -> None:
    first = make_herbivore(3, Position2D(1.0, 2.0))
    second = make_herbivore(1, Position2D(3.0, 4.0))
    source = [first, second]

    world = World(SimulationConfig(dt_seconds=0.1, seed=1), herbivores=source)
    source.clear()

    assert world.herbivores == (first, second)
    assert isinstance(world.herbivores, tuple)


def test_world_rejects_duplicate_or_out_of_bounds_herbivores() -> None:
    duplicate = (
        make_herbivore(1, Position2D(1.0, 2.0)),
        make_herbivore(1, Position2D(3.0, 4.0)),
    )
    with pytest.raises(ValueError, match="duplicate herbivore_id"):
        World(SimulationConfig(dt_seconds=0.1, seed=1), herbivores=duplicate)

    with pytest.raises(ValueError, match="outside world bounds"):
        World(
            SimulationConfig(dt_seconds=0.1, seed=1),
            herbivores=(make_herbivore(1, Position2D(-0.1, 2.0)),),
        )


@pytest.mark.parametrize(
    "position",
    [Position2D(0.0, 0.0), Position2D(1000.0, 1000.0)],
)
def test_world_accepts_herbivores_on_exact_boundary(position: Position2D) -> None:
    herbivore = make_herbivore(1, position)

    world = World(SimulationConfig(dt_seconds=0.1, seed=1), herbivores=(herbivore,))

    assert world.herbivores == (herbivore,)


def test_world_owns_water_state_and_total_includes_herbivore_body_water() -> None:
    source = WaterSource(0, Position2D(5.0, 6.0), 3.0)
    water = WaterState(1.0, 2.0, (source,))
    herbivore = make_herbivore(0, Position2D(1.0, 2.0))

    world = World(
        SimulationConfig(dt_seconds=0.1, seed=1),
        herbivores=(herbivore,),
        water_state=water,
    )

    assert world.water is water
    assert world.total_water_kg == 7.0


def test_world_rejects_out_of_bounds_water_source() -> None:
    water = WaterState(
        1.0,
        2.0,
        (WaterSource(0, Position2D(-0.1, 2.0), 3.0),),
    )

    with pytest.raises(ValueError, match="water source 0 position is outside world bounds"):
        World(SimulationConfig(dt_seconds=0.1, seed=1), water_state=water)


def make_carcass(carcass_id: int, position: Position2D) -> Carcass:
    return Carcass(
        carcass_id=carcass_id,
        source_herbivore_id=carcass_id,
        position=position,
        death_cause=DeathCause.OLD_AGE,
        water_kg=0.2,
        recoverable_nutrient_kg=0.01,
    )


def test_world_validates_existing_carcass_ids_and_bounds() -> None:
    with pytest.raises(ValueError, match="duplicate carcass_id"):
        World(
            SimulationConfig(dt_seconds=0.1, seed=1),
            carcasses=(
                make_carcass(1, Position2D(1.0, 1.0)),
                make_carcass(1, Position2D(2.0, 2.0)),
            ),
        )

    with pytest.raises(ValueError, match="carcass 1 position is outside world bounds"):
        World(
            SimulationConfig(dt_seconds=0.1, seed=1),
            carcasses=(make_carcass(1, Position2D(-1.0, 1.0)),),
        )
