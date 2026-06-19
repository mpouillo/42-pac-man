"""Shared text and layout helpers for the view."""

from typing import Any

import pyray as ray

from src.view.constants import (
    INFO_CONTENT_OFFSET,
    INFO_PAGE_START_Y_RATIO,
)


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
        return self._info_page_start_y() + INFO_CONTENT_OFFSET

    def _info_page_start_y(self) -> int:
        """Return the shared vertical start for information pages."""
        return int(self._window_height * INFO_PAGE_START_Y_RATIO)
