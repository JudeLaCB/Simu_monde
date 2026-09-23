"""Tests for the Pygame adapter without opening a window."""

from __future__ import annotations

import pygame
import pytest

from simu_monde.adapters.pygame_viewer.app import ViewerController, create_default_simulation
from simu_monde.adapters.pygame_viewer.renderer import (
    CARCASS_COLOR,
    HERBIVORE_COLOR,
    PLANT_COLOR,
    WATER_SOURCE_COLOR,
    render,
)
from simu_monde.adapters.pygame_viewer.transform import WorldToScreenTransform
from simu_monde.core.config import SimulationConfig
from simu_monde.core.geometry import Position2D, WorldBounds
from simu_monde.core.herbivore import Herbivore
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
    simulation = create_default_simulation()
    controller = ViewerController(simulation)
    initial_biomass = simulation.world.plants[0].edible_biomass_kg

    controller.step_once()

    assert simulation.world.clock.tick_index == 1
    assert simulation.world.clock.time_seconds == 0.1
    assert simulation.world.plants[0].edible_biomass_kg == pytest.approx(
        initial_biomass + 0.02 * 0.1
    )


def test_paused_viewer_does_not_advance_core_state() -> None:
    simulation = create_default_simulation()
    controller = ViewerController(simulation)
    biomass_before = tuple(plant.edible_biomass_kg for plant in simulation.world.plants)

    controller.update(elapsed_seconds=10.0)

    assert simulation.world.clock.tick_index == 0
    assert tuple(plant.edible_biomass_kg for plant in simulation.world.plants) == biomass_before


def test_running_viewer_uses_fixed_core_ticks_and_pauses_cleanly() -> None:
    simulation = Simulation(World(SimulationConfig(dt_seconds=0.1, seed=42)))
    controller = ViewerController(simulation)
    controller.toggle_running()

    controller.update(elapsed_seconds=0.25)
    controller.toggle_running()
    controller.update(elapsed_seconds=10.0)

    assert simulation.world.clock.tick_index == 2
    assert simulation.world.clock.time_seconds == 0.2


def test_render_update_frequency_does_not_change_core_trajectory() -> None:
    def make_simulation() -> Simulation:
        herbivore = Herbivore(
            herbivore_id=0,
            position=Position2D(50.0, 25.0),
            heading_rad=0.5,
            speed_m_per_s=1.0,
            perception_radius_m=0.0,
            feeding_radius_m=0.0,
            feeding_rate_kg_per_s=0.0,
            body_water_kg=1.0,
            max_body_water_kg=1.0,
            water_loss_kg_per_s=0.0,
            drinking_rate_kg_per_s=0.0,
            drinking_radius_m=0.0,
            energy_j=100.0,
            max_energy_j=100.0,
            basal_power_w=0.0,
            movement_energy_j_per_m=0.0,
            food_energy_j_per_kg=100.0,
            age_s=0.0,
            lifespan_s=100.0,
            recoverable_nutrient_kg=0.02,
        )
        return Simulation(
            World(
                SimulationConfig(
                    dt_seconds=0.25,
                    seed=42,
                    width_m=100.0,
                    height_m=50.0,
                ),
                herbivores=(herbivore,),
            )
        )

    frequent_simulation = make_simulation()
    infrequent_simulation = make_simulation()
    frequent = ViewerController(frequent_simulation)
    infrequent = ViewerController(infrequent_simulation)
    frequent.toggle_running()
    infrequent.toggle_running()

    for _ in range(4):
        frequent.update(elapsed_seconds=0.25)
    infrequent.update(elapsed_seconds=1.0)

    frequent_world = frequent_simulation.world
    infrequent_world = infrequent_simulation.world
    assert frequent_world.clock.tick_index == infrequent_world.clock.tick_index == 4
    assert frequent_world.herbivores[0].position == infrequent_world.herbivores[0].position
    assert frequent_world.herbivores[0].heading_rad == infrequent_world.herbivores[0].heading_rad


def test_default_viewer_scenario_contains_deterministic_core_plants() -> None:
    first = create_default_simulation()
    second = create_default_simulation()

    assert len(first.world.plants) == 100
    assert [plant.plant_id for plant in first.world.plants] == list(range(100))
    assert [plant.position for plant in first.world.plants] == [
        plant.position for plant in second.world.plants
    ]
    assert all(first.world.bounds.contains(plant.position) for plant in first.world.plants)
    assert all(plant.edible_biomass_kg == 0.5 for plant in first.world.plants)
    assert all(plant.max_edible_biomass_kg == 1.0 for plant in first.world.plants)
    assert all(plant.growth_rate_kg_per_s == 0.02 for plant in first.world.plants)


