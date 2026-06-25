"""Constants"""
from pathlib import Path

import pyray as ray

# Paths
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

# Game data
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
TEXT_COLOR = ray.Color(240, 240, 240, 255)
MUTED_TEXT_COLOR = ray.Color(150, 150, 150, 255)
SELECTED_COLOR = ray.Color(255, 230, 0, 255)
OVERLAY_COLOR = ray.Color(0, 0, 0, 190)
MAIN_MENU_CHASE_OVERLAY_COLOR = ray.Color(0, 0, 0, 40)
ERROR_TEXT_COLOR = ray.Color(255, 80, 80, 255)

# Shared text page typography and layout
TEXT_PAGE_START_Y_RATIO = 0.25
TEXT_PAGE_TITLE_FONT_SIZE = 70
TEXT_PAGE_BODY_FONT_SIZE = 40
TEXT_PAGE_BODY_TOP_OFFSET = 100
TEXT_PAGE_BODY_LINE_SPACING = 40
TEXT_PAGE_FOOTER_BOTTOM_OFFSET = 90

# Shared page copy
HIGHSCORES_TITLE = "Highscores"
TEXT_PAGE_RETURN_FOOTER = "Press Enter or Escape to return"

# Shared menu content
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
MENU_ITEM_SPACING = 55
MENU_MARKER_SIZE = TEXT_PAGE_BODY_FONT_SIZE
MENU_MARKER_GAP = 14
MENU_MARKER_FLOAT_DISTANCE = 8.0
MENU_MARKER_FLOAT_SPEED = 5.0
MENU_MARKER_PULSE_SPEED = 4.0
MENU_MARKER_PULSE_STRENGTH = 0.35

# Score and instruction pages
HIGHSCORE_DISPLAY_LIMIT = 10
HIGHSCORE_QUERY_LIMIT = 1000
SCORE_ENTRY_NAME_BOTTOM_OFFSET = 180
SCORE_ENTRY_ERROR_BOTTOM_OFFSET = 140
SCORE_ENTRY_CURRENT_SCORE_SCALE = 1.5
SCORE_ENTRY_CURSOR_BLINK_SECONDS = 0.5
SCORE_ENTRY_CURSOR_GAP = 6
INSTRUCTION_LINES = (
    "Arrow keys or WASD: move Pac-Man",
    "Escape: pause or resume",
    "Enter: confirm menu selection",
    "F/R: adjust camera FOV",
    "Pause menu: cheat options for testing",
    "",
    "Eat all pacgums to complete the level.",
    "Super pacgums make ghosts edible for a short time.",
    "Avoid ghosts when they are not edible.",
)

# 3D scene
CELL_SIZE_3D = 1.0
MAZE_FLOOR_HEIGHT = 0.08
MAZE_FLOOR_COLOR = ray.Color(6, 18, 68, 150)

# FOV
DEFAULT_FOV = 100.0
AUTO_FOV_SCALE = 1.5
AUTO_FOV_PADDING = 15.0
FOV_MIN = 30.0
FOV_MAX = 120.0
FOV_SPEED = 60.0

# Camera
CAMERA_POSITION = (0.0, 20.0, 20.0)
CAMERA_TARGET = (0.0, 0.0, 0.0)
CAMERA_UP = (0.0, 1.0, 0.0)

# Wall
WALL_MODEL_DIR = ASSETS_DIR / "walls"
WALL_MODEL_FILE_PREFIX = "wall_"
WALL_MODEL_THICKNESS_SCALE = 1.0
WALL_MODEL_HEIGHT_SCALE = 0.6

# Entity assets
ENTITY_MODEL_DIR = ASSETS_DIR / "entities"
MODEL_EXTENSION = ".glb"
ENTITY_MODEL_FILES = {
    "pacman": "pacman",
    "pacgum": "pacgum",
    "super_pacgum": "super_pacgum",
    "ghost_red": "ghost_red",
    "ghost_pink": "ghost_pink",
    "ghost_cyan": "ghost_cyan",
    "ghost_orange": "ghost_orange",
    "ghost_frightened": "ghost_frightened",
    "ghost_respawn": "ghost_respawn",
}
PACGUM_MODEL_SCALE = 1.0
PACMAN_MODEL_SCALE = 1.0
GHOST_MODEL_SCALE = 1.0
PACMAN_MODEL_HEIGHT = 0.35
GHOST_MODEL_HEIGHT = 0.36

# Entity animation
ENTITY_SWAY_SPEED = 4.5
ENTITY_SWAY_DEGREES = 10.0

# HUD
HUD_HORIZONTAL_PADDING = 24
HUD_TOP_OFFSET = 22
HUD_FONT_SIZE = TEXT_PAGE_BODY_FONT_SIZE
