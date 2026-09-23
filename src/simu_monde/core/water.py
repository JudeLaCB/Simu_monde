"""Closed, deterministic water-cycle state and transfer systems."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.randomness import SeededRNG

WATER_CONSERVATION_ABS_TOL_KG = 1e-8


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
class WaterSource:
    """A spatial surface-water reservoir measured in kilograms."""

    water_source_id: int
    position: Position2D
    water_kg: float

    def __post_init__(self) -> None:
        if isinstance(self.water_source_id, bool) or not isinstance(self.water_source_id, int):
            raise TypeError("water_source_id must be an integer, not a boolean")
        if self.water_source_id < 0:
            raise ValueError("water_source_id must be non-negative")
        if not isinstance(self.position, Position2D):
            raise TypeError("position must be a Position2D")
        self.water_kg = _require_non_negative(self.water_kg, "water_kg")


@dataclass(slots=True)
class WaterState:
    """The atmosphere, soil, and ordered surface reservoirs."""

    atmosphere_water_kg: float
    soil_water_kg: float
    surface_sources: tuple[WaterSource, ...]

    def __post_init__(self) -> None:
        self.atmosphere_water_kg = _require_non_negative(
            self.atmosphere_water_kg, "atmosphere_water_kg"
        )
        self.soil_water_kg = _require_non_negative(self.soil_water_kg, "soil_water_kg")
        self.surface_sources = tuple(self.surface_sources)
        source_ids: set[int] = set()
        for source in self.surface_sources:
            if not isinstance(source, WaterSource):
                raise TypeError("surface_sources must contain WaterSource objects")
            if source.water_source_id in source_ids:
                raise ValueError(f"duplicate water_source_id: {source.water_source_id}")
            source_ids.add(source.water_source_id)


class RainfallSystem:
    """Transfer deterministic rainfall from atmosphere to soil and surface."""

    def __init__(self, rain_rate_kg_per_s: float, soil_fraction: float) -> None:
        self._rain_rate_kg_per_s = _require_non_negative(rain_rate_kg_per_s, "rain_rate_kg_per_s")
        self._soil_fraction = _require_finite(soil_fraction, "soil_fraction")
        if not 0.0 <= self._soil_fraction <= 1.0:
            raise ValueError("soil_fraction must be between 0 and 1")

    def step(self, water: WaterState, dt_seconds: float) -> None:
        """Move available atmospheric water using the approved fixed split."""
        rain_kg = min(
            water.atmosphere_water_kg,
            self._rain_rate_kg_per_s * dt_seconds,
        )
        if not water.surface_sources:
            water.soil_water_kg += rain_kg
        else:
            to_soil_kg = rain_kg * self._soil_fraction
            per_source_kg = (rain_kg - to_soil_kg) / len(water.surface_sources)
            water.soil_water_kg += to_soil_kg
            for source in water.surface_sources:
                source.water_kg += per_source_kg
        water.atmosphere_water_kg = max(0.0, water.atmosphere_water_kg - rain_kg)


class EvaporationSystem:
    """Transfer passive soil and surface evaporation into the atmosphere."""

    def __init__(
        self,
        soil_evaporation_rate_kg_per_s: float,
        surface_evaporation_rate_kg_per_s_per_source: float,
    ) -> None:
        self._soil_rate = _require_non_negative(
            soil_evaporation_rate_kg_per_s, "soil_evaporation_rate_kg_per_s"
        )
        self._surface_rate = _require_non_negative(
            surface_evaporation_rate_kg_per_s_per_source,
            "surface_evaporation_rate_kg_per_s_per_source",
        )

    def step(self, water: WaterState, dt_seconds: float) -> None:
        """Evaporate each reservoir without allowing it to become negative."""
        soil_evaporation_kg = min(water.soil_water_kg, self._soil_rate * dt_seconds)
        water.soil_water_kg = max(0.0, water.soil_water_kg - soil_evaporation_kg)
        water.atmosphere_water_kg += soil_evaporation_kg

        for source in water.surface_sources:
            surface_evaporation_kg = min(source.water_kg, self._surface_rate * dt_seconds)
            source.water_kg = max(0.0, source.water_kg - surface_evaporation_kg)
            water.atmosphere_water_kg += surface_evaporation_kg


def create_uniform_water_sources(
    *,
    rng: SeededRNG,
    bounds: WorldBounds,
    count: int,
    water_kg_per_source: float,
) -> tuple[WaterSource, ...]:
    """Create sources using caller RNG draws in exact x-then-y order."""
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an integer, not a boolean")
    if count < 0:
        raise ValueError("count must be non-negative")

    return tuple(
        WaterSource(
            water_source_id=source_id,
            position=Position2D(
                x_m=rng.random() * bounds.width_m,
                y_m=rng.random() * bounds.height_m,
            ),
            water_kg=water_kg_per_source,
        )
        for source_id in range(count)
    )
