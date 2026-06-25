"""Animated 3D chase backdrop for the main menu."""

import math
from dataclasses import dataclass
from typing import Any

import pyray as ray

from src.constants import (
    ENTITY_SWAY_DEGREES,
    ENTITY_SWAY_SPEED,
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
)
from src.types.enums import Direction

DIRECTION_ROTATIONS = {
    Direction.DOWN: 0.0,
    Direction.NONE: 0.0,
    Direction.RIGHT: 90.0,
    Direction.UP: 180.0,
    Direction.LEFT: 270.0,
}
MENU_CHASE_CAMERA_WORLD_HEIGHT = 8.4
MENU_CHASE_PACMAN_SCALE = PACMAN_MODEL_SCALE * 0.62
MENU_CHASE_GHOST_SCALE = GHOST_MODEL_SCALE * 0.62
MENU_CHASE_Z = 3.35
MENU_CHASE_LEFT = -9.35
MENU_CHASE_RIGHT = 9.35
MENU_CHASE_SPEED = 2.1
MENU_CHASE_RUN_GAP = 1.1
MENU_CHASE_PACMAN_GAP = 1.35
MENU_CHASE_FIRST_GHOST_OFFSET = 1.55
MENU_CHASE_GHOST_SPACING = 0.62
MENU_CHASE_PACMAN_BOB_SPEED = 5.5
MENU_CHASE_GHOST_BOB_SPEED = 4.2
MENU_CHASE_GHOSTS = (
    "ghost_red",
    "ghost_pink",
    "ghost_cyan",
    "ghost_orange",
)


@dataclass(frozen=True)
class PathSample:
    """Position and facing direction sampled from a chase track."""

    x: float
    z: float
    direction: Direction
    visible: bool


