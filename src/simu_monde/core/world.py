"""The minimal deterministic world aggregate."""

from __future__ import annotations

from collections.abc import Iterable

from simu_monde.core.clock import SimulationClock
from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import WorldBounds
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.vegetation import Plant


class World:
    """Own the core services derived from one simulation configuration."""

    def __init__(self, config: SimulationConfig, plants: Iterable[Plant] = ()) -> None:
        self._config = config
        self._bounds = WorldBounds(width_m=config.width_m, height_m=config.height_m)
        self._clock = SimulationClock(dt_seconds=config.dt_seconds)
        self._rng = SeededRNG(seed=config.seed)
        self._plants = tuple(plants)

        plant_ids: set[int] = set()
        for plant in self._plants:
            if plant.plant_id in plant_ids:
                raise ValueError(f"duplicate plant_id: {plant.plant_id}")
            if not self._bounds.contains(plant.position):
                raise ValueError(f"plant {plant.plant_id} position is outside world bounds")
            plant_ids.add(plant.plant_id)

    @property
    def config(self) -> SimulationConfig:
        """The immutable configuration used to initialize this world."""
        return self._config

    @property
    def bounds(self) -> WorldBounds:
        """The closed spatial bounds of this world."""
        return self._bounds

    @property
    def clock(self) -> SimulationClock:
        """The world's fixed-timestep simulation clock."""
        return self._clock

    @property
    def rng(self) -> SeededRNG:
        """The world's deterministic random-number stream."""
        return self._rng

    @property
    def plants(self) -> tuple[Plant, ...]:
        """The ordered plant collection, structurally exposed as an immutable tuple."""
        return self._plants
