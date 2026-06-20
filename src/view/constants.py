"""Constants used by the Pac-Man view."""

from pathlib import Path

import pyray as ray

from src.view.wall_shapes import WallAssetKind


BACKGROUND = ray.Color(5, 5, 20, 255)
BOARD_BACKGROUND = ray.Color(0, 0, 0, 255)
WALL_COLOR = ray.Color(20, 40, 180, 255)
PACGUM_COLOR = ray.Color(240, 220, 160, 255)
SUPER_PACGUM_COLOR = ray.Color(255, 255, 255, 255)
PACMAN_COLOR = ray.Color(255, 220, 0, 255)
TEXT_COLOR = ray.Color(240, 240, 240, 255)
MUTED_TEXT_COLOR = ray.Color(150, 150, 150, 255)
SELECTED_COLOR = ray.Color(255, 230, 0, 255)
OVERLAY_COLOR = ray.Color(0, 0, 0, 190)
FRIGHTENED_COLOR = ray.Color(40, 80, 255, 255)
FLASHING_COLOR = ray.Color(255, 255, 255, 255)

INFO_PAGE_START_Y_RATIO = 0.25
INFO_CONTENT_OFFSET = 100
MENU_ITEM_SPACING = 44
MENU_ITEM_HEIGHT = 40
TITLE_FONT_SIZE = 48
CONTENT_FONT_SIZE = 30

AUTO_FOV_SCALE = 1.5
AUTO_FOV_PADDING = 15.0
FOV_MIN = 30.0
FOV_MAX = 120.0
FOV_SPEED = 60.0

WALL_MODEL_DIR = Path(__file__).resolve().parents[2] / "assets" / "walls"
WALL_MODEL_FILES = {
    asset_kind: f"wall_{asset_kind.value}"
    for asset_kind in WallAssetKind
}
WALL_MODEL_EXTENSIONS = (".glb", ".obj", ".gltf")
WALL_MODEL_SCALE = 1.0

ENTITY_MODEL_DIR = Path(__file__).resolve().parents[2] / "assets" / "entities"
ENTITY_MODEL_EXTENSIONS = (".glb", ".obj", ".gltf")

ENTITY_MODEL_FILES = {
    "pacgum": "pacgum",

    "pacman": "pacman",
    "pacman_closed": "pacman_closed",
    "pacman_half": "pacman_half",
    "pacman_open": "pacman_open",

    "ghost_red": "ghost_red",
    "ghost_pink": "ghost_pink",
    "ghost_cyan": "ghost_cyan",
    "ghost_orange": "ghost_orange",
    "ghost_respawn": "ghost_respawn",
}

PACGUM_MODEL_SCALE = 1.0
PACMAN_MODEL_SCALE = 1.0
GHOST_MODEL_SCALE = 1.0

PACMAN_ANIMATION_FPS = 9.0

GHOST_TILT_SPEED = 4.5
GHOST_TILT_DEGREES = 4.0

RESPAWN_GHOST_TILT_SPEED = 8.0
RESPAWN_GHOST_TILT_DEGREES = 7.0
