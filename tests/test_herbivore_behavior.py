"""Behavior, boundary, consumption, and replay tests for herbivores."""

from __future__ import annotations

from math import pi

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.herbivore import Herbivore, HerbivoreBehaviorSystem, reflect_travel
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.simulation import Simulation
from simu_monde.core.vegetation import Plant
from simu_monde.core.world import World

DEFAULT_POSITION = Position2D(10.0, 10.0)


def make_herbivore(
    *,
    herbivore_id: int = 0,
    position: Position2D = DEFAULT_POSITION,
    hunger: float = 0.6,
    heading_rad: float = 0.0,
    speed_m_per_s: float = 2.0,
    perception_radius_m: float = 20.0,
    feeding_radius_m: float = 1.0,
    hunger_rate_per_s: float = 0.0,
    feeding_rate_kg_per_s: float = 0.2,
    food_capacity_kg: float = 1.0,
    seek_food_hunger_threshold: float = 0.5,
) -> Herbivore:
    return Herbivore(
        herbivore_id=herbivore_id,
        position=position,
        hunger=hunger,
        heading_rad=heading_rad,
        speed_m_per_s=speed_m_per_s,
        perception_radius_m=perception_radius_m,
        feeding_radius_m=feeding_radius_m,
        hunger_rate_per_s=hunger_rate_per_s,
        feeding_rate_kg_per_s=feeding_rate_kg_per_s,
        food_capacity_kg=food_capacity_kg,
        seek_food_hunger_threshold=seek_food_hunger_threshold,
    )


def make_plant(
    plant_id: int,
    position: Position2D,
    biomass: float = 1.0,
    growth_rate: float = 0.0,
) -> Plant:
    return Plant(
        plant_id=plant_id,
        position=position,
        edible_biomass_kg=biomass,
        max_edible_biomass_kg=2.0,
        growth_rate_kg_per_s=growth_rate,
    )


def step(
    herbivores: tuple[Herbivore, ...],
    plants: tuple[Plant, ...] = (),
    *,
    seed: int = 1,
    dt_seconds: float = 1.0,
    turn_rate: float = 0.8,
) -> SeededRNG:
    rng = SeededRNG(seed)
    HerbivoreBehaviorSystem(turn_rate).step(
        herbivores=herbivores,
        plants=plants,
        bounds=WorldBounds(100.0, 100.0),
        rng=rng,
        dt_seconds=dt_seconds,
    )
    return rng


def test_perception_ignores_depleted_and_out_of_radius_plants() -> None:
    herbivore = make_herbivore()
    plants = (
        make_plant(0, Position2D(11.0, 10.0), biomass=0.0),
        make_plant(1, Position2D(40.0, 10.0)),
        make_plant(2, Position2D(10.0, 15.0)),
    )

    step((herbivore,), plants)

    assert herbivore.position == Position2D(10.0, 12.0)
    assert herbivore.heading_rad == pytest.approx(pi / 2)


def test_perception_selects_nearest_then_lowest_id_for_equal_distance() -> None:
    nearest = make_herbivore()
    step(
        (nearest,),
        (make_plant(5, Position2D(10.0, 16.0)), make_plant(9, Position2D(13.0, 10.0))),
    )
    tied = make_herbivore()
    step(
        (tied,),
        (make_plant(2, Position2D(10.0, 15.0)), make_plant(1, Position2D(15.0, 10.0))),
    )

    assert nearest.position == Position2D(12.0, 10.0)
    assert tied.position == Position2D(12.0, 10.0)


def test_hunger_is_increased_before_threshold_decision() -> None:
    herbivore = make_herbivore(hunger=0.49, hunger_rate_per_s=0.02)

    step((herbivore,), (make_plant(0, Position2D(15.0, 10.0)),))

    assert herbivore.hunger == pytest.approx(0.51)
    assert herbivore.position == Position2D(12.0, 10.0)


def test_hunger_accumulation_is_capped_at_one() -> None:
    herbivore = make_herbivore(
        hunger=0.95,
        hunger_rate_per_s=0.2,
        perception_radius_m=0.0,
        speed_m_per_s=0.0,
    )

    step((herbivore,))

    assert herbivore.hunger == 1.0


def test_below_threshold_explores_without_targeting_or_eating() -> None:
    herbivore = make_herbivore(hunger=0.49, speed_m_per_s=0.0)
    plant = make_plant(0, Position2D(10.0, 10.0))
    rng = step((herbivore,), (plant,))
    replay_rng = SeededRNG(1)
    replay_rng.random()

    assert plant.edible_biomass_kg == 1.0
    assert rng.random() == replay_rng.random()


