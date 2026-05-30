"""Constants"""
from pathlib import Path

# Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
LEVELS_DIR = ASSETS_DIR / "levels"
CONFIG_FILE_PATH = PROJECT_ROOT / "config.json"

# Game data
STARTING_LIVES: int = 3
PACMAN_SPEED: float = 2.0
GHOST_SPEED: float = 1.0
