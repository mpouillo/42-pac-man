"""Background image rendering."""

from __future__ import annotations

from typing import Any

import pyray as ray

from src.constants import ASSETS_DIR

BACKGROUND_IMAGE_PATH = (
    ASSETS_DIR
    / "backgrounds"
    / "pacman_bg_blueprint_map_1600x900.png"
)


def load_arcade_background_texture() -> Any | None:
    """Load the optional shared background texture after window init."""
    if not BACKGROUND_IMAGE_PATH.is_file():
        return None

    return ray.load_texture(str(BACKGROUND_IMAGE_PATH))


def unload_arcade_background_texture(texture: Any | None) -> None:
    """Unload the shared background texture if it was loaded."""
    if texture is not None:
        ray.unload_texture(texture)


def draw_arcade_background(
    width: int,
    height: int,
    texture: Any | None = None,
) -> None:
    """Stretch the shared background image across the current window."""
    if width <= 0 or height <= 0 or texture is None:
        return

    ray.draw_texture_pro(
        texture,
        ray.Rectangle(
            0.0,
            0.0,
            float(texture.width),
            float(texture.height),
        ),
        ray.Rectangle(0.0, 0.0, float(width), float(height)),
        ray.Vector2(0.0, 0.0),
        0.0,
        ray.WHITE,
    )
