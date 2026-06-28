"""3D maze, entity, asset, and HUD rendering."""
# mypy: disable-error-code="attr-defined"

import math
from pathlib import Path
from typing import Any

import pyray as ray

from src.constants import (
    AUTO_CAMERA_DISTANCE_PADDING,
    AUTO_FOV_FIT_HEIGHT,
    AUTO_FOV_WORLD_PADDING,
    CAMERA_POSITION,
    CAMERA_TARGET,
    CAMERA_UP,
    CELL_SIZE_3D,
    DEFAULT_FOV,
    FOV_MAX,
    FOV_MIN,
    FOV_SPEED,
    HUD_FONT_SIZE,
    HUD_HORIZONTAL_PADDING,
    HUD_TOP_OFFSET,
    MAZE_FLOOR_COLOR,
    MAZE_FLOOR_HEIGHT,
    MODEL_EXTENSION,
    TEXT_COLOR,
    WALL_MODEL_DIR,
    WALL_MODEL_FILE_PREFIX,
    WALL_MODEL_HEIGHT_SCALE,
    WALL_MODEL_THICKNESS_SCALE,
)
from src.types.enums import CellState
from src.types.protocols import ModelProtocol
from src.view.background import draw_arcade_background
from src.view.entities_3d import Entity3DRendererMixin
from src.view.wall_shapes import WallAssetKind, get_wall_asset_kind


