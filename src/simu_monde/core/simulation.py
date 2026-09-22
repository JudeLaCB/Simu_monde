"""Headless simulation entry point."""

from __future__ import annotations

from simu_monde.core.world import World


class Simulation:
    """Advance a world one fixed simulation tick at a time."""

    def __init__(self, world: World) -> None:
        self._world = world

    @property
    def world(self) -> World:
        """The world whose state this simulation advances."""
        return self._world

    def step(self) -> None:
        """Perform the Phase 1A state transition: advance one clock tick."""
        self._world.clock.advance()
