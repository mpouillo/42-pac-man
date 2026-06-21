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

# Shared text page typography and layout
TEXT_PAGE_START_Y_RATIO = 0.25
TEXT_PAGE_TITLE_FONT_SIZE = 70
TEXT_PAGE_BODY_FONT_SIZE = 40
TEXT_PAGE_BODY_TOP_OFFSET = 100
TEXT_PAGE_BODY_LINE_SPACING = 40
TEXT_PAGE_FOOTER_BOTTOM_OFFSET = 90

# Shared page titles and footer copy
MAIN_MENU_TITLE = "Pac-Man"
PAUSE_MENU_TITLE = "Paused"
HIGHSCORES_TITLE = "Highscores"
INSTRUCTIONS_TITLE = "Instructions"
GAME_OVER_TITLE = "GAME OVER"
WIN_TITLE = "YOU WIN!"
TEXT_PAGE_RETURN_FOOTER = "Press Enter or Escape to return"
MAIN_MENU_FOOTER = "Enter/click: select"
PAUSE_MENU_FOOTER = "Escape: resume   Enter: select"
SCORE_ENTRY_SAVE_FOOTER = "Enter: save score"
SCORE_ENTRY_SAVED_FOOTER = "Score saved. Press Enter or Escape to return"

# Shared menu content and action keys
MAIN_MENU_ACTION_START_GAME = "start_game"
MAIN_MENU_ACTION_HIGHSCORES = "highscores"
MAIN_MENU_ACTION_INSTRUCTIONS = "instructions"
MAIN_MENU_ACTION_EXIT = "exit"
PAUSE_MENU_ACTION_RESUME = "resume"
PAUSE_MENU_ACTION_INVINCIBILITY = "invincibility"
PAUSE_MENU_ACTION_GHOST_FREEZE = "ghost_freeze"
PAUSE_MENU_ACTION_SPEED_BOOST = "speed_boost"
PAUSE_MENU_ACTION_LEVEL_SKIP = "level_skip"
PAUSE_MENU_ACTION_MAIN_MENU = "main_menu"
MAIN_MENU_ITEMS = (
    ("Start Game", MAIN_MENU_ACTION_START_GAME),
    ("Highscores", MAIN_MENU_ACTION_HIGHSCORES),
    ("Instructions", MAIN_MENU_ACTION_INSTRUCTIONS),
    ("Exit", MAIN_MENU_ACTION_EXIT),
)
MAIN_MENU_OPTIONS = tuple(label for label, _action in MAIN_MENU_ITEMS)
MAIN_MENU_ACTIONS = tuple(action for _label, action in MAIN_MENU_ITEMS)
PAUSE_MENU_ITEMS = (
    ("Resume", PAUSE_MENU_ACTION_RESUME),
    ("Invincibility: {invincibility}", PAUSE_MENU_ACTION_INVINCIBILITY),
    ("Ghost Freeze: {ghost_freeze}", PAUSE_MENU_ACTION_GHOST_FREEZE),
    ("Speed Boost: {speed_boost}", PAUSE_MENU_ACTION_SPEED_BOOST),
    ("Level Skip", PAUSE_MENU_ACTION_LEVEL_SKIP),
    ("Return to Main Menu", PAUSE_MENU_ACTION_MAIN_MENU),
)
PAUSE_MENU_OPTION_TEMPLATES = tuple(
    label for label, _action in PAUSE_MENU_ITEMS
)
PAUSE_MENU_ACTIONS = tuple(action for _label, action in PAUSE_MENU_ITEMS)
MENU_ITEM_SPACING = 55
MENU_ITEM_HEIGHT = TEXT_PAGE_BODY_FONT_SIZE
MENU_MARKER_SIZE = TEXT_PAGE_BODY_FONT_SIZE
MENU_MARKER_GAP = 14
MENU_MARKER_MOUTH_RATIO = 0.6

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
WALL_MODEL_THICKNESS_SCALE = 1.0
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
HUD_FONT_SIZE = TEXT_PAGE_BODY_FONT_SIZE
