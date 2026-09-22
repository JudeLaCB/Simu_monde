"""Tests for continuous world geometry."""

from __future__ import annotations

from math import inf, nan

import pytest
from hypothesis import given
from hypothesis import strategies as st

from simu_monde.core.geometry import Position2D, WorldBounds


@pytest.fixture
def bounds() -> WorldBounds:
    return WorldBounds(width_m=10.0, height_m=20.0)


def test_position_permits_negative_mathematical_coordinates() -> None:
    position = Position2D(x_m=-1.0, y_m=-2.0)

    assert position == Position2D(x_m=-1.0, y_m=-2.0)


@pytest.mark.parametrize(
    ("x_m", "y_m"),
    [(0.0, 0.0), (10.0, 0.0), (0.0, 20.0), (10.0, 20.0)],
)
def test_bounds_contains_each_corner_of_closed_domain(
    bounds: WorldBounds, x_m: float, y_m: float
) -> None:
    assert bounds.contains(Position2D(x_m=x_m, y_m=y_m))


def test_bounds_contains_representative_interior_point(bounds: WorldBounds) -> None:
    assert bounds.contains(Position2D(x_m=4.5, y_m=12.0))


@pytest.mark.parametrize(
    ("x_m", "y_m"),
    [(-0.0001, 10.0), (10.0001, 10.0), (5.0, -0.0001), (5.0, 20.0001)],
)
def test_bounds_excludes_points_beyond_walls(bounds: WorldBounds, x_m: float, y_m: float) -> None:
    assert not bounds.contains(Position2D(x_m=x_m, y_m=y_m))


@pytest.mark.parametrize("coordinate", [nan, inf, -inf])
@pytest.mark.parametrize("axis", ["x_m", "y_m"])
def test_position_rejects_non_finite_coordinates(axis: str, coordinate: float) -> None:
    arguments = {"x_m": 1.0, "y_m": 2.0, axis: coordinate}

    with pytest.raises(ValueError):
        Position2D(**arguments)


@pytest.mark.parametrize("dimension", [0.0, -1.0, nan, inf, -inf])
@pytest.mark.parametrize("field", ["width_m", "height_m"])
def test_bounds_rejects_invalid_dimensions(field: str, dimension: float) -> None:
    arguments = {"width_m": 1.0, "height_m": 1.0, field: dimension}

    with pytest.raises(ValueError):
        WorldBounds(**arguments)


@given(
    width_m=st.floats(min_value=0.001, max_value=10_000.0, allow_nan=False, allow_infinity=False),
    height_m=st.floats(min_value=0.001, max_value=10_000.0, allow_nan=False, allow_infinity=False),
    x_fraction=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    y_fraction=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_bounds_contains_all_generated_points_in_closed_domain(
    width_m: float,
    height_m: float,
    x_fraction: float,
    y_fraction: float,
) -> None:
    bounds = WorldBounds(width_m=width_m, height_m=height_m)
    position = Position2D(x_m=width_m * x_fraction, y_m=height_m * y_fraction)

    assert bounds.contains(position)
