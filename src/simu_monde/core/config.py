"""Configuration for a deterministic simulation world."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _require_positive_finite(value: float, name: str) -> float:
    """Return ``value`` as a float when it is a positive, finite number."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive, finite number")

    try:
        valid = isfinite(value) and value > 0
    except TypeError as error:
        raise ValueError(f"{name} must be a positive, finite number") from error

    if not valid:
        raise ValueError(f"{name} must be a positive, finite number")
    return float(value)


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Immutable parameters required to initialize the world kernel.

    Spatial dimensions and timestep are measured in meters and seconds,
    respectively.
    """

    dt_seconds: float
    seed: int
    width_m: float = 1000.0
    height_m: float = 1000.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "dt_seconds",
            _require_positive_finite(self.dt_seconds, "dt_seconds"),
        )
        object.__setattr__(self, "width_m", _require_positive_finite(self.width_m, "width_m"))
        object.__setattr__(self, "height_m", _require_positive_finite(self.height_m, "height_m"))

        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer, not a boolean")
