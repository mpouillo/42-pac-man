"""Pac-Man, pacgum, and ghost rendering for the 3D scene."""

import math
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pyray as ray

from src.constants import (
    ENTITY_MODEL_DIR,
    ENTITY_MODEL_EXTENSION,
    ENTITY_MODEL_FILES,
    GHOST_BLUE_TILT_PHASE,
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    GHOST_ORANGE_TILT_PHASE,
    GHOST_PINK_TILT_PHASE,
    GHOST_RED_TILT_PHASE,
    GHOST_TILT_DEGREES,
    GHOST_TILT_SPEED,
    PACGUM_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
    RESPAWN_GHOST_TILT_DEGREES,
    RESPAWN_GHOST_TILT_SPEED,
)
from src.types.dataclasses import GhostData
from src.types.enums import CellState, Direction, GhostState, GhostType


class Entity3DRendererMixin:
    """Load and draw gameplay entity models."""

    _entity_models: dict[str, Any]
    _grid_to_world: Callable[
        [float, float, list[list[CellState]], float],
        Any,
    ]
    _load_model_asset: Callable[[Path, str, str], Any]

    def _load_entity_models(self) -> None:
        """Load Pac-Man, pacgum, and ghost models once."""
        self._entity_models.clear()

        for model_key, base_name in ENTITY_MODEL_FILES.items():
            model = self._load_model_asset(
                ENTITY_MODEL_DIR,
                base_name,
                ENTITY_MODEL_EXTENSION,
            )
            self._entity_models[model_key] = model

    def _unload_entity_models(self) -> None:
        """Unload all entity models."""
        for model in self._entity_models.values():
            ray.unload_model(model)

        self._entity_models.clear()

    def _draw_3d_pacgum(
        self,
        grid_x: int,
        grid_y: int,
        grid: list[list[CellState]],
        height: float,
        is_super: bool = False,
    ) -> None:
        """Draw one 3D pacgum or super pacgum."""
        model_key = "super_pacgum" if is_super else "pacgum"
        model = self._entity_models[model_key]
        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            height,
        )

        ray.draw_model_ex(
            model,
            position,
            ray.Vector3(0.0, 1.0, 0.0),
            0.0,
            ray.Vector3(
                PACGUM_MODEL_SCALE,
                PACGUM_MODEL_SCALE,
                PACGUM_MODEL_SCALE,
            ),
            ray.WHITE,
        )

    def _draw_3d_pacman(
        self,
        pacman: Any,
        grid: list[list[CellState]],
    ) -> None:
        """Draw Pac-Man in 3D."""
        model = self._entity_models["pacman"]

        position = self._grid_to_world(
            pacman.x,
            pacman.y,
            grid,
            PACMAN_MODEL_HEIGHT,
        )

        ray.draw_model_ex(
            model,
            position,
            ray.Vector3(0.0, 1.0, 0.0),
            self._direction_to_rotation(pacman.direction),
            ray.Vector3(
                PACMAN_MODEL_SCALE,
                PACMAN_MODEL_SCALE,
                PACMAN_MODEL_SCALE,
            ),
            ray.WHITE,
        )

    def _draw_3d_ghost(
        self,
        ghost: GhostData,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one ghost in 3D."""
        model_key = self._ghost_model_key(ghost)
        model = self._entity_models[model_key]
        position = self._grid_to_world(
            ghost.x,
            ghost.y,
            grid,
            GHOST_MODEL_HEIGHT,
        )

        rotation_axis, rotation_angle = self._ghost_rotation(ghost)

        ray.draw_model_ex(
            model,
            position,
            rotation_axis,
            rotation_angle,
            ray.Vector3(
                GHOST_MODEL_SCALE,
                GHOST_MODEL_SCALE,
                GHOST_MODEL_SCALE,
            ),
            ray.WHITE,
        )

    def _ghost_model_key(self, ghost: GhostData) -> str:
        """Return the model key for a ghost."""
        if ghost.state == GhostState.EATEN:
            return "ghost_respawn"

        if ghost.state in (GhostState.FRIGHTENED, GhostState.FLASHING):
            return "ghost_cyan"

        match ghost.type:
            case GhostType.RED:
                return "ghost_red"
            case GhostType.PINK:
                return "ghost_pink"
            case GhostType.BLUE:
                return "ghost_cyan"
            case GhostType.ORANGE:
                return "ghost_orange"
        raise ValueError(f"Unsupported ghost type: {ghost.type}")

    def _ghost_rotation(self, ghost: GhostData) -> tuple[Any, float]:
        """Return one axis-angle rotation combining facing and runtime tilt."""
        facing_angle = self._direction_to_rotation(ghost.direction)

        if ghost.state == GhostState.EATEN:
            tilt_angle = self._respawn_ghost_tilt(ghost)
        else:
            tilt_angle = self._ghost_tilt(ghost)

        return self._combined_yaw_roll_rotation(facing_angle, tilt_angle)

    def _ghost_tilt(self, ghost: GhostData) -> float:
        """Return smooth left/right tilt for a normal ghost."""
        return (
            math.sin(
                ray.get_time() * GHOST_TILT_SPEED + self._ghost_phase(ghost)
            )
            * GHOST_TILT_DEGREES
        )

    def _respawn_ghost_tilt(self, ghost: GhostData) -> float:
        """Return a quicker tilt for the dashed respawn ghost."""
        return (
            math.sin(
                ray.get_time() * RESPAWN_GHOST_TILT_SPEED
                + self._ghost_phase(ghost)
            )
            * RESPAWN_GHOST_TILT_DEGREES
        )

    def _ghost_phase(self, ghost: GhostData) -> float:
        """Return animation offset so ghosts do not sway together."""
        match ghost.type:
            case GhostType.RED:
                return GHOST_RED_TILT_PHASE
            case GhostType.PINK:
                return GHOST_PINK_TILT_PHASE
            case GhostType.BLUE:
                return GHOST_BLUE_TILT_PHASE
            case GhostType.ORANGE:
                return GHOST_ORANGE_TILT_PHASE
        return 0.0

    def _combined_yaw_roll_rotation(
        self,
        yaw_degrees: float,
        roll_degrees: float,
    ) -> tuple[Any, float]:
        """Combine direction yaw and local sideways tilt."""
        yaw = math.radians(yaw_degrees) / 2.0
        roll = math.radians(roll_degrees) / 2.0

        yaw_quaternion = (math.cos(yaw), 0.0, math.sin(yaw), 0.0)
        roll_quaternion = (math.cos(roll), 0.0, 0.0, math.sin(roll))

        w, x, y, z = self._multiply_quaternions(
            yaw_quaternion,
            roll_quaternion,
        )

        length = math.sqrt(w * w + x * x + y * y + z * z)
        if length == 0.0:
            return ray.Vector3(0.0, 1.0, 0.0), 0.0

        w /= length
        x /= length
        y /= length
        z /= length

        w = max(-1.0, min(1.0, w))
        angle = math.degrees(2.0 * math.acos(w))
        axis_scale = math.sqrt(max(0.0, 1.0 - w * w))

        if axis_scale < 0.0001:
            return ray.Vector3(0.0, 1.0, 0.0), 0.0

        return ray.Vector3(
            x / axis_scale,
            y / axis_scale,
            z / axis_scale,
        ), angle

    def _multiply_quaternions(
        self,
        first: tuple[float, float, float, float],
        second: tuple[float, float, float, float],
    ) -> tuple[float, float, float, float]:
        """Return first * second for quaternions stored as w, x, y, z."""
        first_w, first_x, first_y, first_z = first
        second_w, second_x, second_y, second_z = second

        return (
            first_w * second_w
            - first_x * second_x
            - first_y * second_y
            - first_z * second_z,
            first_w * second_x
            + first_x * second_w
            + first_y * second_z
            - first_z * second_y,
            first_w * second_y
            - first_x * second_z
            + first_y * second_w
            + first_z * second_x,
            first_w * second_z
            + first_x * second_y
            - first_y * second_x
            + first_z * second_w,
        )

    def _direction_to_rotation(self, direction: Direction) -> float:
        """Return model Y-axis rotation from entity direction."""
        match direction:
            case Direction.RIGHT:
                return 90.0
            case Direction.UP:
                return 180.0
            case Direction.LEFT:
                return 270.0
            case Direction.DOWN | Direction.NONE:
                return 0.0
        return 0.0
