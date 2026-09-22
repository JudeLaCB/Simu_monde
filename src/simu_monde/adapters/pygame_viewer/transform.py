"""Pure world-meter to screen-pixel transformations for the Pygame adapter."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from simu_monde.core.geometry import Position2D, WorldBounds


@dataclass(frozen=True, slots=True)
class PixelViewport:
    """The letterboxed pixel rectangle used to render the logical world."""

    left_px: float
    top_px: float
    width_px: float
    height_px: float

    @property
    def right_px(self) -> float:
        """The horizontal coordinate of the viewport's right edge."""
        return self.left_px + self.width_px

    @property
    def bottom_px(self) -> float:
        """The vertical coordinate of the viewport's bottom edge."""
        return self.top_px + self.height_px


@dataclass(frozen=True, slots=True)
class WorldToScreenTransform:
    """Map meter-based world positions to a centered, aspect-preserving viewport.

    The logical world origin is bottom-left. Screen Y is inverted here because
    the Pygame display origin is top-left.
    """

    bounds: WorldBounds
    viewport_width_px: int
    viewport_height_px: int
    padding_px: float = 0.0

    def __post_init__(self) -> None:
        if (
            isinstance(self.viewport_width_px, bool)
            or not isinstance(self.viewport_width_px, int)
            or self.viewport_width_px <= 0
        ):
            raise ValueError("viewport_width_px must be a positive integer")
        if (
            isinstance(self.viewport_height_px, bool)
            or not isinstance(self.viewport_height_px, int)
            or self.viewport_height_px <= 0
        ):
            raise ValueError("viewport_height_px must be a positive integer")
        if (
            isinstance(self.padding_px, bool)
            or not isfinite(self.padding_px)
            or self.padding_px < 0
        ):
            raise ValueError("padding_px must be a finite, non-negative number")
        if self.padding_px * 2 >= self.viewport_width_px:
            raise ValueError("padding_px leaves no horizontal drawing area")
        if self.padding_px * 2 >= self.viewport_height_px:
            raise ValueError("padding_px leaves no vertical drawing area")

    @property
    def scale_px_per_m(self) -> float:
        """The uniform scale applied to both world axes."""
        drawable_width = self.viewport_width_px - 2 * self.padding_px
        drawable_height = self.viewport_height_px - 2 * self.padding_px
        return min(drawable_width / self.bounds.width_m, drawable_height / self.bounds.height_m)

    @property
    def world_viewport(self) -> PixelViewport:
        """Return the centered pixel rectangle allocated to the whole world."""
        width_px = self.bounds.width_m * self.scale_px_per_m
        height_px = self.bounds.height_m * self.scale_px_per_m
        left_px = (self.viewport_width_px - width_px) / 2
        top_px = (self.viewport_height_px - height_px) / 2
        return PixelViewport(
            left_px=left_px,
            top_px=top_px,
            width_px=width_px,
            height_px=height_px,
        )

    def to_screen(self, position: Position2D) -> tuple[float, float]:
        """Map a world position to pixels without changing or clamping it."""
        world_viewport = self.world_viewport
        return (
            world_viewport.left_px + position.x_m * self.scale_px_per_m,
            world_viewport.bottom_px - position.y_m * self.scale_px_per_m,
        )
