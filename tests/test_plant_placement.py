"""Tests for deterministic uniform plant placement."""

from __future__ import annotations

import pytest

from simu_monde.core.geometry import WorldBounds
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.vegetation import Plant, create_uniform_plants


def create_plants(seed: int, count: int = 5) -> tuple[Plant, ...]:
    return create_uniform_plants(
        rng=SeededRNG(seed),
        bounds=WorldBounds(100.0, 50.0),
        count=count,
        initial_biomass_kg=0.5,
        max_biomass_kg=1.0,
        growth_rate_kg_per_s=0.2,
        age_s=0.0,
        lifespan_s=300.0,
    )


def test_zero_count_returns_empty_tuple() -> None:
    plants = create_plants(seed=1, count=0)

    assert plants == ()


def test_placement_assigns_ordered_ids_and_in_bounds_positions() -> None:
    bounds = WorldBounds(100.0, 50.0)
    plants = create_uniform_plants(
        rng=SeededRNG(12),
        bounds=bounds,
        count=20,
        initial_biomass_kg=0.5,
        max_biomass_kg=1.0,
        growth_rate_kg_per_s=0.2,
        age_s=0.0,
        lifespan_s=300.0,
    )

    assert [plant.plant_id for plant in plants] == list(range(20))
    assert all(bounds.contains(plant.position) for plant in plants)
    assert all(plant.position.x_m < bounds.width_m for plant in plants)
    assert all(plant.position.y_m < bounds.height_m for plant in plants)


def test_same_seed_replays_identical_positions() -> None:
    first = create_plants(seed=123)
    second = create_plants(seed=123)

    assert [plant.position for plant in first] == [plant.position for plant in second]


def test_representative_different_seeds_produce_different_positions() -> None:
    first = create_plants(seed=1)
    second = create_plants(seed=2)

    assert [plant.position for plant in first] != [plant.position for plant in second]


def test_placement_draws_x_then_y_from_caller_rng() -> None:
    rng = SeededRNG(123)
    replay_rng = SeededRNG(123)
    bounds = WorldBounds(100.0, 50.0)

    plants = create_uniform_plants(
        rng=rng,
        bounds=bounds,
        count=2,
        initial_biomass_kg=0.5,
        max_biomass_kg=1.0,
        growth_rate_kg_per_s=0.2,
        age_s=0.0,
        lifespan_s=300.0,
    )
    expected_positions = [
        (replay_rng.random() * bounds.width_m, replay_rng.random() * bounds.height_m)
        for _ in range(2)
    ]

    assert [(plant.position.x_m, plant.position.y_m) for plant in plants] == expected_positions
    assert rng.random() == replay_rng.random()


@pytest.mark.parametrize(
    ("count", "expected_error"),
    [(-1, ValueError), (True, TypeError), (1.5, TypeError)],
)
def test_placement_rejects_invalid_count(
    count: object,
    expected_error: type[Exception],
) -> None:
    with pytest.raises(expected_error):
        create_uniform_plants(
            rng=SeededRNG(1),
            bounds=WorldBounds(100.0, 50.0),
            count=count,  # type: ignore[arg-type]
            initial_biomass_kg=0.5,
            max_biomass_kg=1.0,
            growth_rate_kg_per_s=0.2,
            age_s=0.0,
            lifespan_s=300.0,
        )
