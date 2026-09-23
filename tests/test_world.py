"""Tests for world ownership of the vegetation collection."""

from __future__ import annotations

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D
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
