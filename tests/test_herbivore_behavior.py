"""Energy, arbitration, movement, and resource-action tests for herbivores."""

from __future__ import annotations

from math import pi

import pytest

from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.herbivore import Herbivore, HerbivoreBehaviorSystem, reflect_travel
from simu_monde.core.homeostasis import HomeostasisController
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.vegetation import Plant
from simu_monde.core.water import WaterSource, WaterState

DEFAULT_POSITION = Position2D(10.0, 10.0)


def make_herbivore(
    *,
    herbivore_id: int = 0,
    position: Position2D = DEFAULT_POSITION,
    heading_rad: float = 0.0,
    speed_m_per_s: float = 2.0,
    perception_radius_m: float = 20.0,
    feeding_radius_m: float = 1.0,
    feeding_rate_kg_per_s: float = 0.2,
    body_water_kg: float = 1.0,
    max_body_water_kg: float = 1.0,
    water_loss_kg_per_s: float = 0.0,
    drinking_rate_kg_per_s: float = 0.2,
    drinking_radius_m: float = 1.0,
    energy_j: float = 50.0,
    max_energy_j: float = 100.0,
    basal_power_w: float = 0.0,
    movement_energy_j_per_m: float = 0.0,
    food_energy_j_per_kg: float = 100.0,
    age_s: float = 0.0,
    lifespan_s: float = 100.0,
    recoverable_nutrient_kg: float = 0.02,
) -> Herbivore:
    return Herbivore(
        herbivore_id=herbivore_id,
        position=position,
        heading_rad=heading_rad,
        speed_m_per_s=speed_m_per_s,
        perception_radius_m=perception_radius_m,
        feeding_radius_m=feeding_radius_m,
        feeding_rate_kg_per_s=feeding_rate_kg_per_s,
        body_water_kg=body_water_kg,
        max_body_water_kg=max_body_water_kg,
        water_loss_kg_per_s=water_loss_kg_per_s,
        drinking_rate_kg_per_s=drinking_rate_kg_per_s,
        drinking_radius_m=drinking_radius_m,
        energy_j=energy_j,
        max_energy_j=max_energy_j,
        basal_power_w=basal_power_w,
        movement_energy_j_per_m=movement_energy_j_per_m,
        food_energy_j_per_kg=food_energy_j_per_kg,
        age_s=age_s,
        lifespan_s=lifespan_s,
        recoverable_nutrient_kg=recoverable_nutrient_kg,
    )


def make_plant(
    plant_id: int,
    position: Position2D,
    biomass: float = 1.0,
) -> Plant:
    return Plant(
        plant_id=plant_id,
        position=position,
        edible_biomass_kg=biomass,
        max_edible_biomass_kg=2.0,
        growth_rate_kg_per_s=0.0,
        age_s=0.0,
        lifespan_s=100.0,
    )


def make_source(
    source_id: int,
    position: Position2D,
    water_kg: float = 1.0,
) -> WaterSource:
    return WaterSource(source_id, position, water_kg)


def make_controller(
    *,
    target_energy: float = 0.8,
    target_water: float = 0.8,
    activation: float = 0.1,
) -> HomeostasisController:
    return HomeostasisController(
        kp=1.0,
        ki_per_s=0.0,
        kd_s=0.0,
        target_energy_fraction=target_energy,
        target_water_fraction=target_water,
        integral_limit_s=8.0,
        action_activation_urgency=activation,
    )


def step(
    herbivores: tuple[Herbivore, ...],
    plants: tuple[Plant, ...] = (),
    *,
    water: WaterState | None = None,
    seed: int = 1,
    dt_seconds: float = 1.0,
    controller: HomeostasisController | None = None,
    turn_rate: float = 0.8,
) -> SeededRNG:
    rng = SeededRNG(seed)
    water_state = water if water is not None else WaterState(0.0, 0.0, ())
    HerbivoreBehaviorSystem(
        exploration_turn_rate_rad_per_s=turn_rate,
        controller=controller if controller is not None else make_controller(),
    ).step(
        herbivores=herbivores,
        plants=plants,
        water=water_state,
        bounds=WorldBounds(100.0, 100.0),
        rng=rng,
        dt_seconds=dt_seconds,
    )
    return rng


def test_basal_energy_and_body_water_loss_happen_before_action() -> None:
    herbivore = make_herbivore(
        energy_j=10.0,
        basal_power_w=2.0,
        body_water_kg=0.5,
        water_loss_kg_per_s=0.1,
        speed_m_per_s=0.0,
    )
    water = WaterState(1.0, 0.0, ())

    step((herbivore,), water=water, dt_seconds=2.0)

    assert herbivore.energy_j == 6.0
    assert herbivore.body_water_kg == pytest.approx(0.3)
    assert water.atmosphere_water_kg == pytest.approx(1.2)


