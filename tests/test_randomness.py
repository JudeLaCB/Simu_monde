"""Tests for project-owned deterministic randomness."""

from __future__ import annotations

import pytest

from simu_monde.core.randomness import SeededRNG


def test_same_seed_replays_same_random_sequence() -> None:
    first = SeededRNG(seed=1234)
    second = SeededRNG(seed=1234)

    assert [first.random() for _ in range(10)] == [second.random() for _ in range(10)]


def test_representative_different_seeds_produce_different_sequence() -> None:
    first = SeededRNG(seed=1)
    second = SeededRNG(seed=2)

    assert [first.random() for _ in range(10)] != [second.random() for _ in range(10)]


def test_random_values_stay_in_half_open_unit_interval() -> None:
    rng = SeededRNG(seed=1234)

    assert all(0.0 <= rng.random() < 1.0 for _ in range(100))


@pytest.mark.parametrize("seed", [True, False, 1.5, "1"])
def test_rng_rejects_non_integer_seed(seed: object) -> None:
    with pytest.raises(TypeError):
        SeededRNG(seed=seed)  # type: ignore[arg-type]
