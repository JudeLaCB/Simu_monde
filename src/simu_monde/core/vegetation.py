"""Minimal deterministic vegetation domain model."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite

from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.water import WaterState


def _require_finite(value: float, name: str) -> float:
    """Return ``value`` as a float when it is a finite numeric value."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")

    try:
        valid = isfinite(value)
    except TypeError as error:
        raise ValueError(f"{name} must be a finite number") from error

    if not valid:
        raise ValueError(f"{name} must be a finite number")
    return float(value)


@dataclass(slots=True)
class Plant:
    """A positioned plant with edible biomass measured in kilograms."""

    plant_id: int
    position: Position2D
    edible_biomass_kg: float
    max_edible_biomass_kg: float
    growth_rate_kg_per_s: float
    age_s: float
    lifespan_s: float

    def __post_init__(self) -> None:
        if isinstance(self.plant_id, bool) or not isinstance(self.plant_id, int):
            raise TypeError("plant_id must be an integer, not a boolean")
        if self.plant_id < 0:
            raise ValueError("plant_id must be non-negative")
        if not isinstance(self.position, Position2D):
            raise TypeError("position must be a Position2D")

        max_biomass = _require_finite(
            self.max_edible_biomass_kg,
            "max_edible_biomass_kg",
        )
        if max_biomass <= 0:
            raise ValueError("max_edible_biomass_kg must be positive")

        biomass = _require_finite(self.edible_biomass_kg, "edible_biomass_kg")
        if biomass < 0:
            raise ValueError("edible_biomass_kg must be non-negative")
        if biomass > max_biomass:
            raise ValueError("edible_biomass_kg must not exceed max_edible_biomass_kg")

        growth_rate = _require_finite(self.growth_rate_kg_per_s, "growth_rate_kg_per_s")
        if growth_rate < 0:
            raise ValueError("growth_rate_kg_per_s must be non-negative")

        self.edible_biomass_kg = biomass
        self.max_edible_biomass_kg = max_biomass
        self.growth_rate_kg_per_s = growth_rate
        age_s = _require_finite(self.age_s, "age_s")
        if age_s < 0.0:
            raise ValueError("age_s must be non-negative")
        lifespan_s = _require_finite(self.lifespan_s, "lifespan_s")
        if lifespan_s <= 0.0:
            raise ValueError("lifespan_s must be positive")
        self.age_s = age_s
        self.lifespan_s = lifespan_s


class PlantGrowthSystem:
    """Apply water-limited growth with same-tick soil-to-atmosphere transpiration."""

    def __init__(self, water_kg_per_biomass_kg: float = 0.2) -> None:
        self._water_coefficient = _require_finite(
            water_kg_per_biomass_kg, "water_kg_per_biomass_kg"
        )
        if self._water_coefficient <= 0.0:
            raise ValueError("water_kg_per_biomass_kg must be positive")

    def step(
        self,
        plants: Sequence[Plant],
        water: WaterState,
        dt_seconds: float,
    ) -> None:
        """Grow plants in order, transferring all used soil water to atmosphere."""
        for plant in plants:
            potential_growth_kg = min(
                plant.growth_rate_kg_per_s * dt_seconds,
                plant.max_edible_biomass_kg - plant.edible_biomass_kg,
            )
            required_water_kg = potential_growth_kg * self._water_coefficient
            used_water_kg = min(required_water_kg, water.soil_water_kg)
            actual_growth_kg = used_water_kg / self._water_coefficient
            water.soil_water_kg = max(0.0, water.soil_water_kg - used_water_kg)
            water.atmosphere_water_kg += used_water_kg
            plant.edible_biomass_kg = min(
                plant.max_edible_biomass_kg,
                plant.edible_biomass_kg + actual_growth_kg,
            )


def create_uniform_plants(
    *,
    rng: SeededRNG,
    bounds: WorldBounds,
    count: int,
    initial_biomass_kg: float,
    max_biomass_kg: float,
    growth_rate_kg_per_s: float,
    age_s: float,
    lifespan_s: float,
) -> tuple[Plant, ...]:
    """Create a replayable uniformly placed plant collection using ``rng``."""
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an integer, not a boolean")
    if count < 0:
        raise ValueError("count must be non-negative")

    plants: list[Plant] = []
    for plant_id in range(count):
        x_m = rng.random() * bounds.width_m
        y_m = rng.random() * bounds.height_m
        plants.append(
            Plant(
                plant_id=plant_id,
                position=Position2D(x_m=x_m, y_m=y_m),
                edible_biomass_kg=initial_biomass_kg,
                max_edible_biomass_kg=max_biomass_kg,
                growth_rate_kg_per_s=growth_rate_kg_per_s,
                age_s=age_s,
                lifespan_s=lifespan_s,
            )
        )
    return tuple(plants)
