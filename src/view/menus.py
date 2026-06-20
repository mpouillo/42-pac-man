"""Main and pause menu rendering."""

from typing import Any, Callable

import pyray as ray

from src.view.constants import (
    CONTENT_FONT_SIZE,
    INFO_CONTENT_OFFSET,
    MENU_ITEM_SPACING,
    MUTED_TEXT_COLOR,
    OVERLAY_COLOR,
    SELECTED_COLOR,
    TEXT_COLOR,
    TITLE_FONT_SIZE,
)


def main_menu_options() -> list[str]:
    """Return the shared main menu labels."""
    return [
        "Start Game",
        "Highscores",
        "Instructions",
        "Exit",
    ]


def pause_menu_options(
    invincibility_enabled: bool,
    ghost_freeze_enabled: bool,
    speed_boost_enabled: bool,
) -> list[str]:
    """Return the shared pause menu labels."""
    invincibility = "ON" if invincibility_enabled else "OFF"
    ghost_freeze = "ON" if ghost_freeze_enabled else "OFF"
    speed_boost = "ON" if speed_boost_enabled else "OFF"

    return [
        "Resume",
        f"Invincibility: {invincibility}",
        f"Ghost Freeze: {ghost_freeze}",
        f"Speed Boost: {speed_boost}",
        "Level Skip",
        "Return to Main Menu",
    ]


class MenuRendererMixin:
    """Draw the main menu, pause menu, and shared menu layout."""

    _window_width: int
    _window_height: int
    _main_menu_index: int
    _pause_menu_index: int
    _invincibility_enabled: bool
    _ghost_freeze_enabled: bool
    _speed_boost_enabled: bool
    _draw_centered_text: Callable[[str, int, int, Any], None]
    _info_page_start_y: Callable[[], int]

    def _draw_main_menu(self) -> None:
        """Draw the main menu."""
        self._draw_menu(
            title="Pac-Man",
            options=main_menu_options(),
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

        self._draw_menu(
            title="Paused",
            options=pause_menu_options(
                self._invincibility_enabled,
                self._ghost_freeze_enabled,
                self._speed_boost_enabled,
            ),
            selected_index=self._pause_menu_index,
            footer="Escape: resume   Enter: select",
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
