"""Continuous two-dimensional world geometry."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _require_finite(value: float, name: str) -> float:
    """Return ``value`` as a float when it is finite."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")

    try:
        valid = isfinite(value)
    except TypeError as error:
        raise ValueError(f"{name} must be a finite number") from error

    if not valid:
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _require_positive_finite(value: float, name: str) -> float:
    """Return ``value`` as a float when it is positive and finite."""
    finite_value = _require_finite(value, name)
    if finite_value <= 0:
        raise ValueError(f"{name} must be a positive, finite number")
    return finite_value


@dataclass(frozen=True, slots=True)
class Position2D:
    """A finite mathematical position in meters.

    Positions may be outside a world. ``WorldBounds`` determines membership.
    """

    x_m: float
    y_m: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "x_m", _require_finite(self.x_m, "x_m"))
        object.__setattr__(self, "y_m", _require_finite(self.y_m, "y_m"))


@dataclass(frozen=True, slots=True)
class WorldBounds:
    """Closed rectangular world bounds measured in meters."""

    width_m: float
    height_m: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "width_m", _require_positive_finite(self.width_m, "width_m"))
        object.__setattr__(self, "height_m", _require_positive_finite(self.height_m, "height_m"))

    def contains(self, position: Position2D) -> bool:
        """Return whether ``position`` belongs to the closed world domain."""
        return 0.0 <= position.x_m <= self.width_m and 0.0 <= position.y_m <= self.height_m
