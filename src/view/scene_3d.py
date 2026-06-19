"""3D maze, entity, asset, and HUD rendering."""

from typing import Any

import pyray as ray

from src.types.dataclasses import GhostData
from src.types.enums import CellState, GhostType
from src.types.protocols import ModelProtocol
from src.view.constants import (
    AUTO_FOV_PADDING,
    AUTO_FOV_SCALE,
    BOARD_BACKGROUND,
    CONTENT_FONT_SIZE,
    FLASHING_COLOR,
    FRIGHTENED_COLOR,
    PACGUM_COLOR,
    PACMAN_COLOR,
    SUPER_PACGUM_COLOR,
    TEXT_COLOR,
    WALL_COLOR,
    WALL_MODEL_DIR,
    WALL_MODEL_EXTENSIONS,
    WALL_MODEL_FILES,
    WALL_MODEL_SCALE,
)
from src.view.wall_shapes import (
    WALL_SHAPE_RENDER_INFO,
    WallAssetKind,
    WallShape,
    get_wall_shape,
)


class Scene3DRendererMixin:
    """Draw the game scene, HUD, and wall assets."""

    _window_width: int
    _window_height: int
    _cell_size_3d: float
    _wall_height_3d: float
    _fov: float
    _camera: Any
    _wall_models: dict[WallAssetKind, Any]

    def _draw_game(self, model: ModelProtocol) -> None:
        """Draw gameplay screen."""
        grid = model.get_grid()
        pacman = model.get_pacman()
        ghosts = model.get_ghosts()

        ray.begin_mode_3d(self._camera)
        self._draw_3d_floor(grid)
        self._draw_3d_grid(grid)
        self._draw_3d_pacman(pacman, grid)

        for ghost in ghosts:
            self._draw_3d_ghost(ghost, grid)

        ray.end_mode_3d()

        self._draw_hud(model)

    def _grid_to_world(
        self,
        grid_x: float,
        grid_y: float,
        grid: list[list[CellState]],
        height: float,
    ) -> Any:
        """Convert 2D grid coordinates to 3D world coordinates."""
        rows = len(grid)
        cols = len(grid[0])

        centered_x = grid_x - cols / 2.0 + 0.5
        centered_z = grid_y - rows / 2.0 + 0.5

        world_x = centered_x * self._cell_size_3d
        world_z = centered_z * self._cell_size_3d

        return ray.Vector3(world_x, height, world_z)

    def _draw_3d_floor(self, grid: list[list[CellState]]) -> None:
        """Draw the 3D floor under the maze."""
        if not grid or not grid[0]:
            return

        rows = len(grid)
        cols = len(grid[0])

        width = cols * self._cell_size_3d
        depth = rows * self._cell_size_3d

        ray.draw_plane(
            ray.Vector3(0.0, 0.0, 0.0),
            ray.Vector2(width, depth),
            BOARD_BACKGROUND,
        )

    def _load_wall_models(self) -> None:
        """Load all wall models once."""
        self._wall_models.clear()

        for asset_kind, base_name in WALL_MODEL_FILES.items():
            model = self._load_wall_asset(base_name)

            if model is not None:
                self._wall_models[asset_kind] = model

    def _load_wall_asset(self, base_name: str) -> Any | None:
        """Load one wall model using the first available extension."""
        for extension in WALL_MODEL_EXTENSIONS:
            path = WALL_MODEL_DIR / f"{base_name}{extension}"

            if not path.exists():
                continue

            try:
                return ray.load_model(str(path))
            except Exception:
                continue

        return None

    def _unload_wall_models(self) -> None:
        """Unload all wall models."""
        for model in self._wall_models.values():
            ray.unload_model(model)

        self._wall_models.clear()

    def _draw_3d_wall(
        self,
        grid_x: int,
        grid_y: int,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one 3D wall block."""
        shape = get_wall_shape(grid, grid_x, grid_y)

        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            self._wall_height_3d / 2.0,
        )
        self._draw_3d_wall_shape(position, shape)

    def _draw_3d_wall_shadow(
        self,
        model: Any,
        position: Any,
        rotation: float,
    ) -> None:
        """Draw a fake flat shadow under the wall model."""
        shadow_position = ray.Vector3(
            position.x + 0.04,
            0.01,
            position.z + 0.04,
        )

        ray.draw_model_ex(
            model,
            shadow_position,
            ray.Vector3(0.0, 1.0, 0.0),
            rotation,
            ray.Vector3(
                WALL_MODEL_SCALE,
                0.04,
                WALL_MODEL_SCALE,
            ),
            ray.Color(0, 0, 0, 80),
        )

    def _draw_3d_wall_shape(
        self,
        position: Any,
        shape: WallShape,
    ) -> None:
        """Draw one wall shape."""
        asset_kind, rotation = WALL_SHAPE_RENDER_INFO[shape]
        model = self._wall_models.get(asset_kind)

        if model is None:
            ray.draw_cube(
                position,
                self._cell_size_3d,
                self._wall_height_3d,
                self._cell_size_3d,
                WALL_COLOR,
            )
            return

        model_position = ray.Vector3(
            position.x,
            position.y,
            position.z,
        )

        self._draw_3d_wall_shadow(model, model_position, rotation)

        ray.draw_model_ex(
            model,
            model_position,
            ray.Vector3(0.0, 1.0, 0.0),
            rotation,
            ray.Vector3(
                WALL_MODEL_SCALE,
                WALL_MODEL_SCALE,
                WALL_MODEL_SCALE,
            ),
            ray.WHITE,
        )

    def _draw_3d_pacgum(
        self,
        grid_x: int,
        grid_y: int,
        grid: list[list[CellState]],
        is_super: bool = False,
    ) -> None:
        """Draw one 3D pacgum or super pacgum."""
        if is_super:
            radius = 0.23
            color = SUPER_PACGUM_COLOR
        else:
            radius = 0.13
            color = PACGUM_COLOR

        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            self._wall_height_3d / 2,
        )

        ray.draw_sphere(position, radius, color)

    def _draw_3d_pacman(
        self,
        pacman: Any,
        grid: list[list[CellState]],
    ) -> None:
        """Draw Pac-Man in 3D."""
        radius = 0.35

        position = self._grid_to_world(
            pacman.x,
            pacman.y,
            grid,
            radius,
        )

        ray.draw_sphere(
            position,
            radius,
            PACMAN_COLOR,
        )

    def _draw_3d_ghost(
        self,
        ghost: GhostData,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one ghost in 3D."""
        radius = 0.35

        position = self._grid_to_world(
            ghost.x,
            ghost.y,
            grid,
            radius,
        )

        ray.draw_sphere(
            position,
            radius,
            self._get_ghost_color(ghost),
        )

    def _get_ghost_color(self, ghost: GhostData) -> Any:
        """Return ghost color according to type and state."""
        if ghost.state.name == "FRIGHTENED":
            return FRIGHTENED_COLOR

        if ghost.state.name == "FLASHING":
            return FLASHING_COLOR

        colors = {
            GhostType.PINK: ray.Color(255, 120, 200, 255),
            GhostType.RED: ray.Color(255, 40, 40, 255),
            GhostType.ORANGE: ray.Color(255, 150, 40, 255),
            GhostType.BLUE: ray.Color(40, 220, 255, 255),
        }

        return colors.get(ghost.type, TEXT_COLOR)

    def _draw_3d_grid(
        self,
        grid: list[list[CellState]],
    ) -> None:
        """Draw walls and pacgums in the 3D maze."""
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == CellState.WALL:
                    self._draw_3d_wall(x, y, grid)
                elif cell == CellState.PACGUM:
                    self._draw_3d_pacgum(x, y, grid)
                elif cell == CellState.SUPER_PACGUM:
                    self._draw_3d_pacgum(x, y, grid, is_super=True)

    def _draw_hud(self, model: ModelProtocol) -> None:
        """Draw score, lives, level, and timer."""
        time_left = max(0, int(model.get_remaining_time()))
        level = model.get_current_level() + 1

        left_text = f"Score: {model.get_score()}   Lives: {model.get_lives()}"
        right_text = (
            f"FOV: {int(self._fov)}   Level: {level}   Time: {time_left}"
        )

        ray.draw_text(left_text, 24, 22, CONTENT_FONT_SIZE, TEXT_COLOR)

        width = ray.measure_text(right_text, CONTENT_FONT_SIZE)
        ray.draw_text(
            right_text,
            self._window_width - width - 24,
            22,
            CONTENT_FONT_SIZE,
            TEXT_COLOR,
        )

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
