"""Pac-Man, pacgum, and ghost rendering for the 3D scene."""
# mypy: disable-error-code=attr-defined

import math
from typing import Any

import pyray as ray

from src.constants import (
    ENTITY_MODEL_DIR,
    ENTITY_MODEL_FILES,
    ENTITY_SWAY_DEGREES,
    ENTITY_SWAY_SPEED,
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    MODEL_EXTENSION,
    PACGUM_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
)
from src.types.dataclasses import GhostData
from src.types.enums import CellState, Direction, GhostState, GhostType

DIRECTION_ROTATIONS = {
    Direction.DOWN: 0.0,
    Direction.NONE: 0.0,
    Direction.RIGHT: 90.0,
    Direction.UP: 180.0,
    Direction.LEFT: 270.0,
}
GHOST_VISUAL_OFFSETS = {
    GhostType.RED: (0.15, -0.08),
    GhostType.PINK: (0.05, 0.08),
    GhostType.BLUE: (-0.05, -0.08),
    GhostType.ORANGE: (-0.15, 0.08),
}
GHOST_MODEL_KEYS = {
    GhostType.RED: "ghost_red",
    GhostType.PINK: "ghost_pink",
    GhostType.BLUE: "ghost_cyan",
    GhostType.ORANGE: "ghost_orange",
}


class Entity3DRendererMixin:
    """Load and draw gameplay entity models."""

    def _load_entity_models(self) -> None:
        """Load Pac-Man, pacgum, and ghost models once."""
        self._entity_models.clear()

        for model_key, base_name in ENTITY_MODEL_FILES.items():
            model = self._load_model_asset(
                ENTITY_MODEL_DIR,
                base_name,
                MODEL_EXTENSION,
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
        position = self._grid_to_world(
            pacman.x,
            pacman.y,
            grid,
            PACMAN_MODEL_HEIGHT,
        )
        direction = self._pacman_display_direction(pacman.direction)
        rotation_axis, rotation_angle = self._entity_rotation(direction)

        ray.draw_model_ex(
            self._entity_models["pacman"],
            position,
            rotation_axis,
            rotation_angle,
            ray.Vector3(
                PACMAN_MODEL_SCALE,
                PACMAN_MODEL_SCALE,
                PACMAN_MODEL_SCALE,
            ),
            ray.WHITE,
        )

    def _pacman_display_direction(self, direction: Direction) -> Direction:
        """Keep Pac-Man facing the last movement direction when stopped."""
        if direction != Direction.NONE:
            self._last_pacman_direction = direction

        return self._last_pacman_direction

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
        offset_x, offset_z = GHOST_VISUAL_OFFSETS[ghost.type]
        position.x += offset_x
        position.z += offset_z

        rotation_axis, rotation_angle = self._entity_rotation(ghost.direction)

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
            return "ghost_frightened"

        return GHOST_MODEL_KEYS[ghost.type]

    def _entity_rotation(self, direction: Direction) -> tuple[Any, float]:
        """Return shared facing plus left/right turn sway for entities."""
        base_angle = DIRECTION_ROTATIONS.get(direction, 0.0)
        sway = (
            math.sin(ray.get_time() * ENTITY_SWAY_SPEED)
            * ENTITY_SWAY_DEGREES
        )
        return (
            ray.Vector3(0.0, 1.0, 0.0),
            base_angle + sway,
        )
