"""Central Raylib view coordinator for Pac-Man."""

from typing import Any

import pyray as ray

from src.types.enums import GamePhase
from src.types.protocols import ModelProtocol
from src.view.constants import BACKGROUND, OVERLAY_COLOR
from src.view.menus import MenuRendererMixin
from src.view.pages import PageRendererMixin
from src.view.scene_3d import Scene3DRendererMixin
from src.view.text import TextRendererMixin
from src.view.wall_shapes import WallAssetKind


class GameView(
    TextRendererMixin,
    MenuRendererMixin,
    PageRendererMixin,
    Scene3DRendererMixin,
):
    """Coordinate page routing and shared view state."""

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
        self._auto_fov_enabled = True
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
