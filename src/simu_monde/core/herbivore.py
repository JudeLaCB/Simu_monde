"""Deterministic minimal herbivore domain model and behavior."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import atan2, cos, dist, isfinite, pi, sin

from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.vegetation import Plant

TAU = 2.0 * pi


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


def normalize_heading(heading_rad: float) -> float:
    """Normalize a finite heading to the half-open interval [0, 2π)."""
    return _require_finite(heading_rad, "heading_rad") % TAU


@dataclass(slots=True)
class Herbivore:
    """A point herbivore whose state and parameters use explicit SI units."""

    herbivore_id: int
    position: Position2D
    hunger: float
    heading_rad: float
    speed_m_per_s: float
    perception_radius_m: float
    feeding_radius_m: float
    hunger_rate_per_s: float
    feeding_rate_kg_per_s: float
    food_capacity_kg: float
    seek_food_hunger_threshold: float

    def __post_init__(self) -> None:
        if isinstance(self.herbivore_id, bool) or not isinstance(self.herbivore_id, int):
            raise TypeError("herbivore_id must be an integer, not a boolean")
        if self.herbivore_id < 0:
            raise ValueError("herbivore_id must be non-negative")
        if not isinstance(self.position, Position2D):
            raise TypeError("position must be a Position2D")

        self.hunger = _require_finite(self.hunger, "hunger")
        if not 0.0 <= self.hunger <= 1.0:
            raise ValueError("hunger must be between 0 and 1")
        self.heading_rad = normalize_heading(self.heading_rad)
        self.speed_m_per_s = _require_non_negative(self.speed_m_per_s, "speed_m_per_s")
        self.perception_radius_m = _require_non_negative(
            self.perception_radius_m, "perception_radius_m"
        )
        self.feeding_radius_m = _require_non_negative(self.feeding_radius_m, "feeding_radius_m")
        self.hunger_rate_per_s = _require_non_negative(self.hunger_rate_per_s, "hunger_rate_per_s")
        self.feeding_rate_kg_per_s = _require_non_negative(
            self.feeding_rate_kg_per_s, "feeding_rate_kg_per_s"
        )
        self.food_capacity_kg = _require_finite(self.food_capacity_kg, "food_capacity_kg")
        if self.food_capacity_kg <= 0.0:
            raise ValueError("food_capacity_kg must be positive")
        self.seek_food_hunger_threshold = _require_finite(
            self.seek_food_hunger_threshold, "seek_food_hunger_threshold"
        )
        if not 0.0 <= self.seek_food_hunger_threshold <= 1.0:
            raise ValueError("seek_food_hunger_threshold must be between 0 and 1")


def _reflect_axis(start: float, displacement: float, limit: float) -> tuple[float, float]:
    position = start + displacement
    reflected_displacement = displacement
    while position < 0.0 or position > limit:
        if position < 0.0:
            position = -position
        else:
            position = 2.0 * limit - position
        reflected_displacement = -reflected_displacement
    return position, reflected_displacement


def reflect_travel(
    *,
    position: Position2D,
    heading_rad: float,
    distance_m: float,
    bounds: WorldBounds,
) -> tuple[Position2D, float]:
    """Travel through a rectangular world, reflecting each crossed axis."""
    distance_m = _require_non_negative(distance_m, "distance_m")
    heading_rad = normalize_heading(heading_rad)
    if distance_m == 0.0:
        return position, heading_rad

    x_m, reflected_dx = _reflect_axis(position.x_m, cos(heading_rad) * distance_m, bounds.width_m)
    y_m, reflected_dy = _reflect_axis(position.y_m, sin(heading_rad) * distance_m, bounds.height_m)
    reflected_heading = normalize_heading(atan2(reflected_dy, reflected_dx))
    return Position2D(x_m=x_m, y_m=y_m), reflected_heading


def _distance_squared(first: Position2D, second: Position2D) -> float:
    dx_m = second.x_m - first.x_m
    dy_m = second.y_m - first.y_m
    return dx_m * dx_m + dy_m * dy_m


def _nearest_visible_plant(herbivore: Herbivore, plants: Sequence[Plant]) -> Plant | None:
    radius_squared = herbivore.perception_radius_m**2
    candidates = (
        plant
        for plant in plants
        if plant.edible_biomass_kg > 0.0
        and _distance_squared(herbivore.position, plant.position) <= radius_squared
    )
    return min(
        candidates,
        key=lambda plant: (_distance_squared(herbivore.position, plant.position), plant.plant_id),
        default=None,
    )


class HerbivoreBehaviorSystem:
    """Apply hunger, local food seeking, feeding, and bounded exploration."""

    def __init__(self, exploration_turn_rate_rad_per_s: float = 0.8) -> None:
        self._exploration_turn_rate_rad_per_s = _require_non_negative(
            exploration_turn_rate_rad_per_s, "exploration_turn_rate_rad_per_s"
        )

    def step(
        self,
        *,
        herbivores: Sequence[Herbivore],
        plants: Sequence[Plant],
        bounds: WorldBounds,
        rng: SeededRNG,
        dt_seconds: float,
    ) -> None:
        """Advance herbivores in stored order, including sequential consumption."""
        for herbivore in herbivores:
            herbivore.hunger = min(1.0, herbivore.hunger + herbivore.hunger_rate_per_s * dt_seconds)
            target = None
            if herbivore.hunger >= herbivore.seek_food_hunger_threshold:
                target = _nearest_visible_plant(herbivore, plants)

            if target is None:
                self._explore(herbivore, bounds, rng, dt_seconds)
                continue

            distance_to_target = dist(
                (herbivore.position.x_m, herbivore.position.y_m),
                (target.position.x_m, target.position.y_m),
            )
            if distance_to_target <= herbivore.feeding_radius_m:
                self._feed(herbivore, target, dt_seconds)
            else:
                self._seek(herbivore, target, distance_to_target, dt_seconds)

    def _explore(
        self,
        herbivore: Herbivore,
        bounds: WorldBounds,
        rng: SeededRNG,
        dt_seconds: float,
    ) -> None:
        random_turn = (
            (2.0 * rng.random() - 1.0) * self._exploration_turn_rate_rad_per_s * dt_seconds
        )
        herbivore.heading_rad = normalize_heading(herbivore.heading_rad + random_turn)
        herbivore.position, herbivore.heading_rad = reflect_travel(
            position=herbivore.position,
            heading_rad=herbivore.heading_rad,
            distance_m=herbivore.speed_m_per_s * dt_seconds,
            bounds=bounds,
        )

    @staticmethod
    def _seek(
        herbivore: Herbivore,
        target: Plant,
        distance_to_target: float,
        dt_seconds: float,
    ) -> None:
        dx_m = target.position.x_m - herbivore.position.x_m
        dy_m = target.position.y_m - herbivore.position.y_m
        heading = normalize_heading(atan2(dy_m, dx_m))
        travel_distance = min(
            herbivore.speed_m_per_s * dt_seconds,
            distance_to_target - herbivore.feeding_radius_m,
        )
        herbivore.position = Position2D(
            x_m=herbivore.position.x_m + cos(heading) * travel_distance,
            y_m=herbivore.position.y_m + sin(heading) * travel_distance,
        )
        herbivore.heading_rad = heading

    @staticmethod
    def _feed(herbivore: Herbivore, target: Plant, dt_seconds: float) -> None:
        bite_kg = herbivore.feeding_rate_kg_per_s * dt_seconds
        needed_kg = herbivore.hunger * herbivore.food_capacity_kg
        eaten_kg = min(bite_kg, target.edible_biomass_kg, needed_kg)
        target.edible_biomass_kg = max(0.0, target.edible_biomass_kg - eaten_kg)
        herbivore.hunger = max(0.0, herbivore.hunger - eaten_kg / herbivore.food_capacity_kg)


def create_uniform_herbivores(
    *,
    rng: SeededRNG,
    bounds: WorldBounds,
    count: int,
    hunger: float,
    speed_m_per_s: float,
    perception_radius_m: float,
    feeding_radius_m: float,
    hunger_rate_per_s: float,
    feeding_rate_kg_per_s: float,
    food_capacity_kg: float,
    seek_food_hunger_threshold: float,
) -> tuple[Herbivore, ...]:
    """Create herbivores with deterministic x, y, then heading draws per animal."""
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an integer, not a boolean")
    if count < 0:
        raise ValueError("count must be non-negative")

    herbivores: list[Herbivore] = []
    for herbivore_id in range(count):
        herbivores.append(
            Herbivore(
                herbivore_id=herbivore_id,
                position=Position2D(
                    x_m=rng.random() * bounds.width_m,
                    y_m=rng.random() * bounds.height_m,
                ),
                hunger=hunger,
                heading_rad=rng.random() * TAU,
                speed_m_per_s=speed_m_per_s,
                perception_radius_m=perception_radius_m,
                feeding_radius_m=feeding_radius_m,
                hunger_rate_per_s=hunger_rate_per_s,
                feeding_rate_kg_per_s=feeding_rate_kg_per_s,
                food_capacity_kg=food_capacity_kg,
                seek_food_hunger_threshold=seek_food_hunger_threshold,
            )
        )
    return tuple(herbivores)
