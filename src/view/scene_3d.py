"""3D maze, entity, asset, and HUD rendering."""

import math
from pathlib import Path
from typing import Any

import pyray as ray

from src.constants import (
    AUTO_FOV_PADDING,
    AUTO_FOV_SCALE,
    BOARD_BACKGROUND,
    CELL_SIZE_3D,
    CONTENT_FONT_SIZE,
    ENTITY_MODEL_DIR,
    ENTITY_MODEL_EXTENSION,
    ENTITY_MODEL_FILES,
    FOV_MAX,
    FOV_MIN,
    FOV_SPEED,
    GHOST_BLUE_TILT_PHASE,
    GHOST_MODEL_HEIGHT,
    GHOST_MODEL_SCALE,
    GHOST_ORANGE_TILT_PHASE,
    GHOST_PINK_TILT_PHASE,
    GHOST_RED_TILT_PHASE,
    GHOST_TILT_DEGREES,
    GHOST_TILT_SPEED,
    HUD_HORIZONTAL_PADDING,
    HUD_TOP_OFFSET,
    PACGUM_MODEL_SCALE,
    PACMAN_MODEL_HEIGHT,
    PACMAN_MODEL_SCALE,
    RESPAWN_GHOST_TILT_DEGREES,
    RESPAWN_GHOST_TILT_SPEED,
    TEXT_COLOR,
    WALL_MODEL_DIR,
    WALL_MODEL_EXTENSION,
    WALL_MODEL_FILE_PREFIX,
    WALL_MODEL_HEIGHT_SCALE,
    WALL_MODEL_WIDTH_SCALE,
)
from src.types.dataclasses import GhostData
from src.types.enums import (
    CellState,
    Direction,
    GhostState,
    GhostType,
)
from src.types.protocols import ModelProtocol
from src.view.wall_shapes import WallAssetKind, get_wall_asset_kind


class Scene3DRendererMixin:
    """Draw the game scene, HUD, and wall assets."""

    _window_width: int
    _window_height: int
    _fov: float
    _auto_fov_enabled: bool
    _camera: Any
    _wall_models: dict[WallAssetKind, tuple[Any, Any]]
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

        world_x = centered_x * CELL_SIZE_3D
        world_z = centered_z * CELL_SIZE_3D

        return ray.Vector3(world_x, height, world_z)

    def _draw_3d_floor(self, grid: list[list[CellState]]) -> None:
        """Draw the 3D floor under the maze."""
        if not grid or not grid[0]:
            return

        rows = len(grid)
        cols = len(grid[0])

        width = cols * CELL_SIZE_3D
        depth = rows * CELL_SIZE_3D

        ray.draw_plane(
            ray.Vector3(0.0, 0.0, 0.0),
            ray.Vector2(width, depth),
            BOARD_BACKGROUND,
        )

    def _load_wall_models(self) -> None:
        """Load all wall models once."""
        self._wall_models.clear()

        for asset_kind in WallAssetKind:
            base_name = f"{WALL_MODEL_FILE_PREFIX}{asset_kind.value}"
            model = self._load_model_asset(
                WALL_MODEL_DIR,
                base_name,
                WALL_MODEL_EXTENSION,
            )
            bounds = ray.get_model_bounding_box(model)
            self._wall_models[asset_kind] = (model, bounds)

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

    def _load_model_asset(
        self,
        directory: Path,
        base_name: str,
        extension: str,
    ) -> Any:
        """Load one required model asset."""
        path = directory / f"{base_name}{extension}"

        if not path.exists():
            raise FileNotFoundError(f"Model asset not found: {path}")

        try:
            return ray.load_model(str(path))
        except Exception as error:
            raise RuntimeError(
                f"Could not load model asset: {path}"
            ) from error

    def _unload_wall_models(self) -> None:
        """Unload all wall models."""
        for model, _bounds in self._wall_models.values():
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
        _model, bounds = self._wall_models[asset_kind]

        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            -bounds.min.y * WALL_MODEL_HEIGHT_SCALE,
        )
        self._draw_3d_wall_shape(position, asset_kind)

    def _draw_3d_wall_shape(
        self,
        position: Any,
        asset_kind: WallAssetKind,
    ) -> None:
        """Draw one wall shape."""
        model, _bounds = self._wall_models[asset_kind]

        ray.draw_model_ex(
            model,
            position,
            ray.Vector3(0.0, 1.0, 0.0),
            0.0,
            ray.Vector3(
                WALL_MODEL_WIDTH_SCALE,
                WALL_MODEL_HEIGHT_SCALE,
                WALL_MODEL_WIDTH_SCALE,
            ),
            ray.WHITE,
        )

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

    def _draw_3d_grid(
        self,
        grid: list[list[CellState]],
    ) -> None:
        """Draw walls and pacgums in the 3D maze."""
        _wall_model, wall_bounds = next(iter(self._wall_models.values()))
        pacgum_height = (
            wall_bounds.max.y - wall_bounds.min.y
        ) * WALL_MODEL_HEIGHT_SCALE / 2

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == CellState.WALL:
                    self._draw_3d_wall(x, y, grid)
                elif cell == CellState.PACGUM:
                    self._draw_3d_pacgum(x, y, grid, pacgum_height)
                elif cell == CellState.SUPER_PACGUM:
                    self._draw_3d_pacgum(
                        x,
                        y,
                        grid,
                        pacgum_height,
                        is_super=True,
                    )

    def _draw_hud(self, model: ModelProtocol) -> None:
        """Draw score, lives, level, and timer."""
        time_left = max(0, int(model.get_remaining_time()))
        level = model.get_current_level() + 1

        left_text = f"Score: {model.get_score()}   Lives: {model.get_lives()}"
        right_text = (
            f"FOV: {int(self._fov)}   Level: {level}   Time: {time_left}"
        )

        ray.draw_text(
            left_text,
            HUD_HORIZONTAL_PADDING,
            HUD_TOP_OFFSET,
            CONTENT_FONT_SIZE,
            TEXT_COLOR,
        )

        width = ray.measure_text(right_text, CONTENT_FONT_SIZE)
        ray.draw_text(
            right_text,
            self._window_width - width - HUD_HORIZONTAL_PADDING,
            HUD_TOP_OFFSET,
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
