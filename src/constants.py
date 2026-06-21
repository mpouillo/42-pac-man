"""Constants"""
from pathlib import Path

import pyray as ray

# Path
PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
LEVELS_DIR = ASSETS_DIR / "levels"
CONFIG_FILE_PATH = PROJECT_ROOT / "config.json"

# Game data
STARTING_LIVES: int = 3
PACMAN_SPEED: float = 2.0
SPEED_BOOST_CHEAT: float = 2.0
GHOST_FLASH_THRESHOLD: float = 4.0
SPEED_FACTOR: float = 2.5

# Controller runtime
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Pac-Man"
TARGET_FPS = 60
END_SCREEN_DISPLAY_SECONDS = 3.0
PLAYER_NAME_MAX_LENGTH = 10

# UI colors
BACKGROUND = ray.Color(5, 5, 20, 255)
BOARD_BACKGROUND = ray.Color(0, 0, 0, 255)
TEXT_COLOR = ray.Color(240, 240, 240, 255)
MUTED_TEXT_COLOR = ray.Color(150, 150, 150, 255)
SELECTED_COLOR = ray.Color(255, 230, 0, 255)
OVERLAY_COLOR = ray.Color(0, 0, 0, 190)
ERROR_TEXT_COLOR = ray.Color(255, 80, 80, 255)

# Shared text and menu layout
MAIN_MENU_OPTIONS = (
    "Start Game",
    "Highscores",
    "Instructions",
    "Exit",
)
PAUSE_MENU_OPTION_TEMPLATES = (
    "Resume",
    "Invincibility: {invincibility}",
    "Ghost Freeze: {ghost_freeze}",
    "Speed Boost: {speed_boost}",
    "Level Skip",
    "Return to Main Menu",
)
INFO_PAGE_START_Y_RATIO = 0.25
INFO_CONTENT_OFFSET = 100
MENU_ITEM_SPACING = 55
MENU_ITEM_HEIGHT = 40
MENU_FOOTER_BOTTOM_OFFSET = 90
TITLE_FONT_SIZE = 70
CONTENT_FONT_SIZE = 40

# Score and instruction pages
HIGHSCORE_DISPLAY_LIMIT = 10
HIGHSCORE_QUERY_LIMIT = 1000
HIGHSCORE_LINE_SPACING = 36
INFO_PAGE_FOOTER_BOTTOM_OFFSET = 80
SCORE_ENTRY_CONTENT_OFFSET = 70
SCORE_ENTRY_LINE_SPACING = 32
SCORE_ENTRY_NAME_BOTTOM_OFFSET = 180
SCORE_ENTRY_ERROR_BOTTOM_OFFSET = 140
SCORE_ENTRY_FOOTER_BOTTOM_OFFSET = 90
INSTRUCTION_LINE_SPACING = 34

# 3D scene
CELL_SIZE_3D = 1.0

# FOV
DEFAULT_FOV = 100.0
AUTO_FOV_SCALE = 1.5
AUTO_FOV_PADDING = 15.0
FOV_MIN = 30.0
FOV_MAX = 120.0
FOV_SPEED = 60.0

# Camera
CAMERA_POSITION = (0.0, 15.0, 20.0)
CAMERA_TARGET = (0.0, 0.0, 0.0)
CAMERA_UP = (0.0, 1.0, 0.0)

# Wall
WALL_MODEL_DIR = Path(__file__).resolve().parents[1] / "assets" / "walls"
WALL_MODEL_FILE_PREFIX = "wall_"
WALL_MODEL_EXTENSION = ".glb"
WALL_MODEL_WIDTH_SCALE = 1.0
WALL_MODEL_HEIGHT_SCALE = 0.6

# Entity assets
ENTITY_MODEL_DIR = Path(__file__).resolve().parents[1] / "assets" / "entities"
ENTITY_MODEL_EXTENSION = ".glb"
ENTITY_MODEL_FILES = {
    "pacman": "pacman",
    "pacgum": "pacgum",
    "super_pacgum": "super_pacgum",
    "ghost_red": "ghost_red",
    "ghost_pink": "ghost_pink",
    "ghost_cyan": "ghost_cyan",
    "ghost_orange": "ghost_orange",
    "ghost_respawn": "ghost_respawn",
}
PACGUM_MODEL_SCALE = 1.0
PACMAN_MODEL_SCALE = 1.0
GHOST_MODEL_SCALE = 1.0
PACMAN_MODEL_HEIGHT = 0.35
GHOST_MODEL_HEIGHT = 0.36

# Ghost animation
GHOST_TILT_SPEED = 4.5
GHOST_TILT_DEGREES = 4.0
RESPAWN_GHOST_TILT_SPEED = 8.0
RESPAWN_GHOST_TILT_DEGREES = 7.0
GHOST_RED_TILT_PHASE = 0.0
GHOST_PINK_TILT_PHASE = 0.7
GHOST_BLUE_TILT_PHASE = 1.4
GHOST_ORANGE_TILT_PHASE = 2.1

# HUD
HUD_HORIZONTAL_PADDING = 24
HUD_TOP_OFFSET = 22
