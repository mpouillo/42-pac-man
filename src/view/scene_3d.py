"""3D maze, entity, asset, and HUD rendering."""

from pathlib import Path
from typing import Any

import pyray as ray

from src.constants import (
    CELL_SIZE_3D,
    HUD_FONT_SIZE,
    HUD_HORIZONTAL_PADDING,
    HUD_TOP_OFFSET,
    TEXT_COLOR,
    WALL_MODEL_DIR,
    WALL_MODEL_EXTENSION,
    WALL_MODEL_FILE_PREFIX,
    WALL_MODEL_HEIGHT_SCALE,
    WALL_MODEL_THICKNESS_SCALE,
)
from src.types.enums import CellState
from src.types.protocols import ModelProtocol
from src.view.background import draw_arcade_background
from src.view.entities_3d import Entity3DRendererMixin
from src.view.fov import FovRendererMixin
from src.view.screen_shake import ScreenShake
from src.view.wall_shapes import WallAssetKind, get_wall_asset_kind


class Scene3DRendererMixin(Entity3DRendererMixin, FovRendererMixin):
    """Draw the game scene, HUD, and wall assets."""

    _window_width: int
    _window_height: int
    _fov: float
    _auto_fov_enabled: bool
    _camera: Any
    _wall_models: dict[WallAssetKind, tuple[Any, Any]]
    _entity_models: dict[str, Any]
    _background_texture: Any | None
    screen_shake: ScreenShake

    def _draw_game(self, model: ModelProtocol) -> None:
        """Draw gameplay screen."""
        self.screen_shake.update(ray.get_frame_time())
        draw_arcade_background(
            self._window_width,
            self._window_height,
            mode="game",
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
                WALL_MODEL_EXTENSION,
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
