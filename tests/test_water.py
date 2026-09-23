"""Tests for closed water state, rainfall, evaporation, and placement."""

from __future__ import annotations

from math import inf, nan

import pytest

from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.water import (
    EvaporationSystem,
    RainfallSystem,
    WaterSource,
    WaterState,
    create_uniform_water_sources,
)


def make_source(source_id: int = 0, water_kg: float = 1.0) -> WaterSource:
    return WaterSource(source_id, Position2D(1.0, 2.0), water_kg)


@pytest.mark.parametrize("source_id", [True, False, 1.5, "1"])
def test_water_source_rejects_non_integer_id(source_id: object) -> None:
    with pytest.raises(TypeError):
        WaterSource(source_id, Position2D(1.0, 2.0), 1.0)  # type: ignore[arg-type]


def test_water_source_validates_id_position_and_water() -> None:
    with pytest.raises(ValueError):
        make_source(source_id=-1)
    with pytest.raises(TypeError):
        WaterSource(0, (1.0, 2.0), 1.0)  # type: ignore[arg-type]
    for invalid in (-1.0, nan, inf, -inf):
        with pytest.raises(ValueError):
            make_source(water_kg=invalid)


@pytest.mark.parametrize("field", ["atmosphere_water_kg", "soil_water_kg"])
@pytest.mark.parametrize("value", [-1.0, nan, inf, -inf])
def test_water_state_rejects_invalid_global_reservoirs(field: str, value: float) -> None:
    values = {"atmosphere_water_kg": 1.0, "soil_water_kg": 2.0}
    values[field] = value
    with pytest.raises(ValueError):
        WaterState(surface_sources=(), **values)


def test_water_state_owns_tuple_and_rejects_duplicate_source_ids() -> None:
    source = make_source()
    source_list = [source]
    water = WaterState(1.0, 2.0, source_list)  # type: ignore[arg-type]
    source_list.clear()
    assert water.surface_sources == (source,)

    with pytest.raises(ValueError, match="duplicate water_source_id"):
        WaterState(1.0, 2.0, (make_source(1), make_source(1)))


def test_rain_splits_between_soil_and_sources_and_conserves() -> None:
    sources = (make_source(0, 2.0), make_source(1, 3.0))
    water = WaterState(10.0, 4.0, sources)
    total_before = 10.0 + 4.0 + 2.0 + 3.0

    RainfallSystem(rain_rate_kg_per_s=2.0, soil_fraction=0.25).step(water, 2.0)

    assert water.atmosphere_water_kg == 6.0
    assert water.soil_water_kg == 5.0
    assert [source.water_kg for source in sources] == pytest.approx([3.5, 4.5])
    assert water.atmosphere_water_kg + water.soil_water_kg + sum(
        source.water_kg for source in sources
    ) == pytest.approx(total_before)


def test_rain_is_capped_by_atmosphere_and_falls_to_soil_without_sources() -> None:
    water = WaterState(0.3, 1.0, ())

    RainfallSystem(rain_rate_kg_per_s=2.0, soil_fraction=0.0).step(water, 1.0)

    assert water.atmosphere_water_kg == 0.0
    assert water.soil_water_kg == 1.3


def test_zero_rain_rate_changes_nothing() -> None:
    source = make_source()
    water = WaterState(1.0, 2.0, (source,))
    RainfallSystem(0.0, 0.5).step(water, 1.0)
    assert (water.atmosphere_water_kg, water.soil_water_kg, source.water_kg) == (
        1.0,
        2.0,
        1.0,
    )


@pytest.mark.parametrize(
    ("rate", "fraction"),
    [(-1.0, 0.5), (nan, 0.5), (1.0, -0.1), (1.0, 1.1), (1.0, nan)],
)
def test_rain_system_rejects_invalid_parameters(rate: float, fraction: float) -> None:
    with pytest.raises(ValueError):
        RainfallSystem(rate, fraction)


def test_evaporation_transfers_soil_and_each_surface_source() -> None:
    sources = (make_source(0, 0.3), make_source(1, 1.0))
    water = WaterState(2.0, 0.4, sources)
    total_before = 3.7

    EvaporationSystem(
        soil_evaporation_rate_kg_per_s=0.5, surface_evaporation_rate_kg_per_s_per_source=0.2
    ).step(water, 1.0)

    assert water.soil_water_kg == 0.0
    assert [source.water_kg for source in sources] == pytest.approx([0.1, 0.8])
    assert water.atmosphere_water_kg == pytest.approx(2.8)
    assert water.atmosphere_water_kg + sum(source.water_kg for source in sources) == pytest.approx(
        total_before
    )


def test_evaporation_depletion_floor_and_zero_rates() -> None:
    source = make_source(water_kg=0.1)
    water = WaterState(0.0, 0.1, (source,))
    EvaporationSystem(1.0, 1.0).step(water, 1.0)
    assert water.soil_water_kg == 0.0
    assert source.water_kg == 0.0
    assert water.atmosphere_water_kg == pytest.approx(0.2)

    EvaporationSystem(0.0, 0.0).step(water, 1.0)
    assert water.atmosphere_water_kg == pytest.approx(0.2)


@pytest.mark.parametrize("soil_rate", [-1.0, nan, inf])
def test_evaporation_rejects_invalid_rates(soil_rate: float) -> None:
    with pytest.raises(ValueError):
        EvaporationSystem(soil_rate, 0.0)
    with pytest.raises(ValueError):
        EvaporationSystem(0.0, soil_rate)


def test_uniform_source_placement_uses_x_then_y_and_caller_rng() -> None:
    rng = SeededRNG(123)
    replay = SeededRNG(123)
    bounds = WorldBounds(100.0, 50.0)
    sources = create_uniform_water_sources(
        rng=rng,
        bounds=bounds,
        count=2,
        water_kg_per_source=4.0,
    )
    expected = [
        (replay.random() * bounds.width_m, replay.random() * bounds.height_m) for _ in range(2)
    ]

    assert [source.water_source_id for source in sources] == [0, 1]
    assert [(source.position.x_m, source.position.y_m) for source in sources] == expected
    assert all(source.water_kg == 4.0 for source in sources)
    assert rng.random() == replay.random()


def test_source_placement_replays_and_validates_count() -> None:
    bounds = WorldBounds(100.0, 50.0)
    first = create_uniform_water_sources(
        rng=SeededRNG(1), bounds=bounds, count=3, water_kg_per_source=4.0
    )
    second = create_uniform_water_sources(
        rng=SeededRNG(1), bounds=bounds, count=3, water_kg_per_source=4.0
    )
    assert [source.position for source in first] == [source.position for source in second]

    for count, error in [(-1, ValueError), (True, TypeError), (1.5, TypeError)]:
        with pytest.raises(error):
            create_uniform_water_sources(
                rng=SeededRNG(1),
                bounds=WorldBounds(1.0, 1.0),
                count=count,  # type: ignore[arg-type]
                water_kg_per_source=1.0,
            )