def test_default_viewer_scenario_contains_deterministic_core_herbivores() -> None:
    first = create_default_simulation()
    second = create_default_simulation()

    assert len(first.world.herbivores) == 12
    assert [item.herbivore_id for item in first.world.herbivores] == list(range(12))
    assert [(item.position, item.heading_rad) for item in first.world.herbivores] == [
        (item.position, item.heading_rad) for item in second.world.herbivores
    ]
    assert all(first.world.bounds.contains(item.position) for item in first.world.herbivores)


def test_renderer_draws_real_core_plants_and_herbivores() -> None:
    simulation = create_default_simulation()
    surface = pygame.Surface((1000, 700))
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    transform = WorldToScreenTransform(
        bounds=simulation.world.bounds,
        viewport_width_px=1000,
        viewport_height_px=700,
        padding_px=24.0,
    )

    render(
        screen=surface,
        font=font,
        transform=transform,
        plants=simulation.world.plants,
        herbivores=simulation.world.herbivores,
        carcasses=simulation.world.carcasses,
        water=simulation.world.water,
        total_water_kg=simulation.world.total_water_kg,
        animal_body_water_kg=sum(item.body_water_kg for item in simulation.world.herbivores),
        average_energy_fraction=sum(item.energy_fraction for item in simulation.world.herbivores)
        / len(simulation.world.herbivores),
        average_hydration_fraction=sum(1.0 - item.thirst for item in simulation.world.herbivores)
        / len(simulation.world.herbivores),
        tick_index=0,
        time_seconds=0.0,
        is_running=False,
    )

    plant_px = transform.to_screen(simulation.world.plants[0].position)
    herbivore_px = transform.to_screen(simulation.world.herbivores[0].position)
    water_source_px = transform.to_screen(simulation.world.water.surface_sources[0].position)
    assert surface.get_at((round(plant_px[0]), round(plant_px[1]))) == pygame.Color(
        *PLANT_COLOR, 255
    )
    assert surface.get_at((round(herbivore_px[0]), round(herbivore_px[1]))) == pygame.Color(
        *HERBIVORE_COLOR, 255
    )
    assert surface.get_at((round(water_source_px[0]), round(water_source_px[1]))) == pygame.Color(
        *WATER_SOURCE_COLOR, 255
    )


def test_default_viewer_scenario_has_deterministic_conserved_water() -> None:
    first = create_default_simulation()
    second = create_default_simulation()

    assert first.world.total_water_kg == pytest.approx(448.4)
    assert first.world.water.atmosphere_water_kg == 200.0
    assert first.world.water.soil_water_kg == 120.0
    assert len(first.world.water.surface_sources) == 3
    assert [source.position for source in first.world.water.surface_sources] == [
        source.position for source in second.world.water.surface_sources
    ]

    initial_total = first.world.total_water_kg
    for _ in range(100):
        first.step()
    assert first.world.total_water_kg == pytest.approx(initial_total, abs=1e-8)


