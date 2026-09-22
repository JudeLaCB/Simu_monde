"""Tests for simulation configuration validation."""

from __future__ import annotations

from math import inf, nan

import pytest

from simu_monde.core.config import SimulationConfig


def test_config_uses_default_world_dimensions() -> None:
    config = SimulationConfig(dt_seconds=0.25, seed=7)

    assert config.width_m == 1000.0
    assert config.height_m == 1000.0


def test_config_accepts_custom_dimensions_and_positive_finite_timestep() -> None:
    config = SimulationConfig(dt_seconds=0.125, seed=7, width_m=1500.0, height_m=750.0)

    assert config.dt_seconds == 0.125
    assert config.width_m == 1500.0
    assert config.height_m == 750.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("width_m", 0.0),
        ("width_m", -1.0),
        ("width_m", nan),
        ("width_m", inf),
        ("width_m", -inf),
        ("height_m", 0.0),
        ("height_m", -1.0),
        ("height_m", nan),
        ("height_m", inf),
        ("height_m", -inf),
        ("dt_seconds", 0.0),
        ("dt_seconds", -0.1),
        ("dt_seconds", nan),
        ("dt_seconds", inf),
        ("dt_seconds", -inf),
    ],
)
def test_config_rejects_invalid_numeric_values(field: str, value: float) -> None:
    arguments: dict[str, float | int] = {"dt_seconds": 0.5, "seed": 1}
    arguments[field] = value

    with pytest.raises(ValueError):
        SimulationConfig(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("seed", [True, False, 1.5, "1"])
def test_config_rejects_non_integer_seed(seed: object) -> None:
    with pytest.raises(TypeError):
        SimulationConfig(dt_seconds=0.5, seed=seed)  # type: ignore[arg-type]
