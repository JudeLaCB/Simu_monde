"""Pygame primitive rendering for the world viewer."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from simu_monde.adapters.pygame_viewer.transform import WorldToScreenTransform
from simu_monde.core.herbivore import Herbivore
from simu_monde.core.vegetation import Plant

BACKGROUND_COLOR = (24, 28, 36)
WORLD_BORDER_COLOR = (205, 215, 230)
PLANT_COLOR = (94, 201, 157)
HERBIVORE_COLOR = (242, 174, 73)
TEXT_COLOR = (245, 245, 245)
PLANT_RADIUS_PX = 6
HERBIVORE_RADIUS_PX = 8


def render(
    screen: pygame.Surface,
    font: pygame.font.Font,
    transform: WorldToScreenTransform,
    plants: Sequence[Plant],
    herbivores: Sequence[Herbivore],
    tick_index: int,
    time_seconds: float,
    is_running: bool,
) -> None:
    """Draw the world border, core plants, and minimal viewer UI."""
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
    screen.blit(status_text, (16, 14))
    screen.blit(controls_text, (16, 42))