def test_renderer_reads_real_carcass_and_metrics_without_mutating_core() -> None:
    simulation = create_default_simulation()
    simulation.world.herbivores[0].energy_j = 0.0
    simulation.step()
    carcass = simulation.world.carcasses[0]
    state_before = (
        tuple(
            (
                item.plant_id,
                item.position,
                item.edible_biomass_kg,
                item.age_s,
                item.lifespan_s,
            )
            for item in simulation.world.plants
        ),
        tuple(
            (
                item.herbivore_id,
                item.position,
                item.energy_j,
                item.body_water_kg,
                item.age_s,
                item.lifespan_s,
                item.homeostasis.food_integral_s,
                item.homeostasis.water_integral_s,
                item.homeostasis.previous_food_error,
                item.homeostasis.previous_water_error,
            )
            for item in simulation.world.herbivores
        ),
        tuple(
            (
                item.carcass_id,
                item.source_herbivore_id,
                item.position,
                item.death_cause,
                item.water_kg,
                item.recoverable_nutrient_kg,
                item.age_s,
            )
            for item in simulation.world.carcasses
        ),
    )
    surface = pygame.Surface((1000, 700))
    pygame.font.init()
    transform = WorldToScreenTransform(simulation.world.bounds, 1000, 700, 24.0)

    render(
        screen=surface,
        font=pygame.font.Font(None, 24),
        transform=transform,
        plants=simulation.world.plants,
        herbivores=simulation.world.herbivores,
        carcasses=simulation.world.carcasses,
        water=simulation.world.water,
        total_water_kg=simulation.world.total_water_kg,
        animal_body_water_kg=sum(item.body_water_kg for item in simulation.world.herbivores),
        average_energy_fraction=sum(item.energy_fraction for item in simulation.world.herbivores)
        / len(simulation.world.herbivores),
        average_hydration_fraction=sum(1.0 - item.thirst for item in simulation.world.herbivores)
        / len(simulation.world.herbivores),
        tick_index=simulation.world.clock.tick_index,
        time_seconds=simulation.world.clock.time_seconds,
        is_running=False,
    )

    carcass_px = transform.to_screen(carcass.position)
    assert surface.get_at((round(carcass_px[0]), round(carcass_px[1]))) == pygame.Color(
        *CARCASS_COLOR, 255
    )
    assert (
        tuple(
            (
                item.plant_id,
                item.position,
                item.edible_biomass_kg,
                item.age_s,
                item.lifespan_s,
            )
            for item in simulation.world.plants
        ),
        tuple(
            (
                item.herbivore_id,
                item.position,
                item.energy_j,
                item.body_water_kg,
                item.age_s,
                item.lifespan_s,
                item.homeostasis.food_integral_s,
                item.homeostasis.water_integral_s,
                item.homeostasis.previous_food_error,
                item.homeostasis.previous_water_error,
            )
            for item in simulation.world.herbivores
        ),
        tuple(
            (
                item.carcass_id,
                item.source_herbivore_id,
                item.position,
                item.death_cause,
                item.water_kg,
                item.recoverable_nutrient_kg,
                item.age_s,
            )
            for item in simulation.world.carcasses
        ),
    ) == state_before


def test_resize_does_not_mutate_plant_biomass() -> None:
    simulation = create_default_simulation()
    biomass_before = tuple(plant.edible_biomass_kg for plant in simulation.world.plants)

    WorldToScreenTransform(
        simulation.world.bounds,
        viewport_width_px=200,
        viewport_height_px=200,
    )
    WorldToScreenTransform(
        simulation.world.bounds,
        viewport_width_px=400,
        viewport_height_px=200,
    )

    assert tuple(plant.edible_biomass_kg for plant in simulation.world.plants) == biomass_before


def test_resize_does_not_mutate_herbivore_state() -> None:
    simulation = create_default_simulation()
    state_before = tuple(
        (item.position, item.energy_j, item.heading_rad) for item in simulation.world.herbivores
    )

    WorldToScreenTransform(simulation.world.bounds, 200, 200)
    WorldToScreenTransform(simulation.world.bounds, 400, 200)

    assert (
        tuple(
            (item.position, item.energy_j, item.heading_rad) for item in simulation.world.herbivores
        )
        == state_before
    )


def test_resize_and_render_do_not_mutate_water() -> None:
    simulation = create_default_simulation()
    water_before = (
        simulation.world.water.atmosphere_water_kg,
        simulation.world.water.soil_water_kg,
        tuple(source.water_kg for source in simulation.world.water.surface_sources),
        tuple(item.body_water_kg for item in simulation.world.herbivores),
    )
    surface = pygame.Surface((400, 300))
    pygame.font.init()
    render(
        screen=surface,
        font=pygame.font.Font(None, 24),
        transform=WorldToScreenTransform(simulation.world.bounds, 400, 300),
        plants=simulation.world.plants,
        herbivores=simulation.world.herbivores,
        carcasses=simulation.world.carcasses,
        water=simulation.world.water,
        total_water_kg=simulation.world.total_water_kg,
        animal_body_water_kg=sum(item.body_water_kg for item in simulation.world.herbivores),
        average_energy_fraction=sum(item.energy_fraction for item in simulation.world.herbivores)
        / len(simulation.world.herbivores),
        average_hydration_fraction=sum(1.0 - item.thirst for item in simulation.world.herbivores)
        / len(simulation.world.herbivores),
        tick_index=0,
        time_seconds=0.0,
        is_running=False,
    )

    assert (
        simulation.world.water.atmosphere_water_kg,
        simulation.world.water.soil_water_kg,
        tuple(source.water_kg for source in simulation.world.water.surface_sources),
        tuple(item.body_water_kg for item in simulation.world.herbivores),
    ) == water_before
