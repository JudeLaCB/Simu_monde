"""Tests for the energy-based herbivore entity."""

from __future__ import annotations

from math import inf, nan, pi

import pytest

from simu_monde.core.geometry import Position2D
from simu_monde.core.herbivore import Herbivore


def make_herbivore(**overrides: object) -> Herbivore:
    arguments: dict[str, object] = {
        "herbivore_id": 0,
        "position": Position2D(1.0, 2.0),
        "heading_rad": 0.0,
        "speed_m_per_s": 2.0,
        "perception_radius_m": 10.0,
        "feeding_radius_m": 1.0,
        "feeding_rate_kg_per_s": 0.2,
        "body_water_kg": 1.0,
        "max_body_water_kg": 1.0,
        "water_loss_kg_per_s": 0.0,
        "drinking_rate_kg_per_s": 0.2,
        "drinking_radius_m": 1.0,
        "energy_j": 50.0,
        "max_energy_j": 100.0,
        "basal_power_w": 1.0,
        "movement_energy_j_per_m": 2.0,
        "food_energy_j_per_kg": 100.0,
        "age_s": 0.0,
        "lifespan_s": 100.0,
        "recoverable_nutrient_kg": 0.02,
    }
    arguments.update(overrides)
    return Herbivore(**arguments)  # type: ignore[arg-type]


def test_entity_accepts_contract_boundaries_and_normalizes_heading() -> None:
    herbivore = make_herbivore(
        heading_rad=-pi / 2,
        speed_m_per_s=0.0,
        perception_radius_m=0.0,
        feeding_radius_m=0.0,
        feeding_rate_kg_per_s=0.0,
        energy_j=0.0,
        body_water_kg=0.0,
        basal_power_w=0.0,
        movement_energy_j_per_m=0.0,
        water_loss_kg_per_s=0.0,
        drinking_rate_kg_per_s=0.0,
        drinking_radius_m=0.0,
        recoverable_nutrient_kg=0.0,
    )

    assert herbivore.heading_rad == pytest.approx(3 * pi / 2)
    assert herbivore.energy_fraction == 0.0
    assert herbivore.thirst == 1.0


@pytest.mark.parametrize("herbivore_id", [True, False, 1.5, "1"])
def test_entity_rejects_non_integer_id(herbivore_id: object) -> None:
    with pytest.raises(TypeError):
        make_herbivore(herbivore_id=herbivore_id)


def test_entity_rejects_negative_id_non_position_and_invalid_homeostasis() -> None:
    with pytest.raises(ValueError):
        make_herbivore(herbivore_id=-1)
    with pytest.raises(TypeError):
        make_herbivore(position=(1.0, 2.0))
    with pytest.raises(TypeError):
        make_herbivore(homeostasis=object())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("speed_m_per_s", -0.1),
        ("perception_radius_m", -0.1),
        ("feeding_radius_m", -0.1),
        ("feeding_rate_kg_per_s", -0.1),
        ("body_water_kg", -0.1),
        ("body_water_kg", 1.1),
        ("max_body_water_kg", 0.0),
        ("water_loss_kg_per_s", -0.1),
        ("drinking_rate_kg_per_s", -0.1),
        ("drinking_radius_m", -0.1),
        ("energy_j", -0.1),
        ("energy_j", 100.1),
        ("max_energy_j", 0.0),
        ("basal_power_w", -0.1),
        ("movement_energy_j_per_m", -0.1),
        ("food_energy_j_per_kg", 0.0),
        ("age_s", -0.1),
        ("lifespan_s", 0.0),
        ("recoverable_nutrient_kg", -0.1),
    ],
)
def test_entity_rejects_out_of_range_values(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        make_herbivore(**{field: value})


@pytest.mark.parametrize("value", [nan, inf, -inf])
@pytest.mark.parametrize(
    "field",
    [
        "heading_rad",
        "speed_m_per_s",
        "perception_radius_m",
        "feeding_radius_m",
        "feeding_rate_kg_per_s",
        "body_water_kg",
        "max_body_water_kg",
        "water_loss_kg_per_s",
        "drinking_rate_kg_per_s",
        "drinking_radius_m",
        "energy_j",
        "max_energy_j",
        "basal_power_w",
        "movement_energy_j_per_m",
        "food_energy_j_per_kg",
        "age_s",
        "lifespan_s",
        "recoverable_nutrient_kg",
    ],
)
def test_entity_rejects_non_finite_values(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        make_herbivore(**{field: value})


def test_energy_and_thirst_fractions_are_computed_from_reserves() -> None:
    herbivore = make_herbivore(
        energy_j=25.0,
        max_energy_j=100.0,
        body_water_kg=0.25,
        max_body_water_kg=1.0,
    )

    assert herbivore.energy_fraction == 0.25
    assert herbivore.thirst == 0.75
