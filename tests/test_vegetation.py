"""Tests for the minimal vegetation domain model and growth rule."""

from __future__ import annotations

from math import inf, nan

import pytest

from simu_monde.core.geometry import Position2D
from simu_monde.core.vegetation import Plant, PlantGrowthSystem
from simu_monde.core.water import WaterState


def make_plant(
    *,
    plant_id: int = 0,
    edible_biomass_kg: float = 0.5,
    max_edible_biomass_kg: float = 1.0,
    growth_rate_kg_per_s: float = 0.2,
) -> Plant:
    return Plant(
        plant_id=plant_id,
        position=Position2D(1.0, 2.0),
        edible_biomass_kg=edible_biomass_kg,
        max_edible_biomass_kg=max_edible_biomass_kg,
        growth_rate_kg_per_s=growth_rate_kg_per_s,
    )


def make_water(soil_water_kg: float) -> WaterState:
    return WaterState(
        atmosphere_water_kg=1.0,
        soil_water_kg=soil_water_kg,
        surface_sources=(),
    )


@pytest.mark.parametrize("biomass", [0.0, 1.0])
def test_plant_accepts_zero_and_maximum_biomass(biomass: float) -> None:
    plant = make_plant(edible_biomass_kg=biomass)

    assert plant.edible_biomass_kg == biomass


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("edible_biomass_kg", -0.1),
        ("edible_biomass_kg", 1.1),
        ("max_edible_biomass_kg", 0.0),
        ("max_edible_biomass_kg", -1.0),
        ("growth_rate_kg_per_s", -0.1),
        ("edible_biomass_kg", nan),
        ("edible_biomass_kg", inf),
        ("edible_biomass_kg", -inf),
        ("max_edible_biomass_kg", nan),
        ("max_edible_biomass_kg", inf),
        ("max_edible_biomass_kg", -inf),
        ("growth_rate_kg_per_s", nan),
        ("growth_rate_kg_per_s", inf),
        ("growth_rate_kg_per_s", -inf),
    ],
)
def test_plant_rejects_invalid_numeric_values(field: str, value: float) -> None:
    arguments: dict[str, float] = {
        "edible_biomass_kg": 0.5,
        "max_edible_biomass_kg": 1.0,
        "growth_rate_kg_per_s": 0.2,
    }
    arguments[field] = value

    with pytest.raises(ValueError):
        make_plant(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("plant_id", [True, False, 1.5, "1"])
def test_plant_rejects_non_integer_id(plant_id: object) -> None:
    with pytest.raises(TypeError):
        Plant(
            plant_id=plant_id,  # type: ignore[arg-type]
            position=Position2D(1.0, 2.0),
            edible_biomass_kg=0.5,
            max_edible_biomass_kg=1.0,
            growth_rate_kg_per_s=0.2,
        )


def test_plant_rejects_negative_id() -> None:
    with pytest.raises(ValueError):
        make_plant(plant_id=-1)


def test_growth_is_linear_below_cap() -> None:
    plant = make_plant(edible_biomass_kg=0.5, growth_rate_kg_per_s=0.2)

    water = make_water(1.0)
    PlantGrowthSystem().step((plant,), water, dt_seconds=0.5)

    assert plant.edible_biomass_kg == pytest.approx(0.6)
    assert water.soil_water_kg == pytest.approx(0.98)
    assert water.atmosphere_water_kg == pytest.approx(1.02)


def test_growth_is_capped_at_maximum() -> None:
    plant = make_plant(edible_biomass_kg=0.95, growth_rate_kg_per_s=0.2)

    water = make_water(1.0)
    PlantGrowthSystem().step((plant,), water, dt_seconds=1.0)

    assert plant.edible_biomass_kg == 1.0
    assert water.soil_water_kg == pytest.approx(0.99)
    assert water.atmosphere_water_kg == pytest.approx(1.01)


@pytest.mark.parametrize(
    ("biomass", "growth_rate"),
    [(0.5, 0.0), (1.0, 0.2)],
)
def test_zero_growth_or_full_plant_stays_unchanged(biomass: float, growth_rate: float) -> None:
    plant = make_plant(edible_biomass_kg=biomass, growth_rate_kg_per_s=growth_rate)

    water = make_water(1.0)
    PlantGrowthSystem().step((plant,), water, dt_seconds=1.0)

    assert plant.edible_biomass_kg == biomass
    assert water.soil_water_kg == 1.0
    assert water.atmosphere_water_kg == 1.0


def test_growth_is_proportional_when_soil_water_is_insufficient() -> None:
    plant = make_plant(edible_biomass_kg=0.5, growth_rate_kg_per_s=1.0)
    water = make_water(0.04)

    PlantGrowthSystem(water_kg_per_biomass_kg=0.2).step((plant,), water, dt_seconds=1.0)

    assert plant.edible_biomass_kg == pytest.approx(0.7)
    assert water.soil_water_kg == 0.0
    assert water.atmosphere_water_kg == pytest.approx(1.04)


def test_zero_soil_water_prevents_growth() -> None:
    plant = make_plant(edible_biomass_kg=0.5, growth_rate_kg_per_s=1.0)
    water = make_water(0.0)

    PlantGrowthSystem().step((plant,), water, dt_seconds=1.0)

    assert plant.edible_biomass_kg == 0.5
    assert water.atmosphere_water_kg == 1.0


@pytest.mark.parametrize("coefficient", [0.0, -1.0, nan, inf])
def test_growth_system_rejects_invalid_water_coefficient(coefficient: float) -> None:
    with pytest.raises(ValueError):
        PlantGrowthSystem(water_kg_per_biomass_kg=coefficient)
