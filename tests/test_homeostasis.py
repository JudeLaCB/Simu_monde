"""Tests for the persistent PID-inspired homeostasis controller."""

from __future__ import annotations

from math import inf, nan

import pytest

from simu_monde.core.homeostasis import HomeostasisController, HomeostasisState


def make_controller(
    *,
    kp: float = 1.0,
    ki_per_s: float = 0.05,
    kd_s: float = 0.2,
    integral_limit_s: float = 8.0,
    activation: float = 0.12,
) -> HomeostasisController:
    return HomeostasisController(
        kp=kp,
        ki_per_s=ki_per_s,
        kd_s=kd_s,
        target_energy_fraction=0.8,
        target_water_fraction=0.8,
        integral_limit_s=integral_limit_s,
        action_activation_urgency=activation,
    )


def test_signed_errors_are_positive_below_and_negative_above_target() -> None:
    signals = make_controller(kd_s=0.0).update(
        state=HomeostasisState(),
        energy_fraction=0.5,
        water_fraction=0.9,
        dt_seconds=1.0,
    )

    assert signals.food_error == pytest.approx(0.3)
    assert signals.water_error == pytest.approx(-0.1)
    assert signals.water_urgency == 0.0


def test_integral_accumulates_and_unwinds_with_signed_error() -> None:
    controller = make_controller(kp=0.0, kd_s=0.0)
    state = HomeostasisState()

    controller.update(state=state, energy_fraction=0.6, water_fraction=0.8, dt_seconds=2.0)
    assert state.food_integral_s == pytest.approx(0.4)

    controller.update(state=state, energy_fraction=1.0, water_fraction=0.8, dt_seconds=1.0)
    assert state.food_integral_s == pytest.approx(0.2)


def test_integral_is_clamped_in_both_directions() -> None:
    controller = make_controller(kp=0.0, kd_s=0.0, integral_limit_s=0.5)
    state = HomeostasisState()

    controller.update(state=state, energy_fraction=0.0, water_fraction=0.0, dt_seconds=10.0)
    assert state.food_integral_s == 0.5
    assert state.water_integral_s == 0.5

    controller.update(state=state, energy_fraction=1.0, water_fraction=1.0, dt_seconds=10.0)
    assert state.food_integral_s == -0.5
    assert state.water_integral_s == -0.5


def test_first_derivative_is_zero_and_worsening_reserve_adds_urgency() -> None:
    controller = make_controller(kp=0.0, ki_per_s=0.0, kd_s=1.0)
    state = HomeostasisState()

    first = controller.update(
        state=state,
        energy_fraction=0.8,
        water_fraction=0.8,
        dt_seconds=1.0,
    )
    second = controller.update(
        state=state,
        energy_fraction=0.6,
        water_fraction=0.5,
        dt_seconds=1.0,
    )

    assert first.food_urgency == 0.0
    assert first.water_urgency == 0.0
    assert second.food_urgency == pytest.approx(0.2)
    assert second.water_urgency == pytest.approx(0.3)


def test_urgency_is_clamped_non_negative() -> None:
    signals = make_controller(ki_per_s=0.0, kd_s=0.0).update(
        state=HomeostasisState(),
        energy_fraction=1.0,
        water_fraction=1.0,
        dt_seconds=1.0,
    )
    assert signals.food_urgency == 0.0
    assert signals.water_urgency == 0.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("kp", -1.0),
        ("ki_per_s", -1.0),
        ("kd_s", -1.0),
        ("target_energy_fraction", -0.1),
        ("target_energy_fraction", 1.1),
        ("target_water_fraction", -0.1),
        ("target_water_fraction", 1.1),
        ("integral_limit_s", 0.0),
        ("action_activation_urgency", -0.1),
    ],
)
def test_controller_rejects_out_of_range_parameters(field: str, value: float) -> None:
    arguments = {
        "kp": 1.0,
        "ki_per_s": 0.05,
        "kd_s": 0.2,
        "target_energy_fraction": 0.8,
        "target_water_fraction": 0.8,
        "integral_limit_s": 8.0,
        "action_activation_urgency": 0.12,
    }
    arguments[field] = value
    with pytest.raises(ValueError):
        HomeostasisController(**arguments)


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_controller_and_state_reject_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError):
        make_controller(kp=value)
    with pytest.raises(ValueError):
        HomeostasisState(food_integral_s=value)
