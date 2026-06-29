"""Animated 3D chase backdrop for the main menu."""

import math
from typing import Any

import pyray as ray

from src.constants import (
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
)
from src.types.enums import Direction
from src.view.entity_motion import entity_rotation

MENU_CHASE_CAMERA_WORLD_HEIGHT = 8.4
MENU_CHASE_PACMAN_SCALE = PACMAN_MODEL_SCALE * 0.62
MENU_CHASE_GHOST_SCALE = GHOST_MODEL_SCALE * 0.62
MENU_CHASE_Z = 3.35
MENU_CHASE_TRACK_WIDTH_RATIO = 1.10
MENU_CHASE_SPEED = 2.1
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

        aspect_ratio = window_width / window_height
        width_based_height = 15.4 / aspect_ratio
        self._camera.fovy = max(
            MENU_CHASE_CAMERA_WORLD_HEIGHT,
            width_based_height,
        )
        visible_width = self._camera.fovy * aspect_ratio
        track_half_width = visible_width * MENU_CHASE_TRACK_WIDTH_RATIO / 2.0
        track_left = -track_half_width
        track_right = track_half_width

        ray.begin_mode_3d(self._camera)
        self._draw_chase_train(track_left, track_right)
        ray.end_mode_3d()

    def _draw_chase_train(
        self,
        track_left: float,
        track_right: float,
    ) -> None:
        """Draw the alternating ghost-chase and Pac-Man-chase trains."""
        segment_distance = self._elapsed * MENU_CHASE_SPEED
        track_length = abs(track_right - track_left)
        run_length = track_length + MENU_CHASE_GHOST_SPACING * 8
        cycle_position = segment_distance % (run_length * 2.0)

        if cycle_position < run_length:
            self._draw_chase_run(
                cycle_position,
                track_left,
                track_right,
                pacman_leads=True,
            )
        else:
            self._draw_chase_run(
                cycle_position - run_length,
                track_right,
                track_left,
                pacman_leads=False,
            )

    def _draw_chase_run(
        self,
        distance: float,
        start_x: float,
        end_x: float,
        pacman_leads: bool,
    ) -> None:
        """Draw one straight chase run in either direction."""
        ghost_start_offset = (
            MENU_CHASE_FIRST_GHOST_OFFSET if pacman_leads else 0.0
        )
        ghost_phase_offset = 0.0 if pacman_leads else 1.2
        pacman_offset = 0.0
        if not pacman_leads:
            pacman_offset = MENU_CHASE_PACMAN_GAP
            pacman_offset += (
                (len(MENU_CHASE_GHOSTS) - 1)
                * MENU_CHASE_GHOST_SPACING
            )

        for index in range(len(MENU_CHASE_GHOSTS) - 1, -1, -1):
            ghost_offset = (
                ghost_start_offset
                + index * MENU_CHASE_GHOST_SPACING
            )
            ghost = self._sample_line(
                start_x,
                end_x,
                distance - ghost_offset,
            )
            self._draw_ghost(
                ghost,
                MENU_CHASE_GHOSTS[index],
                ghost_phase_offset + index * 0.55,
            )

        pacman = self._sample_line(
            start_x,
            end_x,
            distance - pacman_offset,
        )
        self._draw_pacman(pacman)

    def _draw_pacman(
        self,
        sample: tuple[float, Direction] | None,
    ) -> None:
        """Draw one menu Pac-Man using the loaded gameplay model."""
        if sample is None:
            return

        x, direction = sample
        bob = math.sin(
            self._elapsed * MENU_CHASE_PACMAN_BOB_SPEED + x
        )
        position = ray.Vector3(
            x,
            PACMAN_MODEL_HEIGHT + bob * 0.025,
            MENU_CHASE_Z,
        )
        rotation_axis, rotation_angle = entity_rotation(
            direction,
            self._elapsed,
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
        sample: tuple[float, Direction] | None,
        model_key: str,
        phase: float,
    ) -> None:
        """Draw one menu ghost using the loaded gameplay model."""
        if sample is None:
            return

        x, direction = sample
        bob = math.sin(
            self._elapsed * MENU_CHASE_GHOST_BOB_SPEED + phase
        )
        rotation_axis, rotation_angle = entity_rotation(
            direction,
            self._elapsed,
        )
        position = ray.Vector3(
            x,
            GHOST_MODEL_HEIGHT + bob * 0.035,
            MENU_CHASE_Z,
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

    def _sample_line(
        self,
        start_x: float,
        end_x: float,
        distance: float,
    ) -> tuple[float, Direction] | None:
        """Return a non-wrapping sample on one visible line segment."""
        delta_x = end_x - start_x
        visible_length = abs(delta_x)
        direction = (
            Direction.RIGHT if end_x > start_x else Direction.LEFT
        )

        if visible_length == 0.0 or distance < 0.0:
            return None

        if distance > visible_length:
            return None

        amount = distance / visible_length
        return start_x + delta_x * amount, direction
