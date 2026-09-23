"""Tests for world ownership of the vegetation collection."""

from __future__ import annotations

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.vegetation import Plant
from simu_monde.core.world import World


def make_plant(plant_id: int, position: Position2D) -> Plant:
    return Plant(
        plant_id=plant_id,
        position=position,
        edible_biomass_kg=0.5,
        max_edible_biomass_kg=1.0,
        growth_rate_kg_per_s=0.2,
    )


def make_herbivore(herbivore_id: int, position: Position2D) -> Herbivore:
    return Herbivore(
        herbivore_id=herbivore_id,
        position=position,
        hunger=0.5,
        heading_rad=0.0,
        speed_m_per_s=1.0,
        perception_radius_m=10.0,
        feeding_radius_m=1.0,
        hunger_rate_per_s=0.1,
        feeding_rate_kg_per_s=0.2,
        food_capacity_kg=0.5,
        seek_food_hunger_threshold=0.4,
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
