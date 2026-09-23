"""Interactive Pygame viewer that reads the simulation core through its public API."""

from __future__ import annotations

from simu_monde.adapters.pygame_viewer.transform import WorldToScreenTransform
from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import WorldBounds
from simu_monde.core.herbivore import create_uniform_herbivores
from simu_monde.core.randomness import SeededRNG
from simu_monde.core.simulation import Simulation
from simu_monde.core.vegetation import PlantGrowthSystem, create_uniform_plants
from simu_monde.core.water import (
    EvaporationSystem,
    RainfallSystem,
    WaterState,
    create_uniform_water_sources,
)
from simu_monde.core.world import World

WINDOW_SIZE_PX = (1000, 700)
WORLD_PADDING_PX = 24.0


class ViewerController:
    """Keep adapter UI timing separate from fixed-timestep core transitions."""

    def __init__(self, simulation: Simulation) -> None:
        self._simulation = simulation
        self._is_running = False
        self._elapsed_seconds = 0.0

    @property
    def is_running(self) -> bool:
        """Whether adapter-side continuous run mode is active."""
        return self._is_running

    def toggle_running(self) -> None:
        """Toggle adapter-side run/pause without directly changing clock data."""
        self._is_running = not self._is_running

    def step_once(self) -> None:
        """Advance exactly one fixed core tick only while paused."""
        if not self._is_running:
            self._simulation.step()

    def update(self, elapsed_seconds: float) -> None:
        """Advance fixed core ticks from elapsed adapter time while running."""
        if not self._is_running:
            return
        if elapsed_seconds < 0:
            raise ValueError("elapsed_seconds must not be negative")

        self._elapsed_seconds += elapsed_seconds
        dt_seconds = self._simulation.world.clock.dt_seconds
        while self._elapsed_seconds >= dt_seconds:
            self._simulation.step()
            self._elapsed_seconds -= dt_seconds


def create_default_simulation() -> Simulation:
    """Build the approved scenario with one seeded plant-then-herbivore placement stream."""
    config = SimulationConfig(dt_seconds=0.1, seed=42)
    placement_rng = SeededRNG(config.seed)
    bounds = WorldBounds(config.width_m, config.height_m)
    plants = create_uniform_plants(
        rng=placement_rng,
        bounds=bounds,
        count=100,
        initial_biomass_kg=0.5,
        max_biomass_kg=1.0,
        growth_rate_kg_per_s=0.02,
    )
    herbivores = create_uniform_herbivores(
        rng=placement_rng,
        bounds=bounds,
        count=12,
        hunger=0.60,
        speed_m_per_s=15.0,
        perception_radius_m=150.0,
        feeding_radius_m=8.0,
        hunger_rate_per_s=0.003,
        feeding_rate_kg_per_s=0.05,
        food_capacity_kg=0.25,
        seek_food_hunger_threshold=0.35,
        body_water_kg=0.70,
        max_body_water_kg=1.00,
        water_loss_kg_per_s=0.002,
        drinking_rate_kg_per_s=0.05,
        drinking_radius_m=8.0,
        drink_thirst_threshold=0.35,
    )
    water_sources = create_uniform_water_sources(
        rng=placement_rng,
        bounds=bounds,
        count=3,
        water_kg_per_source=40.0,
    )
    water = WaterState(
        atmosphere_water_kg=200.0,
        soil_water_kg=120.0,
        surface_sources=water_sources,
    )
    world = World(config, plants=plants, herbivores=herbivores, water_state=water)
    return Simulation(
        world,
        rainfall_system=RainfallSystem(rain_rate_kg_per_s=0.10, soil_fraction=0.50),
        plant_growth_system=PlantGrowthSystem(water_kg_per_biomass_kg=0.20),
        evaporation_system=EvaporationSystem(
            soil_evaporation_rate_kg_per_s=0.05,
            surface_evaporation_rate_kg_per_s_per_source=0.02,
        ),
    )


def main() -> int:
    """Open the resizable viewer and return an ordinary process exit code."""
    import pygame

    from simu_monde.adapters.pygame_viewer.renderer import render

    simulation = create_default_simulation()
    controller = ViewerController(simulation)

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE_PX, pygame.RESIZABLE)
    pygame.display.set_caption("SimuMonde")
    render_clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    window_is_open = True

    try:
        while window_is_open:
            elapsed_seconds = render_clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    window_is_open = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    controller.toggle_running()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    controller.step_once()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            controller.update(elapsed_seconds)
            width_px, height_px = screen.get_size()
            transform = WorldToScreenTransform(
                bounds=simulation.world.bounds,
                viewport_width_px=width_px,
                viewport_height_px=height_px,
                padding_px=WORLD_PADDING_PX,
            )
            render(
                screen=screen,
                font=font,
                transform=transform,
                plants=simulation.world.plants,
                herbivores=simulation.world.herbivores,
                water=simulation.world.water,
                total_water_kg=simulation.world.total_water_kg,
                animal_body_water_kg=sum(
                    herbivore.body_water_kg for herbivore in simulation.world.herbivores
                ),
                tick_index=simulation.world.clock.tick_index,
                time_seconds=simulation.world.clock.time_seconds,
                is_running=controller.is_running,
            )
            pygame.display.flip()
    finally:
        pygame.quit()

    return 0
