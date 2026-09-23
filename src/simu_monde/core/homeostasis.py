"""PID-inspired deterministic homeostasis controller."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _require_finite(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        valid = isfinite(value)
    except TypeError as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not valid:
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _require_non_negative(value: float, name: str) -> float:
    finite_value = _require_finite(value, name)
    if finite_value < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return finite_value


@dataclass(slots=True)
class HomeostasisState:
    """Persistent integral and previous-error state for both regulated needs."""

    food_integral_s: float = 0.0
    water_integral_s: float = 0.0
    previous_food_error: float | None = None
    previous_water_error: float | None = None

    def __post_init__(self) -> None:
        self.food_integral_s = _require_finite(self.food_integral_s, "food_integral_s")
        self.water_integral_s = _require_finite(self.water_integral_s, "water_integral_s")
        if self.previous_food_error is not None:
            self.previous_food_error = _require_finite(
                self.previous_food_error, "previous_food_error"
            )
        if self.previous_water_error is not None:
            self.previous_water_error = _require_finite(
                self.previous_water_error, "previous_water_error"
            )


@dataclass(frozen=True, slots=True)
class HomeostasisSignals:
    """Current signed errors and non-negative action urgencies."""

    food_error: float
    water_error: float
    food_urgency: float
    water_urgency: float


class HomeostasisController:
    """Update persistent PID-inspired state and return current need signals."""

    def __init__(
        self,
        *,
        kp: float,
        ki_per_s: float,
        kd_s: float,
        target_energy_fraction: float,
        target_water_fraction: float,
        integral_limit_s: float,
        action_activation_urgency: float,
    ) -> None:
        self._kp = _require_non_negative(kp, "kp")
        self._ki_per_s = _require_non_negative(ki_per_s, "ki_per_s")
        self._kd_s = _require_non_negative(kd_s, "kd_s")
        self._target_energy_fraction = _require_finite(
            target_energy_fraction, "target_energy_fraction"
        )
        self._target_water_fraction = _require_finite(
            target_water_fraction, "target_water_fraction"
        )
        if not 0.0 <= self._target_energy_fraction <= 1.0:
            raise ValueError("target_energy_fraction must be between 0 and 1")
        if not 0.0 <= self._target_water_fraction <= 1.0:
            raise ValueError("target_water_fraction must be between 0 and 1")
        self._integral_limit_s = _require_finite(integral_limit_s, "integral_limit_s")
        if self._integral_limit_s <= 0.0:
            raise ValueError("integral_limit_s must be positive")
        self._action_activation_urgency = _require_non_negative(
            action_activation_urgency, "action_activation_urgency"
        )

    @property
    def action_activation_urgency(self) -> float:
        """The inclusive urgency floor for activating a feasible need."""
        return self._action_activation_urgency

    def update(
        self,
        *,
        state: HomeostasisState,
        energy_fraction: float,
        water_fraction: float,
        dt_seconds: float,
    ) -> HomeostasisSignals:
        """Apply signed PID-inspired updates for food and water."""
        food_error = self._target_energy_fraction - energy_fraction
        water_error = self._target_water_fraction - water_fraction

        state.food_integral_s = self._clamp_integral(
            state.food_integral_s + food_error * dt_seconds
        )
        state.water_integral_s = self._clamp_integral(
            state.water_integral_s + water_error * dt_seconds
        )
        food_derivative = self._derivative(food_error, state.previous_food_error, dt_seconds)
        water_derivative = self._derivative(water_error, state.previous_water_error, dt_seconds)
        state.previous_food_error = food_error
        state.previous_water_error = water_error

        return HomeostasisSignals(
            food_error=food_error,
            water_error=water_error,
            food_urgency=self._urgency(food_error, state.food_integral_s, food_derivative),
            water_urgency=self._urgency(water_error, state.water_integral_s, water_derivative),
        )

    def _clamp_integral(self, integral_s: float) -> float:
        return min(self._integral_limit_s, max(-self._integral_limit_s, integral_s))

    @staticmethod
    def _derivative(error: float, previous_error: float | None, dt_seconds: float) -> float:
        if previous_error is None:
            return 0.0
        return (error - previous_error) / dt_seconds

    def _urgency(self, error: float, integral_s: float, derivative_per_s: float) -> float:
        return max(
            0.0,
            self._kp * error + self._ki_per_s * integral_s + self._kd_s * derivative_per_s,
        )


def create_default_homeostasis_controller() -> HomeostasisController:
    """Create the approved Phase 1G controller calibration."""
    return HomeostasisController(
        kp=1.0,
        ki_per_s=0.05,
        kd_s=0.20,
        target_energy_fraction=0.80,
        target_water_fraction=0.80,
        integral_limit_s=8.0,
        action_activation_urgency=0.12,
    )