class Scene3DRendererMixin(Entity3DRendererMixin):
    """Draw the game scene, HUD, and wall assets."""

    def _calculate_auto_camera_fit(
        self,
        grid: list[list[CellState]],
    ) -> tuple[float, float] | None:
        """Return a camera fit that keeps maze bounds inside the screen."""
        if (
            not grid
            or not grid[0]
            or self._window_width <= 0
            or self._window_height <= 0
        ):
            return None

        points = self._maze_bounds_points(grid)
        default_distance = math.dist(CAMERA_POSITION, CAMERA_TARGET)

        camera = self._camera_at_distance(default_distance, FOV_MIN)
        if camera is None:
            return None
        if self._maze_fits_on_screen(points, camera):
            return FOV_MIN, default_distance

        low_fov = FOV_MIN
        high_fov = FOV_MAX
        for _ in range(12):
            mid_fov = (low_fov + high_fov) / 2.0
            camera = self._camera_at_distance(default_distance, mid_fov)
            if camera is None:
                return None

            if self._maze_fits_on_screen(points, camera):
                high_fov = mid_fov
            else:
                low_fov = mid_fov

        fov = high_fov
        camera = self._camera_at_distance(default_distance, fov)
        if camera is not None and self._maze_fits_on_screen(points, camera):
            return fov, default_distance

        fov = FOV_MAX
        low_distance = default_distance
        high_distance = default_distance
        for _ in range(20):
            high_distance *= 1.25
            camera = self._camera_at_distance(high_distance, fov)
            if camera is None:
                return None

            if self._maze_fits_on_screen(points, camera):
                break
        else:
            return fov, high_distance

        for _ in range(12):
            mid_distance = (low_distance + high_distance) / 2.0
            camera = self._camera_at_distance(mid_distance, fov)
            if camera is None:
                return None

            if self._maze_fits_on_screen(points, camera):
                high_distance = mid_distance
            else:
                low_distance = mid_distance

        return fov, high_distance + AUTO_CAMERA_DISTANCE_PADDING

    def _maze_bounds_points(
        self,
        grid: list[list[CellState]],
    ) -> list[Any]:
        """Return world-space corners around the full maze bounds."""
        rows = len(grid)
        cols = len(grid[0])
        half_width = (
            cols / 2.0 + AUTO_FOV_WORLD_PADDING
        ) * CELL_SIZE_3D
        half_depth = (
            rows / 2.0 + AUTO_FOV_WORLD_PADDING
        ) * CELL_SIZE_3D

        return [
            ray.Vector3(x, y, z)
            for x in (-half_width, half_width)
            for y in (0.0, AUTO_FOV_FIT_HEIGHT)
            for z in (-half_depth, half_depth)
        ]

    def _maze_fits_on_screen(
        self,
        points: list[Any],
        camera: Any,
        margin: int = 40,
    ) -> bool:
        """Return whether all maze bound points project inside the viewport."""
        for point in points:
            screen = ray.get_world_to_screen(point, camera)
            if screen.x < margin:
                return False
            if screen.x > self._window_width - margin:
                return False
            if screen.y < margin:
                return False
            if screen.y > self._window_height - margin:
                return False

        return True

    def _camera_at_distance(
        self,
        distance: float,
        fov: float,
    ) -> Any | None:
        """Return a camera along its default target-to-position direction."""
        target = tuple(float(value) for value in CAMERA_TARGET)
        default_position = tuple(float(value) for value in CAMERA_POSITION)
        direction = (
            default_position[0] - target[0],
            default_position[1] - target[1],
            default_position[2] - target[2],
        )
        length = math.sqrt(
            direction[0] ** 2
            + direction[1] ** 2
            + direction[2] ** 2
        )
        if length <= 0.0:
            return None

        unit_direction = (
            direction[0] / length,
            direction[1] / length,
            direction[2] / length,
        )
        position = (
            target[0] + unit_direction[0] * distance,
            target[1] + unit_direction[1] * distance,
            target[2] + unit_direction[2] * distance,
        )

        return ray.Camera3D(
            ray.Vector3(*position),
            ray.Vector3(*target),
            ray.Vector3(*CAMERA_UP),
            fov,
            self._camera.projection,
        )

    def _set_camera_distance(
        self,
        distance: float,
    ) -> None:
        """Move the camera along its default target-to-position direction."""
        camera = self._camera_at_distance(distance, self._fov)
        if camera is None:
            return

        self._camera.position = camera.position
        self._camera.target = camera.target
        self._camera.up = camera.up

    def _reset_camera_position(self) -> None:
        """Restore the camera to its default position and target."""
        self._camera.position = ray.Vector3(*CAMERA_POSITION)
        self._camera.target = ray.Vector3(*CAMERA_TARGET)
        self._camera.up = ray.Vector3(*CAMERA_UP)

    def reset_fov(self) -> None:
        """Enable automatic FOV for a new game."""
        self._auto_fov_enabled = True
        self._fov = DEFAULT_FOV
        self._camera.fovy = self._fov
        self._reset_camera_position()

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
            camera_fit = self._calculate_auto_camera_fit(grid)
            if camera_fit is not None:
                self._fov, camera_distance = camera_fit
                self._set_camera_distance(camera_distance)

        if increase:
            self._fov += FOV_SPEED * delta_time
        if decrease:
            self._fov -= FOV_SPEED * delta_time

        self._fov = max(FOV_MIN, min(FOV_MAX, self._fov))
        self._camera.fovy = self._fov

    def _draw_game(self, model: ModelProtocol) -> None:
        """Draw gameplay screen."""
        self.screen_shake.update(ray.get_frame_time())
        draw_arcade_background(
            self._window_width,
            self._window_height,
            texture=self._background_texture,
        )

        grid = model.get_grid()
        pacman = model.get_pacman()
        ghosts = model.get_ghosts()
        camera = self._shake_camera()

        ray.begin_mode_3d(camera)
        self._draw_3d_grid(grid)
        self._draw_3d_pacman(pacman, grid)

        for ghost in ghosts:
            self._draw_3d_ghost(ghost, grid)

        ray.end_mode_3d()

        self._draw_hud(model)

    def _shake_camera(self) -> Any:
        """Return a temporary camera offset for 3D-world shake only."""
        if not self.screen_shake.is_active():
            return self._camera

        offset_x = self.screen_shake.offset_x
        offset_z = self.screen_shake.offset_z
        return ray.Camera3D(
            ray.Vector3(
                self._camera.position.x + offset_x,
                self._camera.position.y,
                self._camera.position.z + offset_z,
            ),
            ray.Vector3(
                self._camera.target.x + offset_x,
                self._camera.target.y,
                self._camera.target.z + offset_z,
            ),
            ray.Vector3(
                self._camera.up.x,
                self._camera.up.y,
                self._camera.up.z,
            ),
            self._camera.fovy,
            self._camera.projection,
        )

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

    def _load_wall_models(self) -> None:
        """Load all wall models once."""
        self._wall_models.clear()

        for asset_kind in WallAssetKind:
            base_name = f"{WALL_MODEL_FILE_PREFIX}{asset_kind.value}"
            model = self._load_model_asset(
                WALL_MODEL_DIR,
                base_name,
                MODEL_EXTENSION,
            )
            bounds = ray.get_model_bounding_box(model)
            self._wall_models[asset_kind] = (model, bounds)

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

    def _draw_3d_wall(
        self,
        grid_x: int,
        grid_y: int,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one 3D wall block."""
        asset_kind = get_wall_asset_kind(grid, grid_x, grid_y)
        model, bounds = self._wall_models[asset_kind]

        position = self._grid_to_world(
            float(grid_x),
            float(grid_y),
            grid,
            -bounds.min.y * WALL_MODEL_HEIGHT_SCALE,
        )
        scale_x, scale_z = self._wall_thickness_scale(asset_kind)
        ray.draw_model_ex(
            model,
            position,
            ray.Vector3(0.0, 1.0, 0.0),
            0.0,
            ray.Vector3(
                scale_x,
                WALL_MODEL_HEIGHT_SCALE,
                scale_z,
            ),
            ray.WHITE,
        )

    def _wall_thickness_scale(
        self,
        asset_kind: WallAssetKind,
    ) -> tuple[float, float]:
        """Return X/Z scale for thickness without opening seams."""
        if asset_kind == WallAssetKind.ISOLATED:
            return WALL_MODEL_THICKNESS_SCALE, WALL_MODEL_THICKNESS_SCALE

        if asset_kind in (
            WallAssetKind.END_UP,
            WallAssetKind.END_DOWN,
            WallAssetKind.STRAIGHT_VERTICAL,
        ):
            return WALL_MODEL_THICKNESS_SCALE, 1.0

        if asset_kind in (
            WallAssetKind.END_LEFT,
            WallAssetKind.END_RIGHT,
            WallAssetKind.STRAIGHT_HORIZONTAL,
        ):
            return 1.0, WALL_MODEL_THICKNESS_SCALE

        return 1.0, 1.0

    def _draw_3d_grid(
        self,
        grid: list[list[CellState]],
    ) -> None:
        """Draw the floor, walls, and pacgums in the 3D maze."""
        self._draw_3d_floor(grid)

        _wall_model, wall_bounds = next(iter(self._wall_models.values()))
        pacgum_height = (
            wall_bounds.max.y - wall_bounds.min.y
        ) * WALL_MODEL_HEIGHT_SCALE / 2

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == CellState.WALL:
                    self._draw_3d_wall(x, y, grid)

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell in (CellState.PACGUM, CellState.SUPER_PACGUM):
                    self._draw_3d_pacgum_at(
                        self._grid_to_world(
                            float(x),
                            float(y),
                            grid,
                            pacgum_height,
                        ),
                        is_super=cell == CellState.SUPER_PACGUM,
                    )

    def _draw_3d_floor(
        self,
        grid: list[list[CellState]],
    ) -> None:
        """Draw one floor slab under the whole maze."""
        if not grid or not grid[0]:
            return

        rows = len(grid)
        cols = len(grid[0])
        if rows < 2 or cols < 2:
            return

        floor_width = (cols - 1) * CELL_SIZE_3D
        floor_depth = (rows - 1) * CELL_SIZE_3D
        floor_center = ray.Vector3(
            0.0,
            -MAZE_FLOOR_HEIGHT / 2.0,
            0.0,
        )

        ray.draw_cube(
            floor_center,
            floor_width,
            MAZE_FLOOR_HEIGHT,
            floor_depth,
            MAZE_FLOOR_COLOR,
        )

    def _draw_hud(self, model: ModelProtocol) -> None:
        """Draw score, lives, level, and timer."""
        time_left = max(0, int(model.get_remaining_time()))
        level = model.get_current_level() + 1

        left_text = (
            f"FOV: {int(self._fov)}   Level: {level}   Time: {time_left}"
        )
        right_text = f"Score: {model.get_score()}   Lives: {model.get_lives()}"

        ray.draw_text(
            left_text,
            HUD_HORIZONTAL_PADDING,
            HUD_TOP_OFFSET,
            HUD_FONT_SIZE,
            TEXT_COLOR,
        )

        width = ray.measure_text(right_text, HUD_FONT_SIZE)
        ray.draw_text(
            right_text,
            self._window_width - width - HUD_HORIZONTAL_PADDING,
            HUD_TOP_OFFSET,
            HUD_FONT_SIZE,
            TEXT_COLOR,
        )
