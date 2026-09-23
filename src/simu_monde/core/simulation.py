"""Headless simulation entry point."""

from __future__ import annotations

from simu_monde.core.vegetation import PlantGrowthSystem
from simu_monde.core.world import World


class Simulation:
    """Advance a world one fixed simulation tick at a time."""

    def __init__(
        self,
        world: World,
        plant_growth_system: PlantGrowthSystem | None = None,
    ) -> None:
        self._world = world
        self._plant_growth_system = (
            plant_growth_system if plant_growth_system is not None else PlantGrowthSystem()
        )

    @property
    def world(self) -> World:
        """The world whose state this simulation advances."""
        return self._world

    def step(self) -> None:
        """Grow plants over one fixed timestep, then mark the tick complete."""
        self._plant_growth_system.step(
            self._world.plants,
            self._world.clock.dt_seconds,
        )
        self._world.clock.advance()
