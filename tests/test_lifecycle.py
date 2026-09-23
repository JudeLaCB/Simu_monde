"""Tests for ageing, mortality, explicit world mutation, and carcasses."""

from __future__ import annotations

from math import inf, nan

import pytest

from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.lifecycle import Carcass, DeathCause, MortalitySystem
from simu_monde.core.simulation import Simulation
from simu_monde.core.vegetation import Plant
from simu_monde.core.water import WaterState
from simu_monde.core.world import World

DEFAULT_HERBIVORE_POSITION = Position2D(5.0, 5.0)


def make_plant(
    *,
    plant_id: int = 0,
    age_s: float = 0.0,
    lifespan_s: float = 10.0,
    biomass: float = 0.5,
    growth_rate: float = 0.0,
) -> Plant:
    return Plant(
        plant_id=plant_id,
        position=Position2D(1.0 + plant_id, 2.0),
        edible_biomass_kg=biomass,
        max_edible_biomass_kg=1.0,
        growth_rate_kg_per_s=growth_rate,
        age_s=age_s,
        lifespan_s=lifespan_s,
    )


def make_herbivore(
    *,
    herbivore_id: int = 0,
    position: Position2D = DEFAULT_HERBIVORE_POSITION,
    energy_j: float = 50.0,
    basal_power_w: float = 0.0,
    age_s: float = 0.0,
    lifespan_s: float = 10.0,
    body_water_kg: float = 0.7,
    nutrient_kg: float = 0.02,
) -> Herbivore:
    return Herbivore(
        herbivore_id=herbivore_id,
        position=position,
        heading_rad=0.0,
        speed_m_per_s=0.0,
        perception_radius_m=10.0,
        feeding_radius_m=1.0,
        feeding_rate_kg_per_s=0.1,
        body_water_kg=body_water_kg,
        max_body_water_kg=1.0,
        water_loss_kg_per_s=0.0,
        drinking_rate_kg_per_s=0.1,
        drinking_radius_m=1.0,
        energy_j=energy_j,
        max_energy_j=100.0,
        basal_power_w=basal_power_w,
        movement_energy_j_per_m=0.0,
        food_energy_j_per_kg=100.0,
        age_s=age_s,
        lifespan_s=lifespan_s,
        recoverable_nutrient_kg=nutrient_kg,
    )


def make_world(
    *,
    plants: tuple[Plant, ...] = (),
    herbivores: tuple[Herbivore, ...] = (),
    carcasses: tuple[Carcass, ...] = (),
) -> World:
    return World(
        SimulationConfig(dt_seconds=1.0, seed=1, width_m=20.0, height_m=20.0),
        plants=plants,
        herbivores=herbivores,
        water_state=WaterState(1.0, 0.0, ()),
        carcasses=carcasses,
    )


def test_mortality_stage_increments_living_ages_exactly_once() -> None:
    plant = make_plant()
    herbivore = make_herbivore()
    world = make_world(plants=(plant,), herbivores=(herbivore,))

    MortalitySystem().step(world=world, dt_seconds=0.25)

    assert plant.age_s == 0.25
    assert herbivore.age_s == 0.25
    assert world.plants == (plant,)
    assert world.herbivores == (herbivore,)


def test_age_threshold_removes_plant_and_creates_old_age_carcass() -> None:
    plant = make_plant(age_s=9.5, lifespan_s=10.0)
    herbivore = make_herbivore(age_s=9.5, lifespan_s=10.0)
    world = make_world(plants=(plant,), herbivores=(herbivore,))

    MortalitySystem().step(world=world, dt_seconds=0.5)

    assert world.plants == ()
    assert world.herbivores == ()
    assert len(world.carcasses) == 1
    assert world.carcasses[0].death_cause is DeathCause.OLD_AGE


def test_starvation_wins_when_starvation_and_old_age_coincide() -> None:
    herbivore = make_herbivore(energy_j=0.0, age_s=10.0, lifespan_s=10.0)
    world = make_world(herbivores=(herbivore,))

    MortalitySystem().step(world=world, dt_seconds=1.0)

    assert world.carcasses[0].death_cause is DeathCause.STARVATION


def test_death_transfers_exact_position_water_and_nutrient_to_carcass() -> None:
    position = Position2D(7.0, 8.0)
    herbivore = make_herbivore(
        position=position,
        energy_j=0.0,
        body_water_kg=0.6,
        nutrient_kg=0.03,
    )
    world = make_world(herbivores=(herbivore,))
    total_before = world.total_water_kg

    MortalitySystem().step(world=world, dt_seconds=1.0)

    carcass = world.carcasses[0]
    assert carcass.carcass_id == 0
    assert carcass.source_herbivore_id == herbivore.herbivore_id
    assert carcass.position == position
    assert carcass.water_kg == 0.6
    assert carcass.recoverable_nutrient_kg == 0.03
    assert herbivore.body_water_kg == 0.0
    assert herbivore.recoverable_nutrient_kg == 0.0
    assert world.total_water_kg == total_before