@pytest.mark.parametrize(
    ("biomass", "hunger", "rate", "expected_eaten"),
    [
        (1.0, 0.8, 0.2, 0.2),
        (0.1, 0.8, 0.5, 0.1),
        (1.0, 0.1, 0.5, 0.1),
    ],
)
def test_feeding_is_limited_by_bite_plant_and_need(
    biomass: float,
    hunger: float,
    rate: float,
    expected_eaten: float,
) -> None:
    herbivore = make_herbivore(
        hunger=hunger,
        feeding_rate_kg_per_s=rate,
        seek_food_hunger_threshold=0.0,
    )
    plant = make_plant(0, Position2D(10.5, 10.0), biomass=biomass)

    step((herbivore,), (plant,))

    assert plant.edible_biomass_kg == pytest.approx(biomass - expected_eaten)
    assert herbivore.hunger == pytest.approx(hunger - expected_eaten)
    assert plant.edible_biomass_kg >= 0.0
    assert herbivore.hunger >= 0.0


def test_seeking_moves_directly_without_overshooting_feeding_radius() -> None:
    herbivore = make_herbivore(
        position=Position2D(0.0, 10.0), speed_m_per_s=20.0, feeding_radius_m=2.0
    )

    step((herbivore,), (make_plant(0, Position2D(10.0, 10.0)),))

    assert herbivore.position == Position2D(8.0, 10.0)
    assert herbivore.heading_rad == 0.0


def test_exploration_replays_for_same_seed_and_diverges_for_different_seed() -> None:
    first = make_herbivore(hunger=0.0, heading_rad=1.0)
    replay = make_herbivore(hunger=0.0, heading_rad=1.0)
    different = make_herbivore(hunger=0.0, heading_rad=1.0)

    step((first,), seed=7)
    step((replay,), seed=7)
    step((different,), seed=8)

    assert (first.position, first.heading_rad) == (replay.position, replay.heading_rad)
    assert (first.position, first.heading_rad) != (different.position, different.heading_rad)


@pytest.mark.parametrize(
    ("position", "heading", "expected_position", "expected_heading"),
    [
        (Position2D(9.0, 5.0), 0.0, Position2D(8.0, 5.0), pi),
        (Position2D(5.0, 9.0), pi / 2, Position2D(5.0, 8.0), 3 * pi / 2),
        (Position2D(9.0, 9.0), pi / 4, Position2D(8.0, 8.0), 5 * pi / 4),
    ],
)
def test_wall_crossings_reflect_position_and_heading(
    position: Position2D,
    heading: float,
    expected_position: Position2D,
    expected_heading: float,
) -> None:
    reflected_position, reflected_heading = reflect_travel(
        position=position,
        heading_rad=heading,
        distance_m=3.0 if heading in (0.0, pi / 2) else 3.0 * 2**0.5,
        bounds=WorldBounds(10.0, 10.0),
    )

    assert reflected_position.x_m == pytest.approx(expected_position.x_m)
    assert reflected_position.y_m == pytest.approx(expected_position.y_m)
    assert reflected_heading == pytest.approx(expected_heading)


def test_large_step_can_cross_multiple_walls_and_remains_in_bounds() -> None:
    position, heading = reflect_travel(
        position=Position2D(5.0, 5.0),
        heading_rad=0.0,
        distance_m=37.0,
        bounds=WorldBounds(10.0, 10.0),
    )

    assert position == Position2D(2.0, 5.0)
    assert heading == 0.0
    assert WorldBounds(10.0, 10.0).contains(position)


def test_world_order_defines_sequential_consumption_priority() -> None:
    first = make_herbivore(herbivore_id=5, feeding_rate_kg_per_s=0.1)
    second = make_herbivore(herbivore_id=1, feeding_rate_kg_per_s=0.1)
    plant = make_plant(0, Position2D(10.0, 10.0), biomass=0.15)

    step((first, second), (plant,))

    assert first.hunger == pytest.approx(0.5)
    assert second.hunger == pytest.approx(0.55)
    assert plant.edible_biomass_kg == pytest.approx(0.0)


def _make_replay_simulation(seed: int) -> Simulation:
    config = SimulationConfig(dt_seconds=0.25, seed=seed, width_m=20.0, height_m=20.0)
    plants = (make_plant(0, Position2D(15.0, 10.0), growth_rate=0.01),)
    herbivores = (
        make_herbivore(
            position=Position2D(2.0, 2.0),
            heading_rad=0.4,
            speed_m_per_s=3.0,
            perception_radius_m=2.0,
            hunger_rate_per_s=0.01,
        ),
    )
    return Simulation(World(config, plants=plants, herbivores=herbivores))


def test_full_simulation_replay_includes_state_clock_and_rng_continuation() -> None:
    first = _make_replay_simulation(77)
    replay = _make_replay_simulation(77)

    for _ in range(25):
        first.step()
        replay.step()

    first_herbivore = first.world.herbivores[0]
    replay_herbivore = replay.world.herbivores[0]
    assert first.world.clock.tick_index == replay.world.clock.tick_index == 25
    assert first.world.clock.time_seconds == replay.world.clock.time_seconds
    assert first.world.plants[0].edible_biomass_kg == replay.world.plants[0].edible_biomass_kg
    assert first_herbivore.position == replay_herbivore.position
    assert first_herbivore.hunger == replay_herbivore.hunger
    assert first_herbivore.heading_rad == replay_herbivore.heading_rad
    assert first.world.rng.random() == replay.world.rng.random()
