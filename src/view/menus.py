"""Main and pause menu rendering."""

from collections.abc import Sequence
from typing import Any, Callable

import pyray as ray

from src.constants import (
    CONTENT_FONT_SIZE,
    INFO_CONTENT_OFFSET,
    MAIN_MENU_OPTIONS,
    MENU_FOOTER_BOTTOM_OFFSET,
    MENU_ITEM_SPACING,
    MUTED_TEXT_COLOR,
    OVERLAY_COLOR,
    PAUSE_MENU_OPTION_TEMPLATES,
    SELECTED_COLOR,
    TEXT_COLOR,
    TITLE_FONT_SIZE,
)
from src.view.state import ViewState


def pause_menu_options(
    invincibility_enabled: bool,
    ghost_freeze_enabled: bool,
    speed_boost_enabled: bool,
) -> tuple[str, ...]:
    """Return the shared pause menu labels."""
    invincibility = "ON" if invincibility_enabled else "OFF"
    ghost_freeze = "ON" if ghost_freeze_enabled else "OFF"
    speed_boost = "ON" if speed_boost_enabled else "OFF"

    return tuple(
        template.format(
            invincibility=invincibility,
            ghost_freeze=ghost_freeze,
            speed_boost=speed_boost,
        )
        for template in PAUSE_MENU_OPTION_TEMPLATES
    )


class MenuRendererMixin:
    """Draw the main menu, pause menu, and shared menu layout."""

    _window_width: int
    _window_height: int
    _draw_centered_text: Callable[[str, int, int, Any], None]
    _info_page_start_y: Callable[[], int]

    def _draw_main_menu(self, state: ViewState) -> None:
        """Draw the main menu."""
        self._draw_menu(
            title="Pac-Man",
            options=MAIN_MENU_OPTIONS,
            selected_index=state.main_menu_index,
            footer="Enter/click: select",
        )

    def _draw_pause_menu(self, state: ViewState) -> None:
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
                state.invincibility_enabled,
                state.ghost_freeze_enabled,
                state.speed_boost_enabled,
            ),
            selected_index=state.pause_menu_index,
            footer="Escape: resume   Enter: select",
        )

    def _draw_menu(
        self,
        title: str,
        options: Sequence[str],
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
            self._window_height - MENU_FOOTER_BOTTOM_OFFSET,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )
