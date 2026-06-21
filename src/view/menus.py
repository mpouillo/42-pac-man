"""Main and pause menu rendering."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Callable

import pyray as ray

from src.constants import (
    MAIN_MENU_OPTIONS,
    MENU_MARKER_FLOAT_DISTANCE,
    MENU_MARKER_FLOAT_SPEED,
    MENU_MARKER_GAP,
    MENU_MARKER_PULSE_SPEED,
    MENU_MARKER_PULSE_STRENGTH,
    MENU_MARKER_SIZE,
    MENU_ITEM_HEIGHT,
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

    def get_menu_index_at_position(
        self,
        mouse_x: int,
        mouse_y: int,
        options: Sequence[str],
    ) -> int | None:
        """Return the menu index only when the mouse is over option text."""
        for index, option in enumerate(options):
            item_x, item_y, item_width = self._menu_item_text_bounds(
                option,
                index,
            )
            if (
                item_x <= mouse_x <= item_x + item_width
                and item_y <= mouse_y <= item_y + MENU_ITEM_HEIGHT
            ):
                return index

        return None

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
            option_x, item_y, _ = self._menu_item_text_bounds(
                option,
                index,
            )
            self._draw_centered_text(
                option,
                item_y,
                TEXT_PAGE_BODY_FONT_SIZE,
                color,
            )
            if index == selected_index:
                marker_x = option_x - MENU_MARKER_GAP - MENU_MARKER_SIZE
                self._draw_menu_marker(
                    marker_x,
                    item_y,
                )

        self._draw_centered_text(
            footer,
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _menu_item_text_bounds(
        self,
        option: str,
        index: int,
    ) -> tuple[int, int, int]:
        """Return x, y, and width for a centered menu option."""
        option_width = ray.measure_text(
            option,
            TEXT_PAGE_BODY_FONT_SIZE,
        )
        option_x = (self._window_width - option_width) // 2
        option_y = self._info_page_start_y() + TEXT_PAGE_BODY_TOP_OFFSET
        option_y += index * MENU_ITEM_SPACING
        return option_x, option_y, option_width

    def _draw_menu_marker(self, x: int, y: int) -> None:
        """Draw the selected menu marker as a shared animated arrow."""
        elapsed = ray.get_time()
        marker_offset = math.sin(elapsed * MENU_MARKER_FLOAT_SPEED)
        marker_offset *= MENU_MARKER_FLOAT_DISTANCE
        pulse = (math.sin(elapsed * MENU_MARKER_PULSE_SPEED) + 1.0) / 2.0

        marker_size = float(MENU_MARKER_SIZE)
        marker_x = float(x) + marker_offset
        center_y = float(y) + TEXT_PAGE_BODY_FONT_SIZE / 2.0
        half_height = marker_size * 0.36
        tip_x = marker_x + marker_size

        shadow_color = ray.Color(
            SELECTED_COLOR.r,
            SELECTED_COLOR.g,
            SELECTED_COLOR.b,
            70,
        )
        marker_color = self._menu_marker_color(pulse)

        self._draw_marker_triangle(
            marker_x - 4.0,
            tip_x - 4.0,
            center_y,
            half_height,
            shadow_color,
        )
        self._draw_marker_triangle(
            marker_x,
            tip_x,
            center_y,
            half_height,
            marker_color,
        )

    def _menu_marker_color(self, pulse: float) -> Any:
        """Return the marker color with a soft brightness pulse."""
        mix = pulse * MENU_MARKER_PULSE_STRENGTH
        return ray.Color(
            self._mix_color_channel(SELECTED_COLOR.r, 255, mix),
            self._mix_color_channel(SELECTED_COLOR.g, 255, mix),
            self._mix_color_channel(SELECTED_COLOR.b, 120, mix),
            255,
        )

    @staticmethod
    def _mix_color_channel(start: int, end: int, amount: float) -> int:
        """Linearly mix one color channel."""
        return int(start + (end - start) * amount)

    @staticmethod
    def _draw_marker_triangle(
        left_x: float,
        tip_x: float,
        center_y: float,
        half_height: float,
        color: Any,
    ) -> None:
        """Draw a right-facing triangular marker."""
        ray.draw_triangle(
            ray.Vector2(tip_x, center_y),
            ray.Vector2(left_x, center_y - half_height),
            ray.Vector2(left_x, center_y + half_height),
            color,
        )
