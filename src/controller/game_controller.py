"""Main game controller."""

from contextlib import redirect_stdout

import pyray as ray

from src.config import ConfigData
from src.constants import (
    END_SCREEN_DISPLAY_SECONDS,
    MAIN_MENU_OPTIONS,
    MENU_ITEM_HEIGHT,
    MENU_ITEM_SPACING,
    PAUSE_MENU_OPTION_TEMPLATES,
    PLAYER_NAME_MAX_LENGTH,
    TARGET_FPS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.controller.input import InputState, collect_input
from src.model.game_model import GameModel
from src.types.enums import CheatType, Direction, GamePhase
from src.view.ui import GameView, ViewState


class GameController:
    """Main controller for the Pac-Man application."""

    def __init__(self, config: ConfigData) -> None:
        """Initialize the model, view, menus, and UI state."""
        self._config = config
        self._model = GameModel(config)
        self._view = GameView()
        self._running = True
        self._main_menu_index = 0
        self._pause_menu_index = 0
        self._cheat_states: dict[CheatType, bool] = (
            self._default_cheat_states()
        )
        self._end_screen_timer: float
        self._pending_player_name: str
        self._name_error: str
        self._score_entry_open: bool
        self._score_entry_saved: bool
        self._reset_end_flow()
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
        state = ViewState(
            main_menu_index=self._main_menu_index,
            pause_menu_index=self._pause_menu_index,
            invincibility_enabled=self._cheat_states[CheatType.INVINCIBILITY],
            ghost_freeze_enabled=self._cheat_states[CheatType.GHOST_FREEZE],
            speed_boost_enabled=self._cheat_states[CheatType.SPEED_BOOST],
            pending_player_name=self._pending_player_name,
            name_error=self._name_error,
            score_entry_open=self._score_entry_open,
            score_entry_saved=self._score_entry_saved,
        )
        self._view.render(self._model, state)

    def _update_main_menu(self, input_state: InputState) -> None:
        """Handle main menu input."""
        self._main_menu_index = self._move_menu_index(
            self._main_menu_index,
            len(MAIN_MENU_OPTIONS),
            input_state,
        )
        self._main_menu_index, mouse_confirmed = self._update_menu_mouse(
            input_state,
            self._main_menu_index,
            len(MAIN_MENU_OPTIONS),
        )

        if not input_state.confirm and not mouse_confirmed:
            return

        selected = self._main_menu_index

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
        selected_index: int,
        size: int,
    ) -> tuple[int, bool]:
        """Return the mouse-selected menu index and confirmation state."""
        current_position = (input_state.mouse_x, input_state.mouse_y)

        mouse_moved = (
            self._last_mouse_position is not None
            and current_position != self._last_mouse_position
        )

        self._last_mouse_position = current_position

        if not mouse_moved and not input_state.mouse_left_pressed:
            return selected_index, False

        index = self._menu_index_from_mouse(
            input_state.mouse_y,
            size,
        )

        if index is None:
            return selected_index, False

        return index, bool(input_state.mouse_left_pressed)

    def _menu_index_from_mouse(
        self,
        mouse_y: int,
        size: int,
    ) -> int | None:
        """Return hovered menu index from its vertical position."""
        start_y = self._view.get_menu_start_y()
        index = (mouse_y - start_y) // MENU_ITEM_SPACING

        if 0 <= index < size:
            item_y = start_y + index * MENU_ITEM_SPACING
            if item_y <= mouse_y <= item_y + MENU_ITEM_HEIGHT:
                return index

        return None

    def _move_menu_index(
        self,
        index: int,
        size: int,
        input_state: InputState,
    ) -> int:
        """Move a menu index with up/down input."""
        if input_state.up:
            return (index - 1) % size
        if input_state.down:
            return (index + 1) % size
        return index

    def _start_new_game(self) -> None:
        """Create a fresh model and start a new game."""
        self._model = GameModel(self._config)
        self._model.set_game_phase(GamePhase.PLAYING)

        self._pause_menu_index = 0
        self._cheat_states = self._default_cheat_states()
        self._view.reset_fov()
        self._reset_end_flow()

    def _read_pending_player_name_input(self) -> None:
        """Read username input on the score entry page."""
        char_code = ray.get_char_pressed()

        while char_code > 0:
            char = chr(char_code)

            if len(self._pending_player_name) < PLAYER_NAME_MAX_LENGTH:
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
            self._pause_menu_index = 0
            return

        self._view.update_fov(
            self._model.get_grid(),
            input_state.fov_increase,
            input_state.fov_decrease,
            delta_time,
        )

        direction = self._get_direction_from_input(input_state)
        if direction != Direction.NONE:
            self._model.set_player_input(direction)

        self._model.update(delta_time)

    def _update_paused(self, input_state: InputState) -> None:
        """Handle pause menu input."""
        self._pause_menu_index = self._move_menu_index(
            self._pause_menu_index,
            len(PAUSE_MENU_OPTION_TEMPLATES),
            input_state,
        )
        self._pause_menu_index, mouse_confirmed = self._update_menu_mouse(
            input_state,
            self._pause_menu_index,
            len(PAUSE_MENU_OPTION_TEMPLATES),
        )

        if input_state.escape:
            self._model.set_game_phase(GamePhase.PLAYING)
            return

        if not input_state.confirm and not mouse_confirmed:
            return

        selected = self._pause_menu_index

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
            self._main_menu_index = 0

    def _update_simple_return_screen(self, input_state: InputState) -> None:
        """Handle highscores and instructions screens."""
        if input_state.confirm or input_state.escape:
            self._model.set_game_phase(GamePhase.MAIN_MENU)
            self._main_menu_index = 0

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
        self._reset_score_entry_state()
        self._score_entry_open = True

    def _update_score_entry(self, input_state: InputState) -> None:
        """Handle username input on the score entry page."""
        if self._score_entry_saved:
            if input_state.confirm or input_state.escape:
                self._model.set_game_phase(GamePhase.MAIN_MENU)
                self._main_menu_index = 0
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

    @staticmethod
    def _default_cheat_states() -> dict[CheatType, bool]:
        """Return disabled states for all toggleable cheats."""
        return {
            CheatType.INVINCIBILITY: False,
            CheatType.GHOST_FREEZE: False,
            CheatType.SPEED_BOOST: False,
        }

    def _reset_end_flow(self) -> None:
        """Reset end-screen timing and score-entry state."""
        self._end_screen_timer = 0.0
        self._reset_score_entry_state()

    def _reset_score_entry_state(self) -> None:
        """Reset score-entry fields without opening the page."""
        self._pending_player_name = ""
        self._name_error = ""
        self._score_entry_open = False
        self._score_entry_saved = False

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
