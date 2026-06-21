"""Camera FOV helpers for the 3D scene."""

from typing import Any

from src.constants import (
    AUTO_FOV_PADDING,
    AUTO_FOV_SCALE,
    FOV_MAX,
    FOV_MIN,
    FOV_SPEED,
)
from src.types.enums import CellState


class FovRendererMixin:
    """Update automatic and keyboard-controlled camera FOV."""

    _window_width: int
    _window_height: int
    _fov: float
    _auto_fov_enabled: bool
    _camera: Any

    def calculate_auto_fov(self, grid: list[list[CellState]]) -> float:
        """Calculate a FOV that fits the current maze size."""
        if not grid or not grid[0]:
            return self._fov

        if self._window_height <= 0:
            return self._fov

        rows = len(grid)
        cols = len(grid[0])
        aspect_ratio = self._window_width / self._window_height
        maze_size = max(rows, cols / aspect_ratio)
        return maze_size * AUTO_FOV_SCALE + AUTO_FOV_PADDING

    def reset_fov(self) -> None:
        """Enable automatic FOV for a new game."""
        self._auto_fov_enabled = True

    def update_fov(
        self,
        grid: list[list[CellState]],
        increase: bool,
        decrease: bool,
        delta_time: float,
    ) -> None:
        """Update automatic or keyboard-controlled camera FOV."""
        if increase or decrease:
            self._auto_fov_enabled = False

        if self._auto_fov_enabled:
            self._fov = self.calculate_auto_fov(grid)

        if increase:
            self._fov += FOV_SPEED * delta_time
        if decrease:
            self._fov -= FOV_SPEED * delta_time

        self._fov = max(FOV_MIN, min(FOV_MAX, self._fov))
        self._camera.fovy = self._fov