def test_basal_energy_floors_at_zero_and_zero_energy_performs_no_action() -> None:
    herbivore = make_herbivore(
        energy_j=1.0,
        basal_power_w=2.0,
        speed_m_per_s=5.0,
    )
    rng = step((herbivore,))
    replay_rng = SeededRNG(1)

    assert herbivore.energy_j == 0.0
    assert herbivore.position == DEFAULT_POSITION
    assert rng.random() == replay_rng.random()


def test_higher_visible_food_urgency_selects_food() -> None:
    herbivore = make_herbivore(energy_j=20.0, body_water_kg=0.7)
    plant = make_plant(0, Position2D(15.0, 10.0))
    source = make_source(0, Position2D(10.0, 15.0))

    step((herbivore,), (plant,), water=WaterState(0.0, 0.0, (source,)))

    assert herbivore.position == Position2D(12.0, 10.0)


def test_higher_visible_water_urgency_selects_water() -> None:
    herbivore = make_herbivore(energy_j=70.0, body_water_kg=0.2)
    plant = make_plant(0, Position2D(15.0, 10.0))
    source = make_source(0, Position2D(10.0, 15.0))

    step((herbivore,), (plant,), water=WaterState(0.0, 0.0, (source,)))

    assert herbivore.position == Position2D(10.0, 12.0)


def test_exact_urgency_tie_selects_water() -> None:
    herbivore = make_herbivore(energy_j=50.0, body_water_kg=0.5)
    plant = make_plant(0, Position2D(15.0, 10.0))
    source = make_source(0, Position2D(10.0, 15.0))

    step((herbivore,), (plant,), water=WaterState(0.0, 0.0, (source,)))

    assert herbivore.position == Position2D(10.0, 12.0)


def test_unavailable_high_water_urgency_does_not_block_visible_food() -> None:
    herbivore = make_herbivore(
        energy_j=50.0,
        body_water_kg=0.0,
        perception_radius_m=10.0,
    )
    plant = make_plant(0, Position2D(15.0, 10.0))
    distant_source = make_source(0, Position2D(30.0, 10.0))

    step((herbivore,), (plant,), water=WaterState(0.0, 0.0, (distant_source,)))

    assert herbivore.position == Position2D(12.0, 10.0)


def test_no_active_visible_need_explores_and_consumes_one_rng_draw() -> None:
    herbivore = make_herbivore(
        energy_j=100.0,
        body_water_kg=1.0,
        speed_m_per_s=0.0,
    )
    rng = step((herbivore,))
    replay = SeededRNG(1)
    replay.random()

    assert rng.random() == replay.random()


def test_visible_need_below_activation_floor_does_not_select_resource() -> None:
    herbivore = make_herbivore(
        energy_j=75.0,
        body_water_kg=1.0,
        heading_rad=pi / 2,
    )
    plant = make_plant(0, Position2D(15.0, 10.0))

    step(
        (herbivore,),
        (plant,),
        controller=make_controller(target_energy=0.8, activation=0.1),
        turn_rate=0.0,
    )

    assert herbivore.position.x_m == pytest.approx(10.0)
    assert herbivore.position.y_m == pytest.approx(12.0)


def test_food_perception_ignores_depleted_and_out_of_radius_and_ties_by_id() -> None:
    herbivore = make_herbivore(energy_j=20.0, perception_radius_m=10.0)
    plants = (
        make_plant(0, Position2D(11.0, 10.0), biomass=0.0),
        make_plant(3, Position2D(30.0, 10.0)),
        make_plant(2, Position2D(10.0, 15.0)),
        make_plant(1, Position2D(15.0, 10.0)),
    )

    step((herbivore,), plants)

    assert herbivore.position == Position2D(12.0, 10.0)


def test_water_perception_ignores_empty_and_out_of_radius_and_ties_by_id() -> None:
    herbivore = make_herbivore(energy_j=100.0, body_water_kg=0.0, perception_radius_m=10.0)
    sources = (
        make_source(0, Position2D(11.0, 10.0), water_kg=0.0),
        make_source(3, Position2D(30.0, 10.0)),
        make_source(2, Position2D(10.0, 15.0)),
        make_source(1, Position2D(15.0, 10.0)),
    )

    step((herbivore,), water=WaterState(0.0, 0.0, sources))

    assert herbivore.position == Position2D(12.0, 10.0)


