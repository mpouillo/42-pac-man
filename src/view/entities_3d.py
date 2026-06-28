"""Pac-Man, pacgum, and ghost rendering for the 3D scene."""
# mypy: disable-error-code=attr-defined

from typing import Any

import pyray as ray

from src.constants import (
    ENTITY_MODEL_DIR,
    ENTITY_MODEL_FILES,
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    MODEL_EXTENSION,
    PACGUM_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
)
from src.types.dataclasses import GhostData
from src.types.enums import CellState, Direction, GhostState, GhostType
from src.view.entity_motion import entity_rotation

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

    def _draw_3d_pacgum_at(
        self,
        position: Any,
        is_super: bool = False,
    ) -> None:
        """Draw one 3D pacgum or super pacgum."""
        model_key = "super_pacgum" if is_super else "pacgum"
        self._draw_entity_model(
            model_key,
            position,
            PACGUM_MODEL_SCALE,
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
        if pacman.direction != Direction.NONE:
            self._last_pacman_direction = pacman.direction

        rotation_axis, rotation_angle = entity_rotation(
            self._last_pacman_direction,
            ray.get_time(),
        )

        self._draw_entity_model(
            "pacman",
            position,
            PACMAN_MODEL_SCALE,
            rotation_axis,
            rotation_angle,
        )

    def _draw_3d_ghost(
        self,
        ghost: GhostData,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one ghost in 3D."""
        model_key = self._ghost_model_key(ghost)
        position = self._grid_to_world(
            ghost.x,
            ghost.y,
            grid,
            GHOST_MODEL_HEIGHT,
        )
        offset_x, offset_z = GHOST_VISUAL_OFFSETS[ghost.type]
        position.x += offset_x
        position.z += offset_z

        rotation_axis, rotation_angle = entity_rotation(
            ghost.direction,
            ray.get_time(),
        )

        self._draw_entity_model(
            model_key,
            position,
            GHOST_MODEL_SCALE,
            rotation_axis,
            rotation_angle,
        )

    def _ghost_model_key(self, ghost: GhostData) -> str:
        """Return the model key for a ghost."""
        if ghost.state == GhostState.EATEN:
            return "ghost_respawn"

        if ghost.state in (GhostState.FRIGHTENED, GhostState.FLASHING):
            return "ghost_frightened"

        return GHOST_MODEL_KEYS[ghost.type]

    def _draw_entity_model(
        self,
        model_key: str,
        position: Any,
        scale: float,
        rotation_axis: Any | None = None,
        rotation_angle: float = 0.0,
    ) -> None:
        """Draw one loaded entity model with uniform scale."""
        if rotation_axis is None:
            rotation_axis = ray.Vector3(0.0, 1.0, 0.0)

        ray.draw_model_ex(
            self._entity_models[model_key],
            position,
            rotation_axis,
            rotation_angle,
            ray.Vector3(scale, scale, scale),
            ray.WHITE,
        )
