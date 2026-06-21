"""Main and pause menu rendering."""
# mypy: disable-error-code="attr-defined,no-untyped-def"

from __future__ import annotations

import math
from collections.abc import Sequence

import pyray as ray

from src.constants import (
    MAIN_MENU_OPTIONS,
    MENU_MARKER_FLOAT_DISTANCE,
    MENU_MARKER_FLOAT_SPEED,
    MENU_MARKER_GAP,
    MENU_MARKER_PULSE_SPEED,
    MENU_MARKER_PULSE_STRENGTH,
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
                and item_y
                <= mouse_y
                <= item_y + TEXT_PAGE_BODY_FONT_SIZE
            ):
                return index

        return None

    def _draw_main_menu(self, state) -> None:
        """Draw the main menu."""
        self._draw_menu(
            title="Pac-Man",
            options=MAIN_MENU_OPTIONS,
            selected_index=state.main_menu_index,
            footer="Enter/click: select",
        )

    def _draw_pause_menu(self, state) -> None:
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
        mix = pulse * MENU_MARKER_PULSE_STRENGTH
        marker_color = ray.Color(
            int(SELECTED_COLOR.r + (255 - SELECTED_COLOR.r) * mix),
            int(SELECTED_COLOR.g + (255 - SELECTED_COLOR.g) * mix),
            int(SELECTED_COLOR.b + (120 - SELECTED_COLOR.b) * mix),
            255,
        )

        ray.draw_triangle(
            ray.Vector2(tip_x - 4.0, center_y),
            ray.Vector2(marker_x - 4.0, center_y - half_height),
            ray.Vector2(marker_x - 4.0, center_y + half_height),
            shadow_color,
        )
        ray.draw_triangle(
            ray.Vector2(tip_x, center_y),
            ray.Vector2(marker_x, center_y - half_height),
            ray.Vector2(marker_x, center_y + half_height),
            marker_color,
        )
