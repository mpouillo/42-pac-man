"""Central Raylib view coordinator for Pac-Man."""

from dataclasses import dataclass
from typing import Any

import pyray as ray

from src.constants import (
    BACKGROUND,
    CAMERA_POSITION,
    CAMERA_TARGET,
    CAMERA_UP,
    DEFAULT_FOV,
    OVERLAY_COLOR,
    TEXT_PAGE_BODY_TOP_OFFSET,
    TEXT_PAGE_START_Y_RATIO,
    WINDOW_TITLE,
)
from src.types.enums import GamePhase
from src.types.protocols import ModelProtocol
from src.view.menus import MenuRendererMixin
from src.view.pages import PageRendererMixin
from src.view.scene_3d import Scene3DRendererMixin
from src.view.wall_shapes import WallAssetKind


@dataclass(frozen=True)
class ViewState:
    """Contain controller-owned state needed for one rendered frame."""

    main_menu_index: int
    pause_menu_index: int
    invincibility_enabled: bool
    ghost_freeze_enabled: bool
    speed_boost_enabled: bool
    pending_player_name: str
    name_error: str
    score_entry_open: bool
    score_entry_saved: bool


class TextRendererMixin:
    """Provide shared text drawing and vertical layout helpers."""

    _window_width: int
    _window_height: int

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
        return self._info_page_start_y() + TEXT_PAGE_BODY_TOP_OFFSET

    def _info_page_start_y(self) -> int:
        """Return the shared vertical start for information pages."""
        return int(self._window_height * TEXT_PAGE_START_Y_RATIO)


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
