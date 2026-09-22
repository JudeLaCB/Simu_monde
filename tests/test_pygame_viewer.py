"""Tests for the Pygame adapter without opening a window."""

from __future__ import annotations

import pytest

from simu_monde.adapters.pygame_viewer.app import ViewerController
from simu_monde.adapters.pygame_viewer.transform import WorldToScreenTransform
from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.simulation import Simulation
from simu_monde.core.world import World


@pytest.fixture
def square_bounds() -> WorldBounds:
    return WorldBounds(width_m=100.0, height_m=100.0)


def test_transform_maps_origin_to_world_viewport_bottom_left(square_bounds: WorldBounds) -> None:
    transform = WorldToScreenTransform(square_bounds, viewport_width_px=200, viewport_height_px=200)

    assert transform.to_screen(Position2D(0.0, 0.0)) == (0.0, 200.0)


def test_transform_maps_top_right_corner_to_world_viewport_top_right(
    square_bounds: WorldBounds,
) -> None:
    transform = WorldToScreenTransform(square_bounds, viewport_width_px=200, viewport_height_px=200)

    assert transform.to_screen(Position2D(100.0, 100.0)) == (200.0, 0.0)


def test_transform_maps_center_to_world_viewport_center(square_bounds: WorldBounds) -> None:
    transform = WorldToScreenTransform(square_bounds, viewport_width_px=200, viewport_height_px=200)

    assert transform.to_screen(Position2D(50.0, 50.0)) == (100.0, 100.0)


def test_non_square_viewport_letterboxes_without_distorting_world(
    square_bounds: WorldBounds,
) -> None:
    transform = WorldToScreenTransform(square_bounds, viewport_width_px=300, viewport_height_px=200)

    assert transform.world_viewport.left_px == 50.0
    assert transform.world_viewport.top_px == 0.0
    assert transform.world_viewport.width_px == 200.0
    assert transform.world_viewport.height_px == 200.0
    assert transform.to_screen(Position2D(0.0, 0.0)) == (50.0, 200.0)
    assert transform.to_screen(Position2D(100.0, 100.0)) == (250.0, 0.0)


def test_non_square_world_uses_same_scale_for_each_axis() -> None:
    bounds = WorldBounds(width_m=200.0, height_m=100.0)
    transform = WorldToScreenTransform(bounds, viewport_width_px=300, viewport_height_px=300)

    assert transform.scale_px_per_m == 1.5
    assert transform.world_viewport.left_px == 0.0
    assert transform.world_viewport.top_px == 75.0
    assert transform.to_screen(Position2D(200.0, 100.0)) == (300.0, 75.0)


def test_transform_does_not_clamp_out_of_world_positions(square_bounds: WorldBounds) -> None:
    transform = WorldToScreenTransform(square_bounds, viewport_width_px=200, viewport_height_px=200)

    assert transform.to_screen(Position2D(-10.0, 110.0)) == (-20.0, -20.0)


def test_same_world_state_and_viewport_map_to_same_screen_coordinates(
    square_bounds: WorldBounds,
) -> None:
    first_transform = WorldToScreenTransform(
        square_bounds,
        viewport_width_px=200,
        viewport_height_px=200,
    )
    second_transform = WorldToScreenTransform(
        square_bounds,
        viewport_width_px=200,
        viewport_height_px=200,
    )
    position = Position2D(25.0, 75.0)

    assert first_transform.to_screen(position) == second_transform.to_screen(position)


def test_resize_changes_only_view_mapping_not_core_state() -> None:
    world = World(SimulationConfig(dt_seconds=0.1, seed=42, width_m=100.0, height_m=50.0))
    reference_world = World(SimulationConfig(dt_seconds=0.1, seed=42, width_m=100.0, height_m=50.0))
    simulation = Simulation(world)
    position = Position2D(50.0, 25.0)
    original_bounds = world.bounds
    original_config = world.config

    before_resize = WorldToScreenTransform(
        world.bounds,
        viewport_width_px=200,
        viewport_height_px=200,
    )
    after_resize = WorldToScreenTransform(
        world.bounds,
        viewport_width_px=400,
        viewport_height_px=200,
    )

    assert before_resize.to_screen(position) != after_resize.to_screen(position)
    assert world.bounds is original_bounds
    assert world.config is original_config
    assert simulation.world.clock.tick_index == 0
    assert world.rng.random() == reference_world.rng.random()


def test_single_step_advances_exactly_one_core_tick_while_paused() -> None:
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.1, seed=42)))
    controller = ViewerController(simulation)

    controller.step_once()

    assert simulation.world.clock.tick_index == 1
    assert simulation.world.clock.time_seconds == 0.1


def test_paused_viewer_does_not_advance_core_state() -> None:
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.1, seed=42)))
    controller = ViewerController(simulation)

    controller.update(elapsed_seconds=10.0)

    assert simulation.world.clock.tick_index == 0


def test_running_viewer_uses_fixed_core_ticks_and_pauses_cleanly() -> None:
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.1, seed=42)))
    controller = ViewerController(simulation)
    controller.toggle_running()

    controller.update(elapsed_seconds=0.25)
    controller.toggle_running()
    controller.update(elapsed_seconds=10.0)

    assert simulation.world.clock.tick_index == 2
    assert simulation.world.clock.time_seconds == 0.2