def test_carcass_ids_continue_after_existing_maximum_and_follow_world_order() -> None:
    existing = Carcass(
        carcass_id=5,
        source_herbivore_id=9,
        position=Position2D(1.0, 1.0),
        death_cause=DeathCause.OLD_AGE,
        water_kg=0.1,
        recoverable_nutrient_kg=0.01,
    )
    first = make_herbivore(herbivore_id=4, energy_j=0.0)
    second = make_herbivore(herbivore_id=2, energy_j=0.0)
    world = make_world(herbivores=(first, second), carcasses=(existing,))

    MortalitySystem().step(world=world, dt_seconds=1.0)

    assert [carcass.carcass_id for carcass in world.carcasses] == [5, 6, 7]
    assert [carcass.source_herbivore_id for carcass in world.carcasses] == [9, 4, 2]


def test_carcass_persists_unchanged_without_decomposition() -> None:
    carcass = Carcass(
        carcass_id=0,
        source_herbivore_id=0,
        position=Position2D(5.0, 5.0),
        death_cause=DeathCause.STARVATION,
        water_kg=0.7,
        recoverable_nutrient_kg=0.02,
    )
    world = make_world(carcasses=(carcass,))

    for _ in range(20):
        Simulation(world).step()

    assert world.carcasses == (carcass,)
    assert carcass.age_s == 0.0
    assert carcass.water_kg == 0.7
    assert carcass.recoverable_nutrient_kg == 0.02


def test_starved_herbivore_does_not_act_and_dead_plant_stays_out_next_tick() -> None:
    plant = make_plant(age_s=9.0, lifespan_s=10.0, biomass=0.5, growth_rate=0.2)
    herbivore = make_herbivore(
        position=plant.position,
        energy_j=1.0,
        basal_power_w=1.0,
    )
    world = make_world(plants=(plant,), herbivores=(herbivore,))
    simulation = Simulation(world)

    simulation.step()
    biomass_after_death_tick = plant.edible_biomass_kg
    simulation.step()

    assert world.herbivores == ()
    assert world.plants == ()
    assert biomass_after_death_tick == 0.5
    assert plant.edible_biomass_kg == biomass_after_death_tick


def test_repeated_deaths_preserve_total_water() -> None:
    herbivores = tuple(
        make_herbivore(herbivore_id=index, energy_j=0.0, body_water_kg=0.1 * index)
        for index in range(1, 6)
    )
    world = make_world(herbivores=herbivores)
    initial_total = world.total_water_kg

    Simulation(world).step()

    assert world.herbivores == ()
    assert len(world.carcasses) == 5
    assert world.total_water_kg == pytest.approx(initial_total, abs=1e-8)


def test_same_seed_replays_lifecycle_history_controller_state_and_rng() -> None:
    def build() -> Simulation:
        plants = (
            make_plant(plant_id=0, lifespan_s=2.0),
            make_plant(plant_id=1, lifespan_s=4.0),
        )
        herbivores = (
            make_herbivore(herbivore_id=0, lifespan_s=2.0),
            make_herbivore(herbivore_id=1, lifespan_s=4.0),
        )
        return Simulation(make_world(plants=plants, herbivores=herbivores))

    first = build()
    replay = build()

    for _ in range(5):
        first.step()
        replay.step()

    assert first.world.plants == replay.world.plants == ()
    assert first.world.herbivores == replay.world.herbivores == ()
    assert first.world.carcasses == replay.world.carcasses
    assert first.world.water == replay.world.water
    assert first.world.clock.tick_index == replay.world.clock.tick_index == 5
    assert first.world.rng.random() == replay.world.rng.random()


def test_long_run_with_staggered_mortality_stays_within_water_tolerance() -> None:
    herbivores = tuple(
        make_herbivore(
            herbivore_id=index,
            lifespan_s=float(index + 1),
            body_water_kg=0.1 * (index + 1),
        )
        for index in range(5)
    )
    world = make_world(herbivores=herbivores)
    simulation = Simulation(world)
    initial_total = world.total_water_kg

    for _ in range(100):
        simulation.step()
        assert world.total_water_kg == pytest.approx(initial_total, abs=1e-8)

    assert len(world.carcasses) == 5


@pytest.mark.parametrize("field", ["carcass_id", "source_herbivore_id"])
@pytest.mark.parametrize("identifier", [True, 1.5, -1])
def test_carcass_rejects_invalid_ids(field: str, identifier: object) -> None:
    arguments = {
        "carcass_id": 0,
        "source_herbivore_id": 0,
        "position": Position2D(1.0, 1.0),
        "death_cause": DeathCause.STARVATION,
        "water_kg": 0.1,
        "recoverable_nutrient_kg": 0.01,
    }
    arguments[field] = identifier
    with pytest.raises((TypeError, ValueError)):
        Carcass(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [-1.0, nan, inf, -inf])
@pytest.mark.parametrize("field", ["water_kg", "recoverable_nutrient_kg", "age_s"])
def test_carcass_rejects_invalid_numeric_stocks(field: str, value: float) -> None:
    arguments = {
        "carcass_id": 0,
        "source_herbivore_id": 0,
        "position": Position2D(1.0, 1.0),
        "death_cause": DeathCause.STARVATION,
        "water_kg": 0.1,
        "recoverable_nutrient_kg": 0.01,
        "age_s": 0.0,
    }
    arguments[field] = value
    with pytest.raises(ValueError):
        Carcass(**arguments)  # type: ignore[arg-type]
