"""Main and pause menu rendering."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Callable

import pyray as ray

from src.constants import (
    BACKGROUND,
    MAIN_MENU_OPTIONS,
    MENU_MARKER_GAP,
    MENU_MARKER_MOUTH_RATIO,
    MENU_MARKER_SIZE,
    MENU_ITEM_SPACING,
    MUTED_TEXT_COLOR,
    OVERLAY_COLOR,
    PAUSE_MENU_OPTION_TEMPLATES,
    SELECTED_COLOR,
    TEXT_COLOR,
    TEXT_PAGE_BODY_FONT_SIZE,
    TEXT_PAGE_BODY_TOP_OFFSET,
    TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
    TEXT_PAGE_TITLE_FONT_SIZE,
)

if TYPE_CHECKING:
    from src.view.ui import ViewState


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
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        for index, option in enumerate(options):
            color = SELECTED_COLOR if index == selected_index else TEXT_COLOR
            item_y = start_y + TEXT_PAGE_BODY_TOP_OFFSET
            item_y += index * MENU_ITEM_SPACING
            self._draw_centered_text(
                option,
                item_y,
                TEXT_PAGE_BODY_FONT_SIZE,
                color,
            )
            if index == selected_index:
                option_width = ray.measure_text(
                    option,
                    TEXT_PAGE_BODY_FONT_SIZE,
                )
                option_x = (self._window_width - option_width) // 2
                marker_x = option_x - MENU_MARKER_GAP - MENU_MARKER_SIZE
                self._draw_pacman_marker(
                    marker_x,
                    item_y,
                )

        self._draw_centered_text(
            footer,
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_pacman_marker(self, x: int, y: int) -> None:
        """Draw the selected menu marker as a Pac-Man shape."""
        radius = MENU_MARKER_SIZE / 2
        center = ray.Vector2(
            x + radius,
            y + TEXT_PAGE_BODY_FONT_SIZE / 2,
        )
        mouth_height = radius * MENU_MARKER_MOUTH_RATIO

        ray.draw_circle(
            int(center.x),
            int(center.y),
            radius,
            SELECTED_COLOR,
        )
        ray.draw_triangle(
            center,
            ray.Vector2(center.x + radius, center.y - mouth_height),
            ray.Vector2(center.x + radius, center.y + mouth_height),
            BACKGROUND,
        )
