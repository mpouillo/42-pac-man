"""Raylib based 3D user interface for Pac-Man."""

from pathlib import Path
from typing import Any

import pyray as ray

from src.highscore import HighscoreEntry
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
WALL_MODEL_Y_OFFSET = 0.0

class GameView:
    """Draw the current game state."""

    def __init__(self) -> None:
        self._window_width = 0
        self._window_height = 0
        self._main_menu_index = 0
        self._pause_menu_index = 0
        self._wall_breaker_enabled = False

        self._name_popup_open = False
        self._pending_player_name = ""
        self._name_error = ""

        self._cell_size_3d = 1.0
        self._wall_height_3d = 0.8
        self._fov = 100.0
        self._wall_models: dict[WallAssetKind, Any] = {}

        self._camera: Any = ray.Camera3D(
            ray.Vector3(0.0, 15.0, 20.0), # position z = bas du maze (maze_y // 2)
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
        wall_breaker_enabled: bool = False,
        name_popup_open: bool = False,
        pending_player_name: str = "",
        name_error: str = "",
        fov: float = 100.0,
    ) -> None:
        """Receive UI-only state from the controller."""
        self._main_menu_index = main_menu_index
        self._pause_menu_index = pause_menu_index
        self._wall_breaker_enabled = wall_breaker_enabled
        self._name_popup_open = name_popup_open
        self._pending_player_name = pending_player_name
        self._name_error = name_error

        self._fov = fov
        self._camera.fovy = self._fov

    def render(self, model: ModelProtocol) -> None:
        """Render one frame."""
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
            self._draw_end_screen(model, "GAME OVER")

            if self._name_popup_open:
                self._draw_name_popup()

        elif phase == GamePhase.WIN:
            self._draw_end_screen(model, "YOU WIN!")

            if self._name_popup_open:
                self._draw_name_popup()

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
            footer="Use arrow keys and Enter",
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

        wall_breaker = "ON" if self._wall_breaker_enabled else "OFF"
        options = [
            "Resume",
            f"Wall Breaker Cheat: {wall_breaker}",
            "Return to Main Menu",
        ]

        self._draw_menu(
            title="Paused",
            options=options,
            selected_index=self._pause_menu_index,
            footer="Escape: resume   Enter: select",
        )

    def _draw_name_popup(self) -> None:
        """Draw the username input popup before starting a game."""
        ray.draw_rectangle(
            0,
            0,
            self._window_width,
            self._window_height,
            OVERLAY_COLOR,
        )

        popup_width = 460
        popup_height = 240
        popup_x = (self._window_width - popup_width) // 2
        popup_y = (self._window_height - popup_height) // 2

        ray.draw_rectangle(
            popup_x,
            popup_y,
            popup_width,
            popup_height,
            BACKGROUND,
        )
        ray.draw_rectangle_lines(
            popup_x,
            popup_y,
            popup_width,
            popup_height,
            SELECTED_COLOR,
        )

        self._draw_centered_text(
            "Enter your username",
            popup_y + 30,
            28,
            SELECTED_COLOR,
        )

        input_width = 320
        input_height = 44
        input_x = (self._window_width - input_width) // 2
        input_y = popup_y + 90

        ray.draw_rectangle(
            input_x,
            input_y,
            input_width,
            input_height,
            BOARD_BACKGROUND,
        )
        ray.draw_rectangle_lines(
            input_x,
            input_y,
            input_width,
            input_height,
            TEXT_COLOR,
        )

        displayed_name = self._pending_player_name
        if not displayed_name:
            displayed_name = "_"

        name_width = ray.measure_text(displayed_name, 24)
        ray.draw_text(
            displayed_name,
            input_x + (input_width - name_width) // 2,
            input_y + 10,
            24,
            TEXT_COLOR,
        )

        if self._name_error:
            self._draw_centered_text(
                self._name_error,
                popup_y + 145,
                18,
                ray.Color(255, 80, 80, 255),
            )

        self._draw_centered_text(
            "Enter: save score",
            popup_y + 185,
            20,
            MUTED_TEXT_COLOR,
        )

    def _draw_highscores(self, model: ModelProtocol) -> None:
        """Draw highscore screen."""
        self._draw_centered_text("Highscores", 90, 48, SELECTED_COLOR)

        scores = model.get_top_scores(10)
        if not scores:
            self._draw_centered_text(
                "No highscores yet",
                200,
                28,
                TEXT_COLOR,
            )
        else:
            self._draw_score_entries(scores)

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - 80,
            22,
            MUTED_TEXT_COLOR,
        )

    def _draw_score_entries(
        self,
        scores: list[HighscoreEntry],
    ) -> None:
        """Draw highscore entries."""
        start_y = 170

        for index, entry in enumerate(scores):
            text = f"{index + 1}. {entry.name} - {entry.score} pts"
            self._draw_centered_text(
                text,
                start_y + index * 36,
                26,
                TEXT_COLOR,
            )

    def _draw_instructions(self) -> None:
        """Draw instructions screen."""
        self._draw_centered_text("Instructions", 80, 48, SELECTED_COLOR)

        lines = [
            "Arrow keys: move Pac-Man",
            "Escape: pause or resume",
            "Enter: confirm menu selection",
            "Enter: confirm menu selection",
            "",
            "Eat all pacgums to complete the level.",
            "Super pacgums make ghosts edible for a short time.",
            "Avoid ghosts when they are not edible.",
        ]

        y = 160
        for line in lines:
            self._draw_centered_text(line, y, 24, TEXT_COLOR)
            y += 34

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - 80,
            22,
            MUTED_TEXT_COLOR,
        )

    def _draw_end_screen(self, model: ModelProtocol, title: str) -> None:
        """Draw game over or victory screen."""
        self._draw_centered_text(title, 120, 56, SELECTED_COLOR)

        score_text = f"Final score: {model.get_score()}"
        self._draw_centered_text(score_text, 230, 34, TEXT_COLOR)

        self._draw_centered_text(
            "Press Enter to enter your username",
            310,
            26,
            TEXT_COLOR,
        )
        self._draw_centered_text(
            "Username is required to save the score",
            350,
            22,
            MUTED_TEXT_COLOR,
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
            position.y + WALL_MODEL_Y_OFFSET,
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
        right_text = f"FOV: {int(self._fov)}   Level: {level}   Time: {time_left}"

        ray.draw_text(left_text, 24, 22, 26, TEXT_COLOR)

        width = ray.measure_text(right_text, 26)
        ray.draw_text(
            right_text,
            self._window_width - width - 24,
            22,
            26,
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
        self._draw_centered_text(title, 100, 64, SELECTED_COLOR)

        start_y = 230
        for index, option in enumerate(options):
            prefix = "> " if index == selected_index else "  "
            color = SELECTED_COLOR if index == selected_index else TEXT_COLOR
            self._draw_centered_text(
                prefix + option,
                start_y + index * 44,
                30,
                color,
            )

        self._draw_centered_text(
            footer,
            self._window_height - 90,
            22,
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
