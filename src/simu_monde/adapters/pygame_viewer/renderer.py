"""Pygame primitive rendering for the world viewer."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from simu_monde.adapters.pygame_viewer.transform import WorldToScreenTransform
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.vegetation import Plant
from simu_monde.core.water import WaterState

BACKGROUND_COLOR = (24, 28, 36)
WORLD_BORDER_COLOR = (205, 215, 230)
PLANT_COLOR = (94, 201, 157)
HERBIVORE_COLOR = (242, 174, 73)
WATER_SOURCE_COLOR = (65, 155, 245)
TEXT_COLOR = (245, 245, 245)
PLANT_RADIUS_PX = 6
HERBIVORE_RADIUS_PX = 8
WATER_SOURCE_RADIUS_PX = 10


def render(
    screen: pygame.Surface,
    font: pygame.font.Font,
    transform: WorldToScreenTransform,
    plants: Sequence[Plant],
    herbivores: Sequence[Herbivore],
    water: WaterState,
    total_water_kg: float,
    animal_body_water_kg: float,
    tick_index: int,
    time_seconds: float,
    is_running: bool,
) -> None:
    """Draw core plants, herbivores, water sources, and read-only water metrics."""
    screen.fill(BACKGROUND_COLOR)
    world_viewport = transform.world_viewport
    world_rect = pygame.Rect(
        round(world_viewport.left_px),
        round(world_viewport.top_px),
        round(world_viewport.width_px),
        round(world_viewport.height_px),
    )
    pygame.draw.rect(screen, WORLD_BORDER_COLOR, world_rect, width=2)

    for plant in plants:
        screen_position = transform.to_screen(plant.position)
        pygame.draw.circle(
            screen,
            PLANT_COLOR,
            (round(screen_position[0]), round(screen_position[1])),
            PLANT_RADIUS_PX,
        )

    for herbivore in herbivores:
        screen_position = transform.to_screen(herbivore.position)
        pygame.draw.circle(
            screen,
            HERBIVORE_COLOR,
            (round(screen_position[0]), round(screen_position[1])),
            HERBIVORE_RADIUS_PX,
        )

    for source in water.surface_sources:
        screen_position = transform.to_screen(source.position)
        pygame.draw.circle(
            screen,
            WATER_SOURCE_COLOR,
            (round(screen_position[0]), round(screen_position[1])),
            WATER_SOURCE_RADIUS_PX,
        )

    state_label = "running" if is_running else "paused"
    status_text = font.render(
        f"Tick: {tick_index}   Time: {time_seconds:.2f} s   State: {state_label}",
        True,
        TEXT_COLOR,
    )
    controls_text = font.render(
        "Space: run/pause   Right Arrow: single step while paused",
        True,
        TEXT_COLOR,
    )
    surface_water_kg = sum(source.water_kg for source in water.surface_sources)
    water_text = font.render(
        f"Total water: {total_water_kg:.2f} kg   "
        f"Atmosphere: {water.atmosphere_water_kg:.2f} kg   "
        f"Soil: {water.soil_water_kg:.2f} kg",
        True,
        TEXT_COLOR,
    )
    accessible_water_text = font.render(
        f"Surface: {surface_water_kg:.2f} kg   Animal body water: {animal_body_water_kg:.2f} kg",
        True,
        TEXT_COLOR,
    )
    screen.blit(status_text, (16, 14))
    screen.blit(controls_text, (16, 42))
    screen.blit(water_text, (16, 70))
    screen.blit(accessible_water_text, (16, 98))
