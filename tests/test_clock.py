"""Tests for the fixed-timestep simulation clock."""

from __future__ import annotations

from math import inf, nan

import pytest

from simu_monde.core.clock import SimulationClock


def test_clock_starts_at_tick_zero_and_time_zero() -> None:
    clock = SimulationClock(dt_seconds=0.25)

    assert clock.tick_index == 0
    assert clock.time_seconds == 0.0


def test_clock_advance_increments_exactly_one_tick() -> None:
    clock = SimulationClock(dt_seconds=0.25)

    clock.advance()

    assert clock.tick_index == 1
    assert clock.time_seconds == 0.25


def test_clock_time_is_derived_after_multiple_advances() -> None:
    clock = SimulationClock(dt_seconds=0.125)

    for _ in range(8):
        clock.advance()

    assert clock.tick_index == 8
    assert clock.time_seconds == clock.tick_index * clock.dt_seconds


def test_clock_time_does_not_change_without_an_explicit_advance() -> None:
    clock = SimulationClock(dt_seconds=0.25)

    first_reading = clock.time_seconds
    second_reading = clock.time_seconds

    assert first_reading == second_reading == 0.0


@pytest.mark.parametrize("dt_seconds", [0.0, -0.1, nan, inf, -inf])
def test_clock_rejects_invalid_timestep(dt_seconds: float) -> None:
    with pytest.raises(ValueError):
        SimulationClock(dt_seconds=dt_seconds)


def test_clock_timestep_is_read_only() -> None:
    clock = SimulationClock(dt_seconds=0.25)

    with pytest.raises(AttributeError):
        clock.dt_seconds = 0.5  # type: ignore[misc]
