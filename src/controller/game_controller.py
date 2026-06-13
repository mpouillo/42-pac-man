"""Main game controller.

The controller connects input, model and view.
It does not contain game rules and does not draw directly.
"""

import pyray as ray

from src.config import ConfigData
from src.controller.input import InputState, collect_input
from src.controller.state_machine import MenuCursor
from src.model.game_model import GameModel
from src.types.enums import CheatType, Direction, GamePhase
from src.view.ui import GameView


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60


class GameController:
    """Main controller for the Pac-Man application."""
    def __init__(self, config: ConfigData) -> None:
        self._config = config
        self._model = GameModel(config)
        self._view = GameView()
        self._running = True
        self._main_menu = MenuCursor(size=4)
        self._pause_menu = MenuCursor(size=3)
        self._wall_breaker_enabled = False
        self._name_popup_open = False
        self._pending_player_name = ""
        self._current_player_name = "PLAYER"
        self._name_error = ""

    def run(self) -> None:
        """Run the main game loop."""
        self._view.initialize(WINDOW_WIDTH, WINDOW_HEIGHT)
        ray.set_target_fps(TARGET_FPS)

        while self._running and not ray.window_should_close():
            input_state = collect_input()
            delta_time = ray.get_frame_time()

            self._update(input_state, delta_time)
            self._render()

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
            self._update_end_screen(input_state)

        elif phase == GamePhase.WIN:
            self._update_end_screen(input_state)

    def _render(self) -> None:
        """Render current frame through the view."""
        self._view.set_ui_state(
            main_menu_index=self._main_menu.current(),
            pause_menu_index=self._pause_menu.current(),
            wall_breaker_enabled=self._wall_breaker_enabled,
            name_popup_open=self._name_popup_open,
            pending_player_name=self._pending_player_name,
            name_error=self._name_error,
        )
        self._view.render(self._model)

    def _update_main_menu(self, input_state: InputState) -> None:
        """Handle main menu input."""
        if self._name_popup_open:
            self._update_name_popup(input_state)
            return

        self._main_menu.update(input_state)

        if input_state.escape:
            self._running = False
            return

        if not input_state.confirm:
            return

        selected = self._main_menu.current()

        if selected == 0:
            self._name_popup_open = True
            self._pending_player_name = ""
            self._name_error = ""

        elif selected == 1:
            self._model.set_game_phase(GamePhase.HIGHSCORES_MENU)

        elif selected == 2:
            self._model.set_game_phase(GamePhase.INSTRUCTIONS_MENU)

        elif selected == 3:
            self._running = False

    def _start_new_game(self) -> None:
        """Create a fresh model and start a new game."""
        self._model = GameModel(self._config)
        self._model.set_game_phase(GamePhase.PLAYING)

        self._pause_menu.reset()
        self._wall_breaker_enabled = False

    def _read_pending_player_name_input(self) -> None:
        """Read username input while the start-game popup is open."""
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

    def _update_name_popup(self, input_state: InputState) -> None:
        """Handle the username popup before starting a game."""
        self._read_pending_player_name_input()

        if input_state.escape:
            self._name_popup_open = False
            self._pending_player_name = ""
            self._name_error = ""
            return

        if not input_state.confirm:
            return

        player_name = self._pending_player_name.strip()

        if not player_name:
            self._name_error = "Name cannot be empty"
            return

        self._current_player_name = player_name
        self._name_popup_open = False
        self._pending_player_name = ""
        self._name_error = ""
        self._start_new_game()

    def _update_playing(
        self,
        input_state: InputState,
        delta_time: float,
    ) -> None:
        """Handle gameplay input and update model."""
        if input_state.pause:
            self._model.set_game_phase(GamePhase.PAUSED)
            self._pause_menu.reset()
            return

        if input_state.escape:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()
            return

        direction = self._get_direction_from_input(input_state)
        if direction != Direction.NONE:
            self._model.set_player_input(direction)

        self._model.update(delta_time)

    def _update_paused(self, input_state: InputState) -> None:
        """Handle pause menu input."""
        self._pause_menu.update(input_state)

        if input_state.pause:
            self._model.set_game_phase(GamePhase.PLAYING)
            return

        if input_state.escape:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()
            return

        if not input_state.confirm:
            return

        selected = self._pause_menu.current()

        if selected == 0:
            self._model.set_game_phase(GamePhase.PLAYING)

        elif selected == 1:
            self._toggle_wall_breaker()

        elif selected == 2:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()

    def _update_simple_return_screen(self, input_state: InputState) -> None:
        """Handle highscores and instructions screens."""
        if input_state.confirm or input_state.escape or input_state.pause:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()

    def _update_end_screen(self, input_state: InputState) -> None:
        """Handle game over and win screens.

        Name input will be added later.
        For now, ENTER submits a default name and returns to main menu.
        """
        if input_state.confirm:
            self._model.submit_score(self._current_player_name)
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()

        elif input_state.escape:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu.reset()

    def _toggle_wall_breaker(self) -> None:
        """Toggle wall breaker cheat through the model."""
        self._wall_breaker_enabled = not self._wall_breaker_enabled
        self._model.toggle_cheat(CheatType.WALL_JUMP)

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
