"""Raylib based 3D user interface for Pac-Man."""

from pathlib import Path
from typing import Any

import pyray as ray

from src.types.dataclasses import GhostData
from src.types.enums import CellState, GamePhase, GhostType
from src.types.protocols import ModelProtocol
from src.view.wall_shapes import (
    WALL_SHAPE_RENDER_INFO,
    WallAssetKind,
    WallShape,
    get_wall_shape,
)


BACKGROUND = ray.Color(5, 5, 20, 255)
BOARD_BACKGROUND = ray.Color(0, 0, 0, 255)
WALL_COLOR = ray.Color(20, 40, 180, 255)
PACGUM_COLOR = ray.Color(240, 220, 160, 255)
SUPER_PACGUM_COLOR = ray.Color(255, 255, 255, 255)
PACMAN_COLOR = ray.Color(255, 220, 0, 255)
TEXT_COLOR = ray.Color(240, 240, 240, 255)
MUTED_TEXT_COLOR = ray.Color(150, 150, 150, 255)
SELECTED_COLOR = ray.Color(255, 230, 0, 255)
OVERLAY_COLOR = ray.Color(0, 0, 0, 190)
FRIGHTENED_COLOR = ray.Color(40, 80, 255, 255)
FLASHING_COLOR = ray.Color(255, 255, 255, 255)

INFO_PAGE_START_Y_RATIO = 0.25
INFO_CONTENT_OFFSET = 100
MENU_ITEM_SPACING = 44
TITLE_FONT_SIZE = 48
CONTENT_FONT_SIZE = 30

AUTO_FOV_SCALE = 1.5
AUTO_FOV_PADDING = 15.0

WALL_MODEL_DIR = Path(__file__).resolve().parents[2] / "assets" / "walls"

WALL_MODEL_FILES = {
    WallAssetKind.ISOLATED: "wall_isolated",
    WallAssetKind.END: "wall_end",
    WallAssetKind.STRAIGHT: "wall_straight",
    WallAssetKind.CORNER: "wall_corner",
    WallAssetKind.T_JUNCTION: "wall_t_junction",
    WallAssetKind.CROSS: "wall_cross",
}

WALL_MODEL_EXTENSIONS = (".glb", ".obj", ".gltf")

WALL_MODEL_SCALE = 1.0


