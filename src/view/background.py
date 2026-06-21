"""Background image rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyray as ray

BACKGROUND_IMAGE_DIR = (
    Path(__file__).resolve().parents[2] / "assets" / "backgrounds"
)
BACKGROUND_IMAGE_PATHS = (
    BACKGROUND_IMAGE_DIR / "maze_route_background.png",
    BACKGROUND_IMAGE_DIR / "maze_route_background.jpg",
    BACKGROUND_IMAGE_DIR / "maze_route_background.jpeg",
    BACKGROUND_IMAGE_DIR / "maze_route_background.webp",
)
BACKGROUND_MENU_TINT = ray.Color(255, 255, 255, 255)
BACKGROUND_GAME_TINT = ray.Color(255, 255, 255, 235)


def load_arcade_background_texture() -> Any | None:
    """Load the optional shared background texture after window init."""
    path = _background_image_path()
    if path is None:
        return None

    return ray.load_texture(str(path))


def unload_arcade_background_texture(texture: Any | None) -> None:
    """Unload the shared background texture if it was loaded."""
    if texture is not None:
        ray.unload_texture(texture)


def draw_arcade_background(
    width: int,
    height: int,
    mode: str = "game",
    texture: Any | None = None,
) -> None:
    """Draw the shared arcade background image behind all game elements."""
    if width <= 0 or height <= 0 or texture is None:
        return

    source = _cover_source_rect(texture, width, height)
    tint = BACKGROUND_MENU_TINT if mode == "menu" else BACKGROUND_GAME_TINT

    ray.draw_texture_pro(
        texture,
        source,
        ray.Rectangle(0.0, 0.0, float(width), float(height)),
        ray.Vector2(0.0, 0.0),
        0.0,
        tint,
    )


def _cover_source_rect(
    texture: Any,
    width: int,
    height: int,
) -> Any:
    """Return a centered source rect that covers the target screen."""
    texture_width = float(texture.width)
    texture_height = float(texture.height)
    target_ratio = width / height
    texture_ratio = texture_width / texture_height

    if texture_ratio > target_ratio:
        source_height = texture_height
        source_width = texture_height * target_ratio
        source_x = (texture_width - source_width) / 2.0
        source_y = 0.0
    else:
        source_width = texture_width
        source_height = texture_width / target_ratio
        source_x = 0.0
        source_y = (texture_height - source_height) / 2.0

    return ray.Rectangle(
        source_x,
        source_y,
        source_width,
        source_height,
    )


def _background_image_path() -> Path | None:
    """Return the configured background image path when an asset exists."""
    for path in BACKGROUND_IMAGE_PATHS:
        if path.exists():
            return path

    if not BACKGROUND_IMAGE_DIR.exists():
        return None

    for path in sorted(BACKGROUND_IMAGE_DIR.iterdir()):
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            return path

    return None
