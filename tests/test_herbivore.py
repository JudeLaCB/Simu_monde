"""Tests for the minimal herbivore entity."""

from __future__ import annotations

from math import inf, nan, pi

import pytest

from simu_monde.core.geometry import Position2D
from simu_monde.core.herbivore import Herbivore


def make_herbivore(**overrides: object) -> Herbivore:
    arguments: dict[str, object] = {
        "herbivore_id": 0,
        "position": Position2D(1.0, 2.0),
        "hunger": 0.5,
        "heading_rad": 0.0,
        "speed_m_per_s": 2.0,
        "perception_radius_m": 10.0,
        "feeding_radius_m": 1.0,
        "hunger_rate_per_s": 0.1,
        "feeding_rate_kg_per_s": 0.2,
        "food_capacity_kg": 0.5,
        "seek_food_hunger_threshold": 0.4,
    }
    arguments.update(overrides)
    return Herbivore(**arguments)  # type: ignore[arg-type]


def test_entity_accepts_contract_boundaries_and_normalizes_heading() -> None:
    herbivore = make_herbivore(
        hunger=0.0,
        heading_rad=-pi / 2,
        speed_m_per_s=0.0,
        perception_radius_m=0.0,
        feeding_radius_m=0.0,
        hunger_rate_per_s=0.0,
        feeding_rate_kg_per_s=0.0,
        seek_food_hunger_threshold=1.0,
    )

    assert herbivore.hunger == 0.0
    assert herbivore.heading_rad == pytest.approx(3 * pi / 2)


@pytest.mark.parametrize("herbivore_id", [True, False, 1.5, "1"])
def test_entity_rejects_non_integer_id(herbivore_id: object) -> None:
    with pytest.raises(TypeError):
        make_herbivore(herbivore_id=herbivore_id)


def test_entity_rejects_negative_id_and_non_position() -> None:
    with pytest.raises(ValueError):
        make_herbivore(herbivore_id=-1)
    with pytest.raises(TypeError):
        make_herbivore(position=(1.0, 2.0))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("hunger", -0.1),
        ("hunger", 1.1),
        ("seek_food_hunger_threshold", -0.1),
        ("seek_food_hunger_threshold", 1.1),
        ("speed_m_per_s", -0.1),
        ("perception_radius_m", -0.1),
        ("feeding_radius_m", -0.1),
        ("hunger_rate_per_s", -0.1),
        ("feeding_rate_kg_per_s", -0.1),
        ("food_capacity_kg", 0.0),
        ("food_capacity_kg", -0.1),
    ],
)
def test_entity_rejects_out_of_range_values(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        make_herbivore(**{field: value})


@pytest.mark.parametrize("value", [nan, inf, -inf])
@pytest.mark.parametrize(
    "field",
    [
        "hunger",
        "heading_rad",
        "speed_m_per_s",
        "perception_radius_m",
        "feeding_radius_m",
        "hunger_rate_per_s",
        "feeding_rate_kg_per_s",
        "food_capacity_kg",
        "seek_food_hunger_threshold",
    ],
)
def test_entity_rejects_non_finite_values(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        make_herbivore(**{field: value})
