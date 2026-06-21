"""Central Raylib view coordinator for Pac-Man."""

from typing import Any

import pyray as ray

from src.constants import (
    BACKGROUND,
    CAMERA_POSITION,
    CAMERA_TARGET,
    CAMERA_UP,
    DEFAULT_FOV,
    OVERLAY_COLOR,
    WINDOW_TITLE,
)
from src.types.enums import GamePhase
from src.types.protocols import ModelProtocol
from src.view.menus import MenuRendererMixin
from src.view.pages import PageRendererMixin
from src.view.scene_3d import Scene3DRendererMixin
from src.view.state import ViewState
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
        self._fov = DEFAULT_FOV
        self._auto_fov_enabled = True
        self._wall_models: dict[WallAssetKind, tuple[Any, Any]] = {}
        self._entity_models: dict[str, Any] = {}

        self._camera: Any = ray.Camera3D(
            ray.Vector3(*CAMERA_POSITION),
            ray.Vector3(*CAMERA_TARGET),
            ray.Vector3(*CAMERA_UP),
            self._fov,
            ray.CameraProjection.CAMERA_PERSPECTIVE,
        )

    def initialize(self, window_width: int, window_height: int) -> None:
        """Initialize the game window."""
        ray.set_trace_log_level(ray.LOG_ERROR)
        self._window_width = window_width
        self._window_height = window_height
        ray.init_window(window_width, window_height, WINDOW_TITLE)
        ray.set_exit_key(ray.KeyboardKey.KEY_NULL)
        self._load_wall_models()
        self._load_entity_models()

    def shutdown(self) -> None:
        """Close the game window."""
        self._unload_wall_models()
        self._unload_entity_models()
        ray.close_window()

    def render(self, model: ModelProtocol, state: ViewState) -> None:
        """Render one frame."""
        self._window_width = ray.get_screen_width()
        self._window_height = ray.get_screen_height()

        ray.begin_drawing()
        ray.clear_background(BACKGROUND)

        phase = model.get_game_phase()

        if phase == GamePhase.MAIN_MENU:
            self._draw_main_menu(state)

        elif phase == GamePhase.HIGHSCORES_MENU:
            self._draw_highscores(model)

        elif phase == GamePhase.INSTRUCTIONS_MENU:
            self._draw_instructions()

        elif phase == GamePhase.PLAYING:
            self._draw_game(model)

        elif phase == GamePhase.PAUSED:
            self._draw_game(model)
            self._draw_pause_menu(state)

        elif phase == GamePhase.GAME_OVER:
            if state.score_entry_open:
                self._draw_score_entry_page(model, state)
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
            if state.score_entry_open:
                self._draw_score_entry_page(model, state)
            else:
                self._draw_end_screen(model, "YOU WIN!")

        ray.end_drawing()
