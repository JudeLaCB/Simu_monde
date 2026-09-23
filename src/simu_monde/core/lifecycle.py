"""Explicit deterministic mortality and carcass lifecycle operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import TYPE_CHECKING

from simu_monde.core.geometry import Position2D

if TYPE_CHECKING:
    from simu_monde.core.world import World


def _require_finite_non_negative(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite, non-negative number")
    try:
        valid = isfinite(value)
    except TypeError as error:
        raise ValueError(f"{name} must be a finite, non-negative number") from error
    if not valid or value < 0.0:
        raise ValueError(f"{name} must be a finite, non-negative number")
    return float(value)


class DeathCause(Enum):
    """Approved deterministic causes of herbivore mortality."""

    STARVATION = "starvation"
    OLD_AGE = "old_age"


@dataclass(slots=True)
class Carcass:
    """Persistent spatial stocks transferred from one dead herbivore."""

    carcass_id: int
    source_herbivore_id: int
    position: Position2D
    death_cause: DeathCause
    water_kg: float
    recoverable_nutrient_kg: float
    age_s: float = 0.0

    def __post_init__(self) -> None:
        for value, name in (
            (self.carcass_id, "carcass_id"),
            (self.source_herbivore_id, "source_herbivore_id"),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer, not a boolean")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
        if not isinstance(self.position, Position2D):
            raise TypeError("position must be a Position2D")
        if not isinstance(self.death_cause, DeathCause):
            raise TypeError("death_cause must be a DeathCause")
        self.water_kg = _require_finite_non_negative(self.water_kg, "water_kg")
        self.recoverable_nutrient_kg = _require_finite_non_negative(
            self.recoverable_nutrient_kg, "recoverable_nutrient_kg"
        )
        self.age_s = _require_finite_non_negative(self.age_s, "age_s")


class MortalitySystem:
    """Age living entities, remove deaths, and create persistent carcasses."""

    def step(self, *, world: World, dt_seconds: float) -> None:
        """Apply the approved mortality stage once per completed tick interval."""
        surviving_plants = []
        for plant in world.plants:
            plant.age_s += dt_seconds
            if plant.age_s < plant.lifespan_s:
                surviving_plants.append(plant)

        surviving_herbivores = []
        deaths = []
        for herbivore in world.herbivores:
            herbivore.age_s += dt_seconds
            if herbivore.energy_j <= 0.0:
                deaths.append((herbivore, DeathCause.STARVATION))
            elif herbivore.age_s >= herbivore.lifespan_s:
                deaths.append((herbivore, DeathCause.OLD_AGE))
            else:
                surviving_herbivores.append(herbivore)

        world.replace_plants(surviving_plants)
        for herbivore, cause in deaths:
            world.add_carcass_from_herbivore(herbivore, cause)
        world.replace_herbivores(surviving_herbivores)
