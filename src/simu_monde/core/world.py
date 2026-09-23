"""The minimal deterministic world aggregate."""

from __future__ import annotations

from collections.abc import Iterable

from simu_monde.core.clock import SimulationClock
from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import WorldBounds
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.vegetation import Plant
from simu_monde.core.water import WaterState


class World:
    """Own the core services derived from one simulation configuration."""

    def __init__(
        self,
        config: SimulationConfig,
        plants: Iterable[Plant] = (),
        herbivores: Iterable[Herbivore] = (),
        water_state: WaterState | None = None,
    ) -> None:
        self._config = config
        self._bounds = WorldBounds(width_m=config.width_m, height_m=config.height_m)
        self._clock = SimulationClock(dt_seconds=config.dt_seconds)
        self._rng = SeededRNG(seed=config.seed)
        self._plants = tuple(plants)
        self._herbivores = tuple(herbivores)
        self._water = (
            water_state
            if water_state is not None
            else WaterState(atmosphere_water_kg=0.0, soil_water_kg=0.0, surface_sources=())
        )

        plant_ids: set[int] = set()
        for plant in self._plants:
            if plant.plant_id in plant_ids:
                raise ValueError(f"duplicate plant_id: {plant.plant_id}")
            if not self._bounds.contains(plant.position):
                raise ValueError(f"plant {plant.plant_id} position is outside world bounds")
            plant_ids.add(plant.plant_id)

        herbivore_ids: set[int] = set()
        for herbivore in self._herbivores:
            if herbivore.herbivore_id in herbivore_ids:
                raise ValueError(f"duplicate herbivore_id: {herbivore.herbivore_id}")
            if not self._bounds.contains(herbivore.position):
                raise ValueError(
                    f"herbivore {herbivore.herbivore_id} position is outside world bounds"
                )
            herbivore_ids.add(herbivore.herbivore_id)

        for source in self._water.surface_sources:
            if not self._bounds.contains(source.position):
                raise ValueError(
                    f"water source {source.water_source_id} position is outside world bounds"
                )

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

    @property
    def herbivores(self) -> tuple[Herbivore, ...]:
        """The ordered herbivore collection, structurally exposed as an immutable tuple."""
        return self._herbivores

    @property
    def water(self) -> WaterState:
        """The world's atmosphere, soil, and ordered surface water state."""
        return self._water

    @property
    def total_water_kg(self) -> float:
        """Return all modeled water across the four approved reservoirs."""
        return (
            self._water.atmosphere_water_kg
            + self._water.soil_water_kg
            + sum(source.water_kg for source in self._water.surface_sources)
            + sum(herbivore.body_water_kg for herbivore in self._herbivores)
        )
