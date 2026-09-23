"""Headless simulation entry point."""

from __future__ import annotations

from math import isfinite

from simu_monde.core.herbivore import HerbivoreBehaviorSystem
from simu_monde.core.vegetation import PlantGrowthSystem
from simu_monde.core.water import (
    WATER_CONSERVATION_ABS_TOL_KG,
    EvaporationSystem,
    RainfallSystem,
)
from simu_monde.core.world import World


class Simulation:
    """Advance a world one fixed simulation tick at a time."""

    def __init__(
        self,
        world: World,
        plant_growth_system: PlantGrowthSystem | None = None,
        herbivore_behavior_system: HerbivoreBehaviorSystem | None = None,
        rainfall_system: RainfallSystem | None = None,
        evaporation_system: EvaporationSystem | None = None,
    ) -> None:
        self._world = world
        self._rainfall_system = (
            rainfall_system
            if rainfall_system is not None
            else RainfallSystem(rain_rate_kg_per_s=0.0, soil_fraction=1.0)
        )
        self._plant_growth_system = (
            plant_growth_system if plant_growth_system is not None else PlantGrowthSystem()
        )
        self._herbivore_behavior_system = (
            herbivore_behavior_system
            if herbivore_behavior_system is not None
            else HerbivoreBehaviorSystem()
        )
        self._evaporation_system = (
            evaporation_system
            if evaporation_system is not None
            else EvaporationSystem(
                soil_evaporation_rate_kg_per_s=0.0,
                surface_evaporation_rate_kg_per_s_per_source=0.0,
            )
        )

    @property
    def world(self) -> World:
        """The world whose state this simulation advances."""
        return self._world

    def step(self) -> None:
        """Apply the approved water/ecology order and verify conservation."""
        total_water_before_kg = self._world.total_water_kg
        dt_seconds = self._world.clock.dt_seconds
        self._rainfall_system.step(self._world.water, dt_seconds)
        self._plant_growth_system.step(
            self._world.plants,
            self._world.water,
            dt_seconds,
        )
        self._herbivore_behavior_system.step(
            herbivores=self._world.herbivores,
            plants=self._world.plants,
            water=self._world.water,
            bounds=self._world.bounds,
            rng=self._world.rng,
            dt_seconds=dt_seconds,
        )
        self._evaporation_system.step(self._world.water, dt_seconds)
        total_water_after_kg = self._world.total_water_kg
        if (
            not isfinite(total_water_before_kg)
            or not isfinite(total_water_after_kg)
            or abs(total_water_after_kg - total_water_before_kg) > WATER_CONSERVATION_ABS_TOL_KG
        ):
            raise RuntimeError(
                "water conservation violated: "
                f"before={total_water_before_kg!r} kg, "
                f"after={total_water_after_kg!r} kg"
            )
        self._world.clock.advance()
