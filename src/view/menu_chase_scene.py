"""Animated 3D chase backdrop for the main menu."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pyray as ray

from src.constants import (
    ENTITY_SWAY_DEGREES,
    ENTITY_SWAY_SPEED,
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    PACGUM_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
)
from src.types.enums import Direction
from src.view.entity_orientation import (
    direction_from_delta,
    yaw_sway_rotation,
)

PathPoint = tuple[float, float]

MENU_CHASE_CAMERA_WORLD_HEIGHT = 8.4
MENU_CHASE_CAMERA_WORLD_WIDTH = 15.4
MENU_CHASE_PACMAN_SCALE = PACMAN_MODEL_SCALE * 0.62
MENU_CHASE_GHOST_SCALE = GHOST_MODEL_SCALE * 0.62
MENU_CHASE_PELLET_SCALE = PACGUM_MODEL_SCALE * 0.42
MENU_CHASE_SUPER_PELLET_SCALE = PACGUM_MODEL_SCALE * 0.58
MENU_CHASE_PELLET_HEIGHT = 0.12
MENU_CHASE_PELLET_Z = 3.35
MENU_CHASE_ENTITY_Z = MENU_CHASE_PELLET_Z
MENU_CHASE_PELLET_SPACING = 0.72
MENU_CHASE_PELLET_COUNT = 25
MENU_CHASE_TRACK_LEFT = -9.35
MENU_CHASE_TRACK_RIGHT = 9.35
MENU_CHASE_TRACK_SPEED = 2.1
MENU_CHASE_RUN_GAP = 1.1
MENU_CHASE_PACMAN_CHASE_GAP = 1.35
MENU_CHASE_FIRST_GHOST_OFFSET = 1.55
MENU_CHASE_GHOST_QUEUE_SPACING = 0.62
MENU_CHASE_PACMAN_BOB_SPEED = 5.5
MENU_CHASE_GHOST_BOB_SPEED = 4.2
MENU_CHASE_GHOST_QUEUE = (
    "ghost_red",
    "ghost_pink",
    "ghost_cyan",
    "ghost_orange",
)


@dataclass(frozen=True)
class ChaseTrack:
    """A single horizontal line used by the menu chase animation."""

    left: float
    right: float
    z: float
    speed: float
    gap: float


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
        self._track = ChaseTrack(
            MENU_CHASE_TRACK_LEFT,
            MENU_CHASE_TRACK_RIGHT,
            MENU_CHASE_ENTITY_Z,
            MENU_CHASE_TRACK_SPEED,
            MENU_CHASE_RUN_GAP,
        )
        self._pellet_positions = self._horizontal_pellet_positions()
        self._ghost_offsets = self._ghost_offsets_for_pacman_lead()
        self._required_model_keys = self._model_keys()

    def update(self, delta_time: float) -> None:
        """Advance the menu-only animation clock."""
        self._elapsed += delta_time

    def draw(self, window_width: int, window_height: int) -> None:
        """Draw the chase scene directly to the current framebuffer."""
        if window_width <= 0 or window_height <= 0:
            return
        if not self._has_required_models():
            return

        self._update_camera_size(window_width, window_height)

        ray.begin_mode_3d(self._camera)
        self._draw_pellets()
        self._draw_chase_train()
        ray.end_mode_3d()

    def _model_keys(self) -> set[str]:
        """Return all model keys needed by this scene."""
        return {
            "pacman",
            "pacgum",
            "super_pacgum",
            *MENU_CHASE_GHOST_QUEUE,
        }

    def _horizontal_pellet_positions(self) -> tuple[float, ...]:
        """Return centered horizontal pellet X positions."""
        center_index = (MENU_CHASE_PELLET_COUNT - 1) / 2.0
        return tuple(
            (index - center_index) * MENU_CHASE_PELLET_SPACING
            for index in range(MENU_CHASE_PELLET_COUNT)
        )

    def _ghost_offsets_for_pacman_lead(self) -> tuple[float, ...]:
        """Return queue offsets for ghosts chasing Pac-Man."""
        return tuple(
            MENU_CHASE_FIRST_GHOST_OFFSET
            + index * MENU_CHASE_GHOST_QUEUE_SPACING
            for index in range(len(MENU_CHASE_GHOST_QUEUE))
        )

    def _has_required_models(self) -> bool:
        """Return whether the shared entity model cache is ready."""
        return all(key in self._models for key in self._required_model_keys)

    def _update_camera_size(
        self,
        window_width: int,
        window_height: int,
    ) -> None:
        """Keep the orthographic view stable across window sizes."""
        aspect_ratio = window_width / window_height
        width_based_height = MENU_CHASE_CAMERA_WORLD_WIDTH / aspect_ratio
        self._camera.fovy = max(
            MENU_CHASE_CAMERA_WORLD_HEIGHT,
            width_based_height,
        )

    def _draw_pellets(self) -> None:
        """Draw one horizontal pellet line as pacgum, pacgum, super."""
        for index, x in enumerate(self._pellet_positions):
            self._draw_pellet(
                x,
                MENU_CHASE_PELLET_Z,
                is_super=index % 3 == 2,
            )

    def _draw_pellet(
        self,
        x: float,
        z: float,
        is_super: bool = False,
    ) -> None:
        """Draw one 3D pellet or super pellet model."""
        model_key = "super_pacgum" if is_super else "pacgum"
        scale = (
            MENU_CHASE_SUPER_PELLET_SCALE
            if is_super
            else MENU_CHASE_PELLET_SCALE
        )
        ray.draw_model_ex(
            self._models[model_key],
            ray.Vector3(x, MENU_CHASE_PELLET_HEIGHT, z),
            ray.Vector3(0.0, 1.0, 0.0),
            0.0,
            ray.Vector3(scale, scale, scale),
            ray.WHITE,
        )

    def _draw_chase_train(self) -> None:
        """Draw the alternating ghost-chase and Pac-Man-chase trains."""
        segment_distance = self._elapsed * self._track.speed
        track_length = self._track_length()
        run_length = track_length + self._track.gap
        cycle_position = segment_distance % (run_length * 2.0)

        if cycle_position < run_length:
            self._draw_ghosts_chasing_pacman(cycle_position)
        else:
            self._draw_pacman_chasing_ghosts(cycle_position - run_length)

    def _draw_ghosts_chasing_pacman(self, distance: float) -> None:
        """Draw four ghosts chasing Pac-Man from left to right."""
        start = (self._track.left, self._track.z)
        end = (self._track.right, self._track.z)
        pacman = self._sample_line(start, end, distance)

        for index in range(len(MENU_CHASE_GHOST_QUEUE) - 1, -1, -1):
            ghost = self._sample_line(
                start,
                end,
                distance - self._ghost_offsets[index],
            )
            self._draw_ghost(
                ghost,
                MENU_CHASE_GHOST_QUEUE[index],
                index * 0.55,
            )

        self._draw_pacman(pacman)

    def _draw_pacman_chasing_ghosts(self, distance: float) -> None:
        """Draw Pac-Man chasing four ghosts from right to left."""
        start = (self._track.right, self._track.z)
        end = (self._track.left, self._track.z)

        for index in range(len(MENU_CHASE_GHOST_QUEUE) - 1, -1, -1):
            ghost = self._sample_line(
                start,
                end,
                distance - index * MENU_CHASE_GHOST_QUEUE_SPACING,
            )
            self._draw_ghost(
                ghost,
                MENU_CHASE_GHOST_QUEUE[index],
                1.2 + index * 0.55,
            )

        pacman_offset = MENU_CHASE_PACMAN_CHASE_GAP
        pacman_offset += (
            (len(MENU_CHASE_GHOST_QUEUE) - 1)
            * MENU_CHASE_GHOST_QUEUE_SPACING
        )
        pacman = self._sample_line(start, end, distance - pacman_offset)
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
        return (
            ray.Vector3(0.0, 1.0, 0.0),
            yaw_sway_rotation(
                direction,
                self._elapsed,
                ENTITY_SWAY_SPEED,
                ENTITY_SWAY_DEGREES,
            ),
        )

    def _sample_line(
        self,
        start: PathPoint,
        end: PathPoint,
        distance: float,
    ) -> PathSample:
        """Return a non-wrapping sample on one visible line segment."""
        start_x, start_z = start
        end_x, end_z = end
        delta_x = end_x - start_x
        delta_z = end_z - start_z
        visible_length = math.hypot(delta_x, delta_z)
        direction = direction_from_delta(delta_x, delta_z)

        if visible_length == 0.0 or distance < 0.0:
            return PathSample(start_x, start_z, direction, False)

        if distance > visible_length:
            return PathSample(end_x, end_z, direction, False)

        amount = distance / visible_length
        return PathSample(
            start_x + delta_x * amount,
            start_z + delta_z * amount,
            direction,
            True,
        )

    def _track_length(self) -> float:
        """Return the visible length of the horizontal chase track."""
        return abs(self._track.right - self._track.left)