@pytest.mark.parametrize(
    ("biomass", "energy", "rate", "expected_eaten"),
    [
        (1.0, 20.0, 0.2, 0.2),
        (0.1, 20.0, 0.5, 0.1),
        (1.0, 90.0, 0.5, 0.1),
    ],
)
def test_feeding_is_limited_by_bite_biomass_and_energy_need(
    biomass: float,
    energy: float,
    rate: float,
    expected_eaten: float,
) -> None:
    herbivore = make_herbivore(
        energy_j=energy,
        feeding_rate_kg_per_s=rate,
        food_energy_j_per_kg=100.0,
    )
    plant = make_plant(0, Position2D(10.5, 10.0), biomass)

    step(
        (herbivore,),
        (plant,),
        controller=make_controller(target_energy=1.0, activation=0.0),
    )

    assert plant.edible_biomass_kg == pytest.approx(biomass - expected_eaten)
    assert herbivore.energy_j == pytest.approx(energy + expected_eaten * 100.0)


def test_full_energy_animal_does_not_eat() -> None:
    herbivore = make_herbivore(energy_j=100.0, body_water_kg=1.0, speed_m_per_s=0.0)
    plant = make_plant(0, Position2D(10.5, 10.0))

    step(
        (herbivore,),
        (plant,),
        controller=make_controller(target_energy=1.0, activation=0.0),
    )

    assert plant.edible_biomass_kg == 1.0
    assert herbivore.energy_j == 100.0


def test_seeking_movement_cost_uses_actual_distance_to_feeding_radius() -> None:
    herbivore = make_herbivore(
        position=Position2D(0.0, 10.0),
        energy_j=50.0,
        speed_m_per_s=20.0,
        feeding_radius_m=2.0,
        movement_energy_j_per_m=3.0,
    )

    step((herbivore,), (make_plant(0, Position2D(10.0, 10.0)),))

    assert herbivore.position == Position2D(8.0, 10.0)
    assert herbivore.energy_j == pytest.approx(26.0)


def test_exploration_movement_cost_uses_reflected_path_length() -> None:
    herbivore = make_herbivore(
        position=Position2D(99.0, 50.0),
        heading_rad=0.0,
        energy_j=50.0,
        speed_m_per_s=3.0,
        movement_energy_j_per_m=4.0,
    )

    step((herbivore,), turn_rate=0.0)

    assert herbivore.position == Position2D(98.0, 50.0)
    assert herbivore.heading_rad == pytest.approx(pi)
    assert herbivore.energy_j == 38.0


def test_movement_energy_cost_floors_energy_at_zero() -> None:
    herbivore = make_herbivore(
        energy_j=5.0,
        speed_m_per_s=2.0,
        movement_energy_j_per_m=10.0,
    )

    step((herbivore,), (make_plant(0, Position2D(15.0, 10.0)),))

    assert herbivore.position == Position2D(12.0, 10.0)
    assert herbivore.energy_j == 0.0


@pytest.mark.parametrize(
    ("source_water", "body_water", "rate", "expected_drink"),
    [(1.0, 0.0, 0.2, 0.2), (0.1, 0.0, 0.5, 0.1), (1.0, 0.9, 0.5, 0.1)],
)
def test_drinking_is_limited_and_conserves_water(
    source_water: float,
    body_water: float,
    rate: float,
    expected_drink: float,
) -> None:
    herbivore = make_herbivore(
        energy_j=100.0,
        body_water_kg=body_water,
        drinking_rate_kg_per_s=rate,
    )
    source = make_source(0, Position2D(10.5, 10.0), source_water)
    water = WaterState(0.0, 0.0, (source,))
    total_before = body_water + source_water

    step(
        (herbivore,),
        water=water,
        controller=make_controller(target_water=1.0, activation=0.0),
    )

    assert source.water_kg == pytest.approx(source_water - expected_drink)
    assert herbivore.body_water_kg == pytest.approx(body_water + expected_drink)
    assert source.water_kg + herbivore.body_water_kg == pytest.approx(total_before)


def test_exploration_replays_for_same_seed_and_diverges_for_different_seed() -> None:
    first = make_herbivore(energy_j=100.0, body_water_kg=1.0, heading_rad=1.0)
    replay = make_herbivore(energy_j=100.0, body_water_kg=1.0, heading_rad=1.0)
    different = make_herbivore(energy_j=100.0, body_water_kg=1.0, heading_rad=1.0)

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
