"""Main game controller.

The controller connects input, model and view.
It does not contain game rules and does not draw directly.
"""

from contextlib import redirect_stdout

import pyray as ray

from src.config import ConfigData
from src.controller.input import InputState, collect_input
from src.controller.state_machine import MenuCursor
from src.model.game_model import GameModel
from src.types.enums import CheatType, Direction, GamePhase
from src.view.ui import (
    CONTENT_FONT_SIZE,
    MENU_ITEM_SPACING,
    GameView,
)


WINDOW_WIDTH = 1980
WINDOW_HEIGHT = 1080
TARGET_FPS = 60
END_SCREEN_DISPLAY_SECONDS = 5.0

FOV_MIN = 30.0
FOV_MAX = 120.0
FOV_SPEED = 60.0

MENU_ITEM_HEIGHT = 40


class GameController:
    """Main controller for the Pac-Man application."""

    def __init__(self, config: ConfigData) -> None:
        """Initialize the model, view, menus, and UI state."""
        self._config = config
        self._model = GameModel(config)
        self._view = GameView()
        self._running = True
        self._main_menu = MenuCursor(size=4)
        self._pause_menu = MenuCursor(size=6)
        self._cheat_states: dict[CheatType, bool] = {
            CheatType.INVINCIBILITY: False,
            CheatType.GHOST_FREEZE: False,
            CheatType.SPEED_BOOST: False,
        }
        self._pending_player_name = ""
        self._name_error = ""
        self._end_screen_timer = 0.0
        self._score_entry_open = False
        self._score_entry_saved = False
        self._fov = FOV_MIN
        self._auto_fov_enabled = True
        self._last_mouse_position: tuple[int, int] | None = None

    def run(self) -> None:
        """Run the main game loop."""
        self._view.initialize(WINDOW_WIDTH, WINDOW_HEIGHT)
        ray.set_target_fps(TARGET_FPS)

        try:
            while self._running and not ray.window_should_close():
                input_state = collect_input()
                delta_time = ray.get_frame_time()

                self._update(input_state, delta_time)
                self._render()
        finally:
            self._view.shutdown()

    def _update(self, input_state: InputState, delta_time: float) -> None:
        """Update controller and model according to current game phase."""
        phase = self._model.get_game_phase()

        if phase == GamePhase.MAIN_MENU:
            self._update_main_menu(input_state)

        elif phase == GamePhase.HIGHSCORES_MENU:
            self._update_simple_return_screen(input_state)

        elif phase == GamePhase.INSTRUCTIONS_MENU:
            self._update_simple_return_screen(input_state)

        elif phase == GamePhase.PLAYING:
            self._update_playing(input_state, delta_time)

        elif phase == GamePhase.PAUSED:
            self._update_paused(input_state)

        elif phase == GamePhase.GAME_OVER:
            with redirect_stdout(None):
                self._model.update(delta_time)
            self._update_end_flow(input_state, delta_time)

        elif phase == GamePhase.WIN:
            self._update_end_flow(input_state, delta_time)

    def _render(self) -> None:
        """Render current frame through the view."""
        self._auto_update_fov()

        self._view.set_ui_state(
            main_menu_index=self._main_menu.current(),
            pause_menu_index=self._pause_menu.current(),
            invincibility_enabled=self._cheat_states[CheatType.INVINCIBILITY],
            ghost_freeze_enabled=self._cheat_states[CheatType.GHOST_FREEZE],
            speed_boost_enabled=self._cheat_states[CheatType.SPEED_BOOST],
            pending_player_name=self._pending_player_name,
            name_error=self._name_error,
            score_entry_open=self._score_entry_open,
            score_entry_saved=self._score_entry_saved,
            fov=self._fov,
        )
        self._view.render(self._model)

    def _clamp_fov(self, fov: float) -> float:
        """Clamp FOV to the allowed range."""
        return max(FOV_MIN, min(FOV_MAX, fov))

    def _auto_update_fov(self) -> None:
        """Automatically fit FOV to the current maze size."""
        if not self._auto_fov_enabled:
            return

        grid = self._model.get_grid()

        if not grid or not grid[0]:
            return

        auto_fov = self._view.calculate_auto_fov(grid)
        self._fov = self._clamp_fov(auto_fov)

    def _update_main_menu(self, input_state: InputState) -> None:
        """Handle main menu input."""
        self._main_menu.update(input_state)
        mouse_confirmed = self._update_menu_mouse(
            input_state,
            self._main_menu,
            ["Start Game", "Highscores", "Instructions", "Exit"],
        )

        if not input_state.confirm and not mouse_confirmed:
            return

        selected = self._main_menu.current()

        if selected == 0:
            self._start_new_game()

        elif selected == 1:
            self._model.set_game_phase(GamePhase.HIGHSCORES_MENU)

        elif selected == 2:
            self._model.set_game_phase(GamePhase.INSTRUCTIONS_MENU)

        elif selected == 3:
            self._running = False

    def _update_menu_mouse(
        self,
        input_state: InputState,
        menu: MenuCursor,
        options: list[str],
    ) -> bool:
        """Update menu cursor with mouse only when mouse is used."""
        current_position = (input_state.mouse_x, input_state.mouse_y)

        mouse_moved = (
            self._last_mouse_position is not None
            and current_position != self._last_mouse_position
        )

        self._last_mouse_position = current_position

        if not mouse_moved and not input_state.mouse_left_pressed:
            return False

        index = self._menu_index_from_mouse(
            input_state.mouse_x,
            input_state.mouse_y,
            options,
        )

        if index is None:
            return False

        menu.selected_index = index
        return bool(input_state.mouse_left_pressed)

    def _menu_index_from_mouse(
        self,
        mouse_x: int,
        mouse_y: int,
        options: list[str],
    ) -> int | None:
        """Return hovered menu index only if mouse is over option text."""
        start_y = self._view.get_menu_start_y()

        for index, option in enumerate(options):
            item_y = start_y + index * MENU_ITEM_SPACING
            text_width = ray.measure_text(option, CONTENT_FONT_SIZE)
            text_x = (ray.get_screen_width() - text_width) // 2

            inside_x = text_x - 30 <= mouse_x <= text_x + text_width + 30
            inside_y = item_y <= mouse_y <= item_y + MENU_ITEM_HEIGHT
            if inside_x and inside_y:
                return index

        return None

    def _start_new_game(self) -> None:
        """Create a fresh model and start a new game."""
        self._model = GameModel(self._config)
        self._model.set_game_phase(GamePhase.PLAYING)

        self._pause_menu.reset()
        self._cheat_states = {
            CheatType.INVINCIBILITY: False,
            CheatType.GHOST_FREEZE: False,
            CheatType.SPEED_BOOST: False,
        }
        self._auto_fov_enabled = True
        self._end_screen_timer = 0.0
        self._score_entry_open = False
        self._score_entry_saved = False
        self._pending_player_name = ""
        self._name_error = ""

    def _read_pending_player_name_input(self) -> None:
        """Read username input on the score entry page."""
        char_code = ray.get_char_pressed()

        while char_code > 0:
            char = chr(char_code)

            if len(self._pending_player_name) < 10:
                if char.isalnum() or char == " ":
                    self._pending_player_name += char
                    self._name_error = ""
                else:
                    self._name_error = "Only letters, numbers and spaces"

            char_code = ray.get_char_pressed()

        if ray.is_key_pressed(ray.KeyboardKey.KEY_BACKSPACE):
            self._pending_player_name = self._pending_player_name[:-1]
            self._name_error = ""

    def _update_playing(
        self,
        input_state: InputState,
        delta_time: float,
    ) -> None:
        """Handle gameplay input and update model."""
        if input_state.escape:
            self._model.set_game_phase(GamePhase.PAUSED)
            self._pause_menu.reset()
            return

        self._update_fov(input_state, delta_time)

        direction = self._get_direction_from_input(input_state)
        if direction != Direction.NONE:
            self._model.set_player_input(direction)

        self._model.update(delta_time)

    def _update_fov(
        self,
        input_state: InputState,
        delta_time: float,
    ) -> None:
        """Update camera FOV with R/F keys."""
        if input_state.fov_increase or input_state.fov_decrease:
            self._auto_fov_enabled = False

        if input_state.fov_increase:
            self._fov += FOV_SPEED * delta_time

        if input_state.fov_decrease:
            self._fov -= FOV_SPEED * delta_time

        self._fov = self._clamp_fov(self._fov)

    def _update_paused(self, input_state: InputState) -> None:
        """Handle pause menu input."""
        self._pause_menu.update(input_state)
        mouse_confirmed = self._update_menu_mouse(
            input_state,
            self._pause_menu,
            self._pause_menu_options(),
        )

        if input_state.escape:
            self._model.set_game_phase(GamePhase.PLAYING)
            return

        if not input_state.confirm and not mouse_confirmed:
            return

        selected = self._pause_menu.current()

        if selected == 0:
            self._model.set_game_phase(GamePhase.PLAYING)

        elif selected == 1:
            self._toggle_cheat(CheatType.INVINCIBILITY)

        elif selected == 2:
            self._toggle_cheat(CheatType.GHOST_FREEZE)

        elif selected == 3:
            self._toggle_cheat(CheatType.SPEED_BOOST)

        elif selected == 4:
            self._toggle_cheat(CheatType.LEVEL_SKIP)

        elif selected == 5:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()

    def _pause_menu_options(self) -> list[str]:
        """Return pause menu labels with current cheat states."""
        invincibility = (
            "ON" if self._cheat_states[CheatType.INVINCIBILITY] else "OFF"
        )
        ghost_freeze = (
            "ON" if self._cheat_states[CheatType.GHOST_FREEZE] else "OFF"
        )
        speed_boost = (
            "ON" if self._cheat_states[CheatType.SPEED_BOOST] else "OFF"
        )

        return [
            "Resume",
            f"Invincibility: {invincibility}",
            f"Ghost Freeze: {ghost_freeze}",
            f"Speed Boost: {speed_boost}",
            "Level Skip",
            "Return to Main Menu",
        ]

    def _update_simple_return_screen(self, input_state: InputState) -> None:
        """Handle highscores and instructions screens."""
        if input_state.confirm or input_state.escape:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()

    def _update_end_flow(
        self,
        input_state: InputState,
        delta_time: float,
    ) -> None:
        """Show the end screen, then handle score entry."""
        if not self._score_entry_open:
            self._end_screen_timer += delta_time

            if self._end_screen_timer >= END_SCREEN_DISPLAY_SECONDS:
                self._open_score_entry()

            return

        self._update_score_entry(input_state)

    def _open_score_entry(self) -> None:
        """Open a fresh score entry page."""
        self._score_entry_open = True
        self._score_entry_saved = False
        self._pending_player_name = ""
        self._name_error = ""

    def _update_score_entry(self, input_state: InputState) -> None:
        """Handle username input on the score entry page."""
        if self._score_entry_saved:
            if input_state.confirm or input_state.escape:
                self._model.set_game_phase(GamePhase.MAIN_MENU)
                self._main_menu.reset()
            return

        self._read_pending_player_name_input()

        if not input_state.confirm:
            return

        player_name = self._pending_player_name.strip()

        if not player_name:
            self._name_error = "Name cannot be empty"
            return

        if not self._model.submit_score(player_name):
            self._name_error = "Score could not be saved"
            return

        self._pending_player_name = player_name
        self._name_error = ""
        self._score_entry_saved = True

    def _toggle_cheat(self, cheat: CheatType) -> None:
        """Toggle a cheat from the pause menu."""
        if cheat in self._cheat_states:
            self._cheat_states[cheat] = not self._cheat_states[cheat]

        self._model.toggle_cheat(cheat)

    def _get_direction_from_input(
        self,
        input_state: InputState,
    ) -> Direction:
        """Convert input state into a Pac-Man direction."""
        if input_state.up:
            return Direction.UP
        if input_state.down:
            return Direction.DOWN
        if input_state.left:
            return Direction.LEFT
        if input_state.right:
            return Direction.RIGHT
        return Direction.NONE
