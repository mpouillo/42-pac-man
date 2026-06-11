"""Raylib based 2D user interface for Pac-Man."""

from typing import Any

import pyray as ray

from src.highscore import HighscoreEntry
from src.types.dataclasses import GhostData
from src.types.enums import CellState, GamePhase, GhostType
from src.types.protocols import ModelProtocol


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


class GameView:
    """Draw the current game state."""

    def __init__(self) -> None:
        self._window_width = 1280
        self._window_height = 720
        self._main_menu_index = 0
        self._pause_menu_index = 0
        self._wall_breaker_enabled = False

    def initialize(self, window_width: int, window_height: int) -> None:
        """Initialize the game window."""
        self._window_width = window_width
        self._window_height = window_height
        ray.init_window(window_width, window_height, "Pac-Man")

    def shutdown(self) -> None:
        """Close the game window."""
        ray.close_window()

    def set_ui_state(
        self,
        main_menu_index: int,
        pause_menu_index: int,
        wall_breaker_enabled: bool = False,
    ) -> None:
        """Receive UI-only state from the controller."""
        self._main_menu_index = main_menu_index
        self._pause_menu_index = pause_menu_index
        self._wall_breaker_enabled = wall_breaker_enabled

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

        elif phase == GamePhase.WIN:
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
            footer="Space resumes the game",
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
            "Press Enter, Space, or Escape to return",
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
            "Space: pause or resume",
            "Enter: confirm menu selection",
            "Escape: return to main menu",
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
            "Press Enter, Space, or Escape to return",
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
            "Press Enter to save as PLAYER",
            310,
            26,
            TEXT_COLOR,
        )
        self._draw_centered_text(
            "Press Escape to return without saving",
            350,
            22,
            MUTED_TEXT_COLOR,
        )

    def _draw_game(self, model: ModelProtocol) -> None:
        """Draw gameplay screen."""
        self._draw_hud(model)
        self._draw_grid(model)
        self._draw_entities(model)

    def _draw_hud(self, model: ModelProtocol) -> None:
        """Draw score, lives, level, and timer."""
        time_left = max(0, int(model.get_remaining_time()))
        level = model.get_current_level() + 1

        left_text = f"Score: {model.get_score()}   Lives: {model.get_lives()}"
        right_text = f"Level: {level}   Time: {time_left}"

        ray.draw_text(left_text, 24, 22, 26, TEXT_COLOR)

        width = ray.measure_text(right_text, 26)
        ray.draw_text(
            right_text,
            self._window_width - width - 24,
            22,
            26,
            TEXT_COLOR,
        )

    def _draw_grid(self, model: ModelProtocol) -> None:
        """Draw maze cells."""
        grid = model.get_grid()
        layout = self._get_grid_layout(grid)

        if layout is None:
            return

        offset_x, offset_y, cell_size = layout

        board_width = len(grid[0]) * cell_size
        board_height = len(grid) * cell_size

        ray.draw_rectangle(
            offset_x,
            offset_y,
            board_width,
            board_height,
            BOARD_BACKGROUND,
        )

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                self._draw_cell(cell, x, y, offset_x, offset_y, cell_size)

    def _draw_cell(
        self,
        cell: CellState,
        x: int,
        y: int,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:
        """Draw one maze cell."""
        screen_x = offset_x + x * cell_size
        screen_y = offset_y + y * cell_size

        if cell == CellState.WALL:
            ray.draw_rectangle(
                screen_x,
                screen_y,
                cell_size,
                cell_size,
                WALL_COLOR,
            )

        elif cell == CellState.PACGUM:
            radius = max(2, cell_size // 8)
            self._draw_cell_circle(
                screen_x,
                screen_y,
                cell_size,
                radius,
                PACGUM_COLOR,
            )

        elif cell == CellState.SUPER_PACGUM:
            radius = max(4, cell_size // 4)
            self._draw_cell_circle(
                screen_x,
                screen_y,
                cell_size,
                radius,
                SUPER_PACGUM_COLOR,
            )

    def _draw_entities(self, model: ModelProtocol) -> None:
        """Draw Pac-Man and ghosts."""
        grid = model.get_grid()
        layout = self._get_grid_layout(grid)

        if layout is None:
            return

        offset_x, offset_y, cell_size = layout

        pacman = model.get_pacman()
        self._draw_entity_circle(
            pacman.x,
            pacman.y,
            offset_x,
            offset_y,
            cell_size,
            PACMAN_COLOR,
        )

        for ghost in model.get_ghosts():
            self._draw_ghost(ghost, offset_x, offset_y, cell_size)

    def _draw_ghost(
        self,
        ghost: GhostData,
        offset_x: int,
        offset_y: int,
        cell_size: int,
    ) -> None:
        """Draw one ghost."""
        self._draw_entity_circle(
            ghost.x,
            ghost.y,
            offset_x,
            offset_y,
            cell_size,
            self._get_ghost_color(ghost),
        )

    def _draw_entity_circle(
        self,
        grid_x: float,
        grid_y: float,
        offset_x: int,
        offset_y: int,
        cell_size: int,
        color: Any,
    ) -> None:
        """Draw an entity centered on grid coordinates."""
        screen_x = int(offset_x + grid_x * cell_size + cell_size / 2)
        screen_y = int(offset_y + grid_y * cell_size + cell_size / 2)
        radius = max(4, cell_size // 2 - 2)

        ray.draw_circle(screen_x, screen_y, radius, color)

    def _draw_cell_circle(
        self,
        screen_x: int,
        screen_y: int,
        cell_size: int,
        radius: int,
        color: Any,
    ) -> None:
        """Draw a circle centered inside a cell."""
        center_x = screen_x + cell_size // 2
        center_y = screen_y + cell_size // 2
        ray.draw_circle(center_x, center_y, radius, color)

    def _get_grid_layout(
        self,
        grid: list[list[CellState]],
    ) -> tuple[int, int, int] | None:
        """Return offset x, offset y, and cell size."""
        if not grid or not grid[0]:
            return None

        rows = len(grid)
        cols = len(grid[0])

        hud_height = 70
        padding = 24
        max_width = self._window_width - padding * 2
        max_height = self._window_height - hud_height - padding * 2

        cell_size = min(max_width // cols, max_height // rows)
        cell_size = max(4, cell_size)

        board_width = cols * cell_size
        board_height = rows * cell_size

        offset_x = (self._window_width - board_width) // 2
        offset_y = hud_height + (max_height - board_height) // 2

        return offset_x, offset_y, cell_size

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
