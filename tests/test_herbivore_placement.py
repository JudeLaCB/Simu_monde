"""Tests for deterministic uniform herbivore placement."""

from __future__ import annotations

import pytest

from simu_monde.core.geometry import WorldBounds
from simu_monde.core.herbivore import Herbivore, create_uniform_herbivores
from simu_monde.core.randomness import SeededRNG


def create_herbivores(seed: int, count: int = 5) -> tuple[Herbivore, ...]:
    return create_uniform_herbivores(
        rng=SeededRNG(seed),
        bounds=WorldBounds(100.0, 50.0),
        count=count,
        hunger=0.5,
        speed_m_per_s=2.0,
        perception_radius_m=10.0,
        feeding_radius_m=1.0,
        hunger_rate_per_s=0.1,
        feeding_rate_kg_per_s=0.2,
        food_capacity_kg=0.5,
        seek_food_hunger_threshold=0.4,
        body_water_kg=1.0,
        max_body_water_kg=1.0,
        water_loss_kg_per_s=0.0,
        drinking_rate_kg_per_s=0.2,
        drinking_radius_m=1.0,
        drink_thirst_threshold=0.5,
    )


def test_placement_assigns_ordered_ids_and_in_bounds_positions() -> None:
    herbivores = create_herbivores(seed=12, count=20)
    bounds = WorldBounds(100.0, 50.0)

    assert [herbivore.herbivore_id for herbivore in herbivores] == list(range(20))
    assert all(bounds.contains(herbivore.position) for herbivore in herbivores)


def test_same_seed_replays_and_different_seed_diverges() -> None:
    first = create_herbivores(seed=1)
    replay = create_herbivores(seed=1)
    different = create_herbivores(seed=2)

    assert [(item.position, item.heading_rad) for item in first] == [
        (item.position, item.heading_rad) for item in replay
    ]
    assert [(item.position, item.heading_rad) for item in first] != [
        (item.position, item.heading_rad) for item in different
    ]


def test_placement_draws_x_then_y_then_heading_from_caller_rng() -> None:
    rng = SeededRNG(123)
    replay_rng = SeededRNG(123)
    herbivores = create_uniform_herbivores(
        rng=rng,
        bounds=WorldBounds(100.0, 50.0),
        count=2,
        hunger=0.5,
        speed_m_per_s=2.0,
        perception_radius_m=10.0,
        feeding_radius_m=1.0,
        hunger_rate_per_s=0.1,
        feeding_rate_kg_per_s=0.2,
        food_capacity_kg=0.5,
        seek_food_hunger_threshold=0.4,
        body_water_kg=1.0,
        max_body_water_kg=1.0,
        water_loss_kg_per_s=0.0,
        drinking_rate_kg_per_s=0.2,
        drinking_radius_m=1.0,
        drink_thirst_threshold=0.5,
    )
    expected = [
        (replay_rng.random() * 100.0, replay_rng.random() * 50.0, replay_rng.random())
        for _ in range(2)
    ]

    assert [
        (item.position.x_m, item.position.y_m, item.heading_rad / (2.0 * 3.141592653589793))
        for item in herbivores
    ] == expected
    assert rng.random() == replay_rng.random()


@pytest.mark.parametrize(
    ("count", "error"),
    [(-1, ValueError), (True, TypeError), (1.5, TypeError)],
)
def test_placement_rejects_invalid_count(count: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        create_herbivores(seed=1, count=count)  # type: ignore[arg-type]


def test_zero_count_returns_empty_tuple() -> None:
    assert create_herbivores(seed=1, count=0) == ()
