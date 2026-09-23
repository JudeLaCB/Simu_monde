"""Deterministic minimal herbivore domain model and behavior."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from math import atan2, cos, dist, isfinite, pi, sin

from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.homeostasis import (
    HomeostasisController,
    HomeostasisState,
    create_default_homeostasis_controller,
)
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.vegetation import Plant
from simu_monde.core.water import WaterSource, WaterState

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
    heading_rad: float
    speed_m_per_s: float
    perception_radius_m: float
    feeding_radius_m: float
    feeding_rate_kg_per_s: float
    body_water_kg: float
    max_body_water_kg: float
    water_loss_kg_per_s: float
    drinking_rate_kg_per_s: float
    drinking_radius_m: float
    energy_j: float
    max_energy_j: float
    basal_power_w: float
    movement_energy_j_per_m: float
    food_energy_j_per_kg: float
    age_s: float
    lifespan_s: float
    recoverable_nutrient_kg: float
    homeostasis: HomeostasisState = field(default_factory=HomeostasisState)

    def __post_init__(self) -> None:
        if isinstance(self.herbivore_id, bool) or not isinstance(self.herbivore_id, int):
            raise TypeError("herbivore_id must be an integer, not a boolean")
        if self.herbivore_id < 0:
            raise ValueError("herbivore_id must be non-negative")
        if not isinstance(self.position, Position2D):
            raise TypeError("position must be a Position2D")

        self.heading_rad = normalize_heading(self.heading_rad)
        self.speed_m_per_s = _require_non_negative(self.speed_m_per_s, "speed_m_per_s")
        self.perception_radius_m = _require_non_negative(
            self.perception_radius_m, "perception_radius_m"
        )
        self.feeding_radius_m = _require_non_negative(self.feeding_radius_m, "feeding_radius_m")
        self.feeding_rate_kg_per_s = _require_non_negative(
            self.feeding_rate_kg_per_s, "feeding_rate_kg_per_s"
        )

        self.max_body_water_kg = _require_finite(self.max_body_water_kg, "max_body_water_kg")
        if self.max_body_water_kg <= 0.0:
            raise ValueError("max_body_water_kg must be positive")
        self.body_water_kg = _require_non_negative(self.body_water_kg, "body_water_kg")
        if self.body_water_kg > self.max_body_water_kg:
            raise ValueError("body_water_kg must not exceed max_body_water_kg")
        self.water_loss_kg_per_s = _require_non_negative(
            self.water_loss_kg_per_s, "water_loss_kg_per_s"
        )
        self.drinking_rate_kg_per_s = _require_non_negative(
            self.drinking_rate_kg_per_s, "drinking_rate_kg_per_s"
        )
        self.drinking_radius_m = _require_non_negative(self.drinking_radius_m, "drinking_radius_m")
        self.max_energy_j = _require_finite(self.max_energy_j, "max_energy_j")
        if self.max_energy_j <= 0.0:
            raise ValueError("max_energy_j must be positive")
        self.energy_j = _require_non_negative(self.energy_j, "energy_j")
        if self.energy_j > self.max_energy_j:
            raise ValueError("energy_j must not exceed max_energy_j")
        self.basal_power_w = _require_non_negative(self.basal_power_w, "basal_power_w")
        self.movement_energy_j_per_m = _require_non_negative(
            self.movement_energy_j_per_m, "movement_energy_j_per_m"
        )
        self.food_energy_j_per_kg = _require_finite(
            self.food_energy_j_per_kg, "food_energy_j_per_kg"
        )
        if self.food_energy_j_per_kg <= 0.0:
            raise ValueError("food_energy_j_per_kg must be positive")
        self.age_s = _require_non_negative(self.age_s, "age_s")
        self.lifespan_s = _require_finite(self.lifespan_s, "lifespan_s")
        if self.lifespan_s <= 0.0:
            raise ValueError("lifespan_s must be positive")
        self.recoverable_nutrient_kg = _require_non_negative(
            self.recoverable_nutrient_kg, "recoverable_nutrient_kg"
        )
        if not isinstance(self.homeostasis, HomeostasisState):
            raise TypeError("homeostasis must be a HomeostasisState")

    @property
    def energy_fraction(self) -> float:
        """Return the dimensionless energy reserve fraction in [0, 1]."""
        return min(1.0, max(0.0, self.energy_j / self.max_energy_j))

    @property
    def thirst(self) -> float:
        """Return the dimensionless body-water deficit in [0, 1]."""
        return min(1.0, max(0.0, 1.0 - self.body_water_kg / self.max_body_water_kg))


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


def _nearest_visible_water_source(
    herbivore: Herbivore,
    sources: Sequence[WaterSource],
) -> WaterSource | None:
    radius_squared = herbivore.perception_radius_m**2
    candidates = (
        source
        for source in sources
        if source.water_kg > 0.0
        and _distance_squared(herbivore.position, source.position) <= radius_squared
    )
    return min(
        candidates,
        key=lambda source: (
            _distance_squared(herbivore.position, source.position),
            source.water_source_id,
        ),
        default=None,
    )


class HerbivoreBehaviorSystem:
    """Regulate energy and hydration through feasible locally perceived actions."""

    def __init__(
        self,
        exploration_turn_rate_rad_per_s: float = 0.8,
        controller: HomeostasisController | None = None,
    ) -> None:
        self._exploration_turn_rate_rad_per_s = _require_non_negative(
            exploration_turn_rate_rad_per_s, "exploration_turn_rate_rad_per_s"
        )
        self._controller = (
            controller if controller is not None else create_default_homeostasis_controller()
        )

    def step(
        self,
        *,
        herbivores: Sequence[Herbivore],
        plants: Sequence[Plant],
        water: WaterState,
        bounds: WorldBounds,
        rng: SeededRNG,
        dt_seconds: float,
    ) -> None:
        """Pay metabolism, update control state, arbitrate, and act in world order."""
        for herbivore in herbivores:
            basal_cost_j = herbivore.basal_power_w * dt_seconds
            herbivore.energy_j = max(0.0, herbivore.energy_j - basal_cost_j)
            water_lost_kg = min(
                herbivore.body_water_kg,
                herbivore.water_loss_kg_per_s * dt_seconds,
            )
            herbivore.body_water_kg = max(0.0, herbivore.body_water_kg - water_lost_kg)
            water.atmosphere_water_kg += water_lost_kg

            signals = self._controller.update(
                state=herbivore.homeostasis,
                energy_fraction=herbivore.energy_fraction,
                water_fraction=1.0 - herbivore.thirst,
                dt_seconds=dt_seconds,
            )
            if herbivore.energy_j <= 0.0:
                continue

            food_target = _nearest_visible_plant(herbivore, plants)
            water_target = _nearest_visible_water_source(herbivore, water.surface_sources)
            food_active = (
                food_target is not None
                and signals.food_urgency >= self._controller.action_activation_urgency
            )
            water_active = (
                water_target is not None
                and signals.water_urgency >= self._controller.action_activation_urgency
            )

            if (
                water_target is not None
                and water_active
                and (not food_active or signals.water_urgency >= signals.food_urgency)
            ):
                distance_to_water = dist(
                    (herbivore.position.x_m, herbivore.position.y_m),
                    (water_target.position.x_m, water_target.position.y_m),
                )
                if distance_to_water <= herbivore.drinking_radius_m:
                    self._drink(herbivore, water_target, dt_seconds)
                else:
                    distance_travelled_m = self._seek_position(
                        herbivore,
                        water_target.position,
                        distance_to_water,
                        herbivore.drinking_radius_m,
                        dt_seconds,
                    )
                    self._pay_movement_cost(herbivore, distance_travelled_m)
                continue

            if food_target is not None and food_active:
                distance_to_target = dist(
                    (herbivore.position.x_m, herbivore.position.y_m),
                    (food_target.position.x_m, food_target.position.y_m),
                )
                if distance_to_target <= herbivore.feeding_radius_m:
                    self._feed(herbivore, food_target, dt_seconds)
                else:
                    distance_travelled_m = self._seek_position(
                        herbivore,
                        food_target.position,
                        distance_to_target,
                        herbivore.feeding_radius_m,
                        dt_seconds,
                    )
                    self._pay_movement_cost(herbivore, distance_travelled_m)
                continue

            distance_travelled_m = self._explore(herbivore, bounds, rng, dt_seconds)
            self._pay_movement_cost(herbivore, distance_travelled_m)

    def _explore(
        self,
        herbivore: Herbivore,
        bounds: WorldBounds,
        rng: SeededRNG,
        dt_seconds: float,
    ) -> float:
        random_turn = (
            (2.0 * rng.random() - 1.0) * self._exploration_turn_rate_rad_per_s * dt_seconds
        )
        herbivore.heading_rad = normalize_heading(herbivore.heading_rad + random_turn)
        distance_travelled_m = herbivore.speed_m_per_s * dt_seconds
        herbivore.position, herbivore.heading_rad = reflect_travel(
            position=herbivore.position,
            heading_rad=herbivore.heading_rad,
            distance_m=distance_travelled_m,
            bounds=bounds,
        )
        return distance_travelled_m

    @staticmethod
    def _seek_position(
        herbivore: Herbivore,
        target_position: Position2D,
        distance_to_target: float,
        stopping_radius_m: float,
        dt_seconds: float,
    ) -> float:
        dx_m = target_position.x_m - herbivore.position.x_m
        dy_m = target_position.y_m - herbivore.position.y_m
        heading = normalize_heading(atan2(dy_m, dx_m))
        travel_distance = min(
            herbivore.speed_m_per_s * dt_seconds,
            distance_to_target - stopping_radius_m,
        )
        herbivore.position = Position2D(
            x_m=herbivore.position.x_m + cos(heading) * travel_distance,
            y_m=herbivore.position.y_m + sin(heading) * travel_distance,
        )
        herbivore.heading_rad = heading
        return travel_distance

    @staticmethod
    def _feed(herbivore: Herbivore, target: Plant, dt_seconds: float) -> None:
        bite_kg = herbivore.feeding_rate_kg_per_s * dt_seconds
        food_needed_kg = (
            herbivore.max_energy_j - herbivore.energy_j
        ) / herbivore.food_energy_j_per_kg
        eaten_kg = min(bite_kg, target.edible_biomass_kg, food_needed_kg)
        target.edible_biomass_kg = max(0.0, target.edible_biomass_kg - eaten_kg)
        herbivore.energy_j = min(
            herbivore.max_energy_j,
            herbivore.energy_j + eaten_kg * herbivore.food_energy_j_per_kg,
        )

    @staticmethod
    def _drink(herbivore: Herbivore, source: WaterSource, dt_seconds: float) -> None:
        potential_drink_kg = herbivore.drinking_rate_kg_per_s * dt_seconds
        needed_kg = herbivore.max_body_water_kg - herbivore.body_water_kg
        drunk_kg = min(potential_drink_kg, source.water_kg, needed_kg)
        source.water_kg = max(0.0, source.water_kg - drunk_kg)
        herbivore.body_water_kg = min(
            herbivore.max_body_water_kg,
            herbivore.body_water_kg + drunk_kg,
        )

    @staticmethod
    def _pay_movement_cost(herbivore: Herbivore, distance_travelled_m: float) -> None:
        movement_cost_j = distance_travelled_m * herbivore.movement_energy_j_per_m
        herbivore.energy_j = max(0.0, herbivore.energy_j - movement_cost_j)


def create_uniform_herbivores(
    *,
    rng: SeededRNG,
    bounds: WorldBounds,
    count: int,
    speed_m_per_s: float,
    perception_radius_m: float,
    feeding_radius_m: float,
    feeding_rate_kg_per_s: float,
    body_water_kg: float,
    max_body_water_kg: float,
    water_loss_kg_per_s: float,
    drinking_rate_kg_per_s: float,
    drinking_radius_m: float,
    energy_j: float,
    max_energy_j: float,
    basal_power_w: float,
    movement_energy_j_per_m: float,
    food_energy_j_per_kg: float,
    age_s: float,
    lifespan_s: float,
    recoverable_nutrient_kg: float,
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
                heading_rad=rng.random() * TAU,
                speed_m_per_s=speed_m_per_s,
                perception_radius_m=perception_radius_m,
                feeding_radius_m=feeding_radius_m,
                feeding_rate_kg_per_s=feeding_rate_kg_per_s,
                body_water_kg=body_water_kg,
                max_body_water_kg=max_body_water_kg,
                water_loss_kg_per_s=water_loss_kg_per_s,
                drinking_rate_kg_per_s=drinking_rate_kg_per_s,
                drinking_radius_m=drinking_radius_m,
                energy_j=energy_j,
                max_energy_j=max_energy_j,
                basal_power_w=basal_power_w,
                movement_energy_j_per_m=movement_energy_j_per_m,
                food_energy_j_per_kg=food_energy_j_per_kg,
                age_s=age_s,
                lifespan_s=lifespan_s,
                recoverable_nutrient_kg=recoverable_nutrient_kg,
            )
        )
    return tuple(herbivores)
