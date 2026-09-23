"""Headless simulation entry point."""

from __future__ import annotations

from simu_monde.core.herbivore import HerbivoreBehaviorSystem
from simu_monde.core.vegetation import PlantGrowthSystem
from simu_monde.core.world import World


class Simulation:
    """Advance a world one fixed simulation tick at a time."""

    def __init__(
        self,
        world: World,
        plant_growth_system: PlantGrowthSystem | None = None,
        herbivore_behavior_system: HerbivoreBehaviorSystem | None = None,
    ) -> None:
        self._world = world
        self._plant_growth_system = (
            plant_growth_system if plant_growth_system is not None else PlantGrowthSystem()
        )
        self._herbivore_behavior_system = (
            herbivore_behavior_system
            if herbivore_behavior_system is not None
            else HerbivoreBehaviorSystem()
        )

    @property
    def world(self) -> World:
        """The world whose state this simulation advances."""
        return self._world

    def step(self) -> None:
        """Grow plants, update herbivores, then mark the fixed tick complete."""
        self._plant_growth_system.step(
            self._world.plants,
            self._world.clock.dt_seconds,
        )
        self._herbivore_behavior_system.step(
            herbivores=self._world.herbivores,
            plants=self._world.plants,
            bounds=self._world.bounds,
            rng=self._world.rng,
            dt_seconds=self._world.clock.dt_seconds,
        )
        self._world.clock.advance()
