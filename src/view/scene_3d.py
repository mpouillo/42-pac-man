"""3D maze, entity, asset, and HUD rendering."""

from typing import Any

import pyray as ray

from src.types.dataclasses import GhostData
from src.types.enums import CellState, Direction, GhostState, GhostType
from src.types.protocols import ModelProtocol
from src.view.constants import (
    AUTO_FOV_PADDING,
    AUTO_FOV_SCALE,
    BOARD_BACKGROUND,
    CONTENT_FONT_SIZE,
    FLASHING_COLOR,
    FOV_MAX,
    FOV_MIN,
    FOV_SPEED,
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
    ENTITY_MODEL_DIR,
    ENTITY_MODEL_EXTENSIONS,
    ENTITY_MODEL_FILES,
    GHOST_MODEL_SCALE,
    PACGUM_MODEL_SCALE,
    PACMAN_MODEL_SCALE,
)
from src.view.wall_shapes import (
    WallAssetKind,
    get_wall_asset_kind,
)


class Scene3DRendererMixin:
    """Draw the game scene, HUD, and wall assets."""

    _window_width: int
    _window_height: int
    _cell_size_3d: float
    _wall_height_3d: float
    _fov: float
    _auto_fov_enabled: bool
    _camera: Any
    _wall_models: dict[WallAssetKind, Any]
    _entity_models: dict[str, Any]

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

    def _load_entity_models(self) -> None:
        """Load Pac-Man, pacgum, and ghost models once."""
        self._entity_models.clear()

        for model_key, base_name in ENTITY_MODEL_FILES.items():
            model = self._load_entity_asset(base_name)

            if model is not None:
                self._entity_models[model_key] = model

    def _load_entity_asset(self, base_name: str) -> Any | None:
        """Load one entity model using the first available extension."""
        for extension in ENTITY_MODEL_EXTENSIONS:
            path = ENTITY_MODEL_DIR / f"{base_name}{extension}"

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

    def _unload_entity_models(self) -> None:
        """Unload all entity models."""
        for model in self._entity_models.values():
            ray.unload_model(model)

        self._entity_models.clear()

    def _draw_3d_wall(
        self,
        grid_x: int,
        grid_y: int,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one 3D wall block."""
        asset_kind = get_wall_asset_kind(grid, grid_x, grid_y)

        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            self._wall_height_3d / 2.0,
        )
        self._draw_3d_wall_shape(position, asset_kind)

    def _draw_3d_wall_shape(
        self,
        position: Any,
        asset_kind: WallAssetKind,
    ) -> None:
        """Draw one wall shape."""
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

        ray.draw_model_ex(
            model,
            model_position,
            ray.Vector3(0.0, 1.0, 0.0),
            0.0,
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
            self._draw_sphere_at(
                float(grid_x),
                float(grid_y),
                grid,
                0.23,
                SUPER_PACGUM_COLOR,
                self._wall_height_3d / 2,
            )
            return

        model = self._entity_models.get("pacgum")
        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            self._wall_height_3d / 2,
        )

        if model is None:
            ray.draw_sphere(position, 0.13, PACGUM_COLOR)
            return

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
        model = self._entity_models.get("pacman")
        position = self._grid_to_world(pacman.x, pacman.y, grid, 0.35)

        if model is None:
            ray.draw_sphere(position, 0.35, PACMAN_COLOR)
            return

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
        if ghost.state == GhostState.EATEN:
            return

        model_key = self._ghost_model_key(ghost)
        model = self._entity_models.get(model_key)
        position = self._grid_to_world(ghost.x, ghost.y, grid, 0.36)

        if model is None:
            ray.draw_sphere(position, 0.35, self._get_ghost_color(ghost))
            return

        ray.draw_model_ex(
            model,
            position,
            ray.Vector3(0.0, 1.0, 0.0),
            self._direction_to_rotation(ghost.direction),
            ray.Vector3(
                GHOST_MODEL_SCALE,
                GHOST_MODEL_SCALE,
                GHOST_MODEL_SCALE,
            ),
            ray.WHITE,
        )

    def _ghost_model_key(self, ghost: GhostData) -> str:
        """Return the model key for a ghost."""
        if ghost.state in (GhostState.FRIGHTENED, GhostState.FLASHING):
            return "ghost_cyan"

        keys = {
            GhostType.RED: "ghost_red",
            GhostType.PINK: "ghost_pink",
            GhostType.BLUE: "ghost_cyan",
            GhostType.ORANGE: "ghost_orange",
        }

        return keys.get(ghost.type, "ghost_red")

    def _direction_to_rotation(self, direction: Direction) -> float:
        """Return model Y-axis rotation from entity direction."""
        rotations = {
            Direction.DOWN: 0.0,
            Direction.RIGHT: 90.0,
            Direction.UP: 180.0,
            Direction.LEFT: 270.0,
            Direction.NONE: 0.0,
        }

        return rotations.get(direction, 0.0)

    def _draw_sphere_at(
        self,
        grid_x: float,
        grid_y: float,
        grid: list[list[CellState]],
        radius: float,
        color: Any,
        height: float,
    ) -> None:
        """Draw a sphere at a grid position."""
        position = self._grid_to_world(grid_x, grid_y, grid, height)
        ray.draw_sphere(position, radius, color)

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