class GameView:
    """Draw the current game state."""

    def __init__(self) -> None:
        """Initialize UI state, camera, and unloaded assets."""
        self._window_width = 0
        self._window_height = 0
        self._main_menu_index = 0
        self._pause_menu_index = 0
        self._invincibility_enabled = False
        self._ghost_freeze_enabled = False
        self._speed_boost_enabled = False

        self._pending_player_name = ""
        self._name_error = ""
        self._score_entry_open = False
        self._score_entry_saved = False

        self._cell_size_3d = 1.0
        self._wall_height_3d = 0.8
        self._fov = 100.0
        self._wall_models: dict[WallAssetKind, Any] = {}

        self._camera: Any = ray.Camera3D(
            ray.Vector3(0.0, 15.0, 20.0),
            ray.Vector3(0.0, 0.0, 0.0),
            ray.Vector3(0.0, 1.0, 0.0),
            self._fov,
            ray.CameraProjection.CAMERA_PERSPECTIVE,
        )

    def initialize(self, window_width: int, window_height: int) -> None:
        """Initialize the game window."""
        ray.set_trace_log_level(ray.LOG_ERROR)
        self._window_width = window_width
        self._window_height = window_height
        ray.init_window(window_width, window_height, "Pac-Man")
        ray.set_exit_key(ray.KeyboardKey.KEY_NULL)
        self._load_wall_models()

    def shutdown(self) -> None:
        """Close the game window."""
        self._unload_wall_models()
        ray.close_window()

    def set_ui_state(
        self,
        main_menu_index: int,
        pause_menu_index: int,
        invincibility_enabled: bool = False,
        ghost_freeze_enabled: bool = False,
        speed_boost_enabled: bool = False,
        pending_player_name: str = "",
        name_error: str = "",
        score_entry_open: bool = False,
        score_entry_saved: bool = False,
        fov: float = 100.0,
    ) -> None:
        """Receive UI-only state from the controller."""
        self._main_menu_index = main_menu_index
        self._pause_menu_index = pause_menu_index
        self._invincibility_enabled = invincibility_enabled
        self._ghost_freeze_enabled = ghost_freeze_enabled
        self._speed_boost_enabled = speed_boost_enabled
        self._pending_player_name = pending_player_name
        self._name_error = name_error
        self._score_entry_open = score_entry_open
        self._score_entry_saved = score_entry_saved

        self._fov = fov
        self._camera.fovy = self._fov

    def render(self, model: ModelProtocol) -> None:
        """Render one frame."""
        self._window_width = ray.get_screen_width()
        self._window_height = ray.get_screen_height()

        ray.begin_drawing()
        ray.clear_background(BACKGROUND)

        phase = model.get_game_phase()

        if phase == GamePhase.MAIN_MENU:
            self._draw_main_menu()

        elif phase == GamePhase.HIGHSCORES_MENU:
            self._draw_highscores(model)

        elif phase == GamePhase.INSTRUCTIONS_MENU:
            self._draw_instructions()

        elif phase == GamePhase.PLAYING:
            self._draw_game(model)

        elif phase == GamePhase.PAUSED:
            self._draw_game(model)
            self._draw_pause_menu()

        elif phase == GamePhase.GAME_OVER:
            if self._score_entry_open:
                self._draw_score_entry_page(model)
            else:
                self._draw_game(model)

                ray.draw_rectangle(
                    0,
                    0,
                    self._window_width,
                    self._window_height,
                    OVERLAY_COLOR,
                )

                self._draw_end_screen(model, "GAME OVER")

        elif phase == GamePhase.WIN:
            if self._score_entry_open:
                self._draw_score_entry_page(model)
            else:
                self._draw_end_screen(model, "YOU WIN!")

        ray.end_drawing()

    def _draw_main_menu(self) -> None:
        """Draw the main menu."""
        options = [
            "Start Game",
            "Highscores",
            "Instructions",
            "Exit",
        ]
        self._draw_menu(
            title="Pac-Man",
            options=options,
            selected_index=self._main_menu_index,
            footer="Enter/click: select",
        )

    def _draw_pause_menu(self) -> None:
        """Draw the pause menu over the game."""
        ray.draw_rectangle(
            0,
            0,
            self._window_width,
            self._window_height,
            OVERLAY_COLOR,
        )

        invincibility = "ON" if self._invincibility_enabled else "OFF"
        ghost_freeze = "ON" if self._ghost_freeze_enabled else "OFF"
        speed_boost = "ON" if self._speed_boost_enabled else "OFF"

        options = [
            "Resume",
            f"Invincibility: {invincibility}",
            f"Ghost Freeze: {ghost_freeze}",
            f"Speed Boost: {speed_boost}",
            "Level Skip",
            "Return to Main Menu",
        ]

        self._draw_menu(
            title="Paused",
            options=options,
            selected_index=self._pause_menu_index,
            footer="Escape: resume   Enter: select",
        )

    def _draw_highscores(self, model: ModelProtocol) -> None:
        """Draw highscore screen."""
        scores = model.get_top_scores(10)
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            "Highscores",
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        if not scores:
            self._draw_centered_text(
                "No highscores yet",
                start_y + INFO_CONTENT_OFFSET,
                CONTENT_FONT_SIZE,
                TEXT_COLOR,
            )
        else:
            for index, entry in enumerate(scores):
                text = f"{index + 1}. {entry.name} - {entry.score} pts"
                self._draw_centered_text(
                    text,
                    start_y + INFO_CONTENT_OFFSET + index * 36,
                    CONTENT_FONT_SIZE,
                    TEXT_COLOR,
                )

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - 80,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_score_entry_page(self, model: ModelProtocol) -> None:
        """Draw highscore preview and username input after the game ends."""
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            "Highscores",
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        lines = self._build_score_entry_lines(model)

        y = start_y + 70
        for line in lines:
            self._draw_centered_text(
                line,
                y,
                CONTENT_FONT_SIZE,
                TEXT_COLOR,
            )
            y += 32

        displayed_name = self._pending_player_name.strip()
        if not displayed_name:
            displayed_name = "_"

        self._draw_centered_text(
            f"Enter name: {displayed_name}",
            self._window_height - 180,
            CONTENT_FONT_SIZE,
            TEXT_COLOR,
        )

        if self._name_error:
            self._draw_centered_text(
                self._name_error,
                self._window_height - 140,
                CONTENT_FONT_SIZE,
                ray.Color(255, 80, 80, 255),
            )

        if self._score_entry_saved:
            footer = "Score saved. Press Enter or Escape to return"
        else:
            footer = "Enter: save score"

        self._draw_centered_text(
            footer,
            self._window_height - 90,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _build_score_entry_lines(self, model: ModelProtocol) -> list[str]:
        """Build highscore preview lines with the current player's rank."""
        scores = model.get_top_scores(1000)
        current_score = model.get_score()

        player_name = "YOU"
        if self._score_entry_saved and self._pending_player_name.strip():
            player_name = self._pending_player_name.strip()

        base_scores = scores

        if self._score_entry_saved:
            base_scores = self._scores_without_current_saved_entry(
                scores,
                player_name,
                current_score,
            )

        rank = 1 + sum(
            1 for entry in base_scores
            if entry.score >= current_score
        )

        if rank <= 10:
            return self._build_top_ten_with_player(
                base_scores,
                rank,
                player_name,
                current_score,
            )

        lines = [
            f"{index + 1}. {entry.name} - {entry.score} pts"
            for index, entry in enumerate(base_scores[:10])
        ]

        if rank > 11:
            lines.append("...")

        lines.append(f"{rank}. {player_name} - {current_score} pts")
        return lines

    def _scores_without_current_saved_entry(
        self,
        scores: list[Any],
        player_name: str,
        current_score: int,
    ) -> list[Any]:
        """Remove the saved entry to avoid displaying it twice."""
        filtered: list[Any] = []
        removed = False

        for entry in scores:
            if (
                not removed
                and entry.name == player_name
                and entry.score == current_score
            ):
                removed = True
                continue

            filtered.append(entry)

        return filtered

    def _build_top_ten_with_player(
        self,
        scores: list[Any],
        rank: int,
        player_name: str,
        current_score: int,
    ) -> list[str]:
        """Build top 10 lines with current player inserted."""
        lines: list[str] = []
        inserted = False
        display_index = 1
        score_index = 0

        while len(lines) < 10:
            if display_index == rank:
                lines.append(
                    f"{display_index}. {player_name} - {current_score} pts"
                )
                inserted = True
                display_index += 1
                continue

            if score_index >= len(scores):
                break

            entry = scores[score_index]
            lines.append(
                f"{display_index}. {entry.name} - {entry.score} pts"
            )
            score_index += 1
            display_index += 1

        if not inserted and len(lines) < 10:
            lines.append(f"{rank}. {player_name} - {current_score} pts")

        return lines

    def _draw_instructions(self) -> None:
        """Draw instructions screen."""
        lines = [
            "Arrow keys or WASD: move Pac-Man",
            "Escape: pause or resume",
            "Enter: confirm menu selection",
            "F/R: adjust camera FOV",
            "Pause menu: cheat options for testing",
            "",
            "Eat all pacgums to complete the level.",
            "Super pacgums make ghosts edible for a short time.",
            "Avoid ghosts when they are not edible.",
        ]

        start_y = self._info_page_start_y()
        self._draw_centered_text(
            "Instructions",
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        for index, line in enumerate(lines):
            self._draw_centered_text(
                line,
                start_y + INFO_CONTENT_OFFSET + index * 34,
                CONTENT_FONT_SIZE,
                TEXT_COLOR,
            )

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - 80,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_end_screen(self, model: ModelProtocol, title: str) -> None:
        """Draw game over or victory screen."""
        start_y = self._info_page_start_y()
        self._draw_centered_text(
            title,
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        score_text = f"Final score: {model.get_score()}"
        score_y = start_y + INFO_CONTENT_OFFSET
        self._draw_centered_text(
            score_text,
            score_y,
            CONTENT_FONT_SIZE,
            TEXT_COLOR,
        )

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

    def _draw_menu(
        self,
        title: str,
        options: list[str],
        selected_index: int,
        footer: str,
    ) -> None:
        """Draw a vertical menu."""
        start_y = self._info_page_start_y()
        self._draw_centered_text(
            title,
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        for index, option in enumerate(options):
            color = SELECTED_COLOR if index == selected_index else TEXT_COLOR
            item_y = start_y + INFO_CONTENT_OFFSET
            item_y += index * MENU_ITEM_SPACING
            self._draw_centered_text(
                option,
                item_y,
                CONTENT_FONT_SIZE,
                color,
            )
            if index == selected_index:
                option_width = ray.measure_text(option, CONTENT_FONT_SIZE)
                option_x = (self._window_width - option_width) // 2
                marker_width = ray.measure_text("> ", CONTENT_FONT_SIZE)
                ray.draw_text(
                    "> ",
                    option_x - marker_width,
                    item_y,
                    CONTENT_FONT_SIZE,
                    SELECTED_COLOR,
                )

        self._draw_centered_text(
            footer,
            self._window_height - 90,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_centered_text(
        self,
        text: str,
        y: int,
        font_size: int,
        color: Any,
    ) -> None:
        """Draw horizontally centered text."""
        width = ray.measure_text(text, font_size)
        x = (self._window_width - width) // 2
        ray.draw_text(text, x, y, font_size, color)

    def get_menu_start_y(self) -> int:
        """Return the first menu item position for mouse handling."""
        return self._info_page_start_y() + INFO_CONTENT_OFFSET

    def _info_page_start_y(self) -> int:
        """Return the shared vertical start for information pages."""
        return int(self._window_height * INFO_PAGE_START_Y_RATIO)

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