class MenuChaseScene:
    """Draw a real 3D animated chase scene behind the main menu."""

    def __init__(self, models: dict[str, Any]) -> None:
        """Store shared entity models and initialize the menu camera."""
        self._models = models
        self._elapsed = 0.0
        self._camera: Any = ray.Camera3D(
            ray.Vector3(0.0, 7.6, 7.2),
            ray.Vector3(0.0, 0.0, 0.0),
            ray.Vector3(0.0, 1.0, 0.0),
            MENU_CHASE_CAMERA_WORLD_HEIGHT,
            ray.CameraProjection.CAMERA_ORTHOGRAPHIC,
        )

    def update(self, delta_time: float) -> None:
        """Advance the menu-only animation clock."""
        self._elapsed += delta_time

    def draw(self, window_width: int, window_height: int) -> None:
        """Draw the chase scene directly to the current framebuffer."""
        if window_width <= 0 or window_height <= 0:
            return

        self._update_camera_size(window_width, window_height)

        ray.begin_mode_3d(self._camera)
        self._draw_chase_train()
        ray.end_mode_3d()

    def _update_camera_size(
        self,
        window_width: int,
        window_height: int,
    ) -> None:
        """Keep the orthographic view stable across window sizes."""
        aspect_ratio = window_width / window_height
        width_based_height = 15.4 / aspect_ratio
        self._camera.fovy = max(
            MENU_CHASE_CAMERA_WORLD_HEIGHT,
            width_based_height,
        )

    def _draw_chase_train(self) -> None:
        """Draw the alternating ghost-chase and Pac-Man-chase trains."""
        segment_distance = self._elapsed * MENU_CHASE_SPEED
        track_length = abs(MENU_CHASE_RIGHT - MENU_CHASE_LEFT)
        run_length = track_length + MENU_CHASE_RUN_GAP
        cycle_position = segment_distance % (run_length * 2.0)

        if cycle_position < run_length:
            self._draw_ghosts_chasing_pacman(cycle_position)
        else:
            self._draw_pacman_chasing_ghosts(cycle_position - run_length)

    def _draw_ghosts_chasing_pacman(self, distance: float) -> None:
        """Draw four ghosts chasing Pac-Man from left to right."""
        pacman = self._sample_line(
            MENU_CHASE_LEFT,
            MENU_CHASE_RIGHT,
            distance,
        )

        for index in range(len(MENU_CHASE_GHOSTS) - 1, -1, -1):
            ghost_offset = (
                MENU_CHASE_FIRST_GHOST_OFFSET
                + index * MENU_CHASE_GHOST_SPACING
            )
            ghost = self._sample_line(
                MENU_CHASE_LEFT,
                MENU_CHASE_RIGHT,
                distance - ghost_offset,
            )
            self._draw_ghost(
                ghost,
                MENU_CHASE_GHOSTS[index],
                index * 0.55,
            )

        self._draw_pacman(pacman)

    def _draw_pacman_chasing_ghosts(self, distance: float) -> None:
        """Draw Pac-Man chasing four ghosts from right to left."""
        for index in range(len(MENU_CHASE_GHOSTS) - 1, -1, -1):
            ghost = self._sample_line(
                MENU_CHASE_RIGHT,
                MENU_CHASE_LEFT,
                distance - index * MENU_CHASE_GHOST_SPACING,
            )
            self._draw_ghost(
                ghost,
                MENU_CHASE_GHOSTS[index],
                1.2 + index * 0.55,
            )

        pacman_offset = MENU_CHASE_PACMAN_GAP
        pacman_offset += (
            (len(MENU_CHASE_GHOSTS) - 1)
            * MENU_CHASE_GHOST_SPACING
        )
        pacman = self._sample_line(
            MENU_CHASE_RIGHT,
            MENU_CHASE_LEFT,
            distance - pacman_offset,
        )
        self._draw_pacman(pacman)

    def _draw_pacman(self, sample: PathSample) -> None:
        """Draw one menu Pac-Man using the loaded gameplay model."""
        if not sample.visible:
            return

        bob = math.sin(
            self._elapsed * MENU_CHASE_PACMAN_BOB_SPEED + sample.x
        )
        position = ray.Vector3(
            sample.x,
            PACMAN_MODEL_HEIGHT + bob * 0.025,
            sample.z,
        )
        rotation_axis, rotation_angle = self._entity_rotation(
            sample.direction
        )

        ray.draw_model_ex(
            self._models["pacman"],
            position,
            rotation_axis,
            rotation_angle,
            ray.Vector3(
                MENU_CHASE_PACMAN_SCALE,
                MENU_CHASE_PACMAN_SCALE,
                MENU_CHASE_PACMAN_SCALE,
            ),
            ray.WHITE,
        )

    def _draw_ghost(
        self,
        sample: PathSample,
        model_key: str,
        phase: float,
    ) -> None:
        """Draw one menu ghost using the loaded gameplay model."""
        if not sample.visible:
            return

        bob = math.sin(
            self._elapsed * MENU_CHASE_GHOST_BOB_SPEED + phase
        )
        rotation_axis, rotation_angle = self._entity_rotation(
            sample.direction
        )
        position = ray.Vector3(
            sample.x,
            GHOST_MODEL_HEIGHT + bob * 0.035,
            sample.z,
        )

        ray.draw_model_ex(
            self._models[model_key],
            position,
            rotation_axis,
            rotation_angle,
            ray.Vector3(
                MENU_CHASE_GHOST_SCALE,
                MENU_CHASE_GHOST_SCALE,
                MENU_CHASE_GHOST_SCALE,
            ),
            ray.WHITE,
        )

    def _entity_rotation(self, direction: Direction) -> tuple[Any, float]:
        """Return shared facing plus left/right turn sway for menu entities."""
        base_angle = DIRECTION_ROTATIONS.get(direction, 0.0)
        sway = (
            math.sin(self._elapsed * ENTITY_SWAY_SPEED)
            * ENTITY_SWAY_DEGREES
        )
        return (
            ray.Vector3(0.0, 1.0, 0.0),
            base_angle + sway,
        )

    def _sample_line(
        self,
        start_x: float,
        end_x: float,
        distance: float,
    ) -> PathSample:
        """Return a non-wrapping sample on one visible line segment."""
        delta_x = end_x - start_x
        visible_length = abs(delta_x)
        direction = (
            Direction.RIGHT if end_x > start_x else Direction.LEFT
        )

        if visible_length == 0.0 or distance < 0.0:
            return PathSample(
                start_x,
                MENU_CHASE_Z,
                direction,
                False,
            )

        if distance > visible_length:
            return PathSample(
                end_x,
                MENU_CHASE_Z,
                direction,
                False,
            )

        amount = distance / visible_length
        return PathSample(
            start_x + delta_x * amount,
            MENU_CHASE_Z,
            direction,
            True,
        )
