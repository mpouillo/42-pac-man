from typing import Protocol
from dataclasses import dataclass
from enum import Enum


class GamePhase(Enum):
    MAIN_MENU = 1
    HIGHSCORES_MENU = 2
    INSTRUCTIONS_MENU = 3
    PLAYING = 4
    PAUSED = 5
    GAME_OVER = 6
    WIN = 7


class CheatType(Enum):
    INVINCIBILITY = 1
    LEVEL_SKIP = 2
    GHOST_FREEZE = 3
    SPEED_BOOST = 4
    WALL_JUMP = 5


class Direction(Enum):
    """(x, y)"""
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    NONE = (0, 0)


class CellState(Enum):
    EMPTY = 0
    WALL = 1
    PACGUM = 2
    SUPER_PACGUM = 3


class PacmanState(Enum):
    IDLE = 1
    ALIVE = 2
    POWERED = 3
    DEAD = 4


class GhostState(Enum):
    IDLE = 1
    CHASE = 2
    SCATTER = 3
    DEAD = 4


class GhostType(Enum):
    PINK = "Pinky"
    RED = "Blinky"
    ORANGE = "Clyde"
    BLUE = "Inky"


@dataclass
class EntityData:
    x: float
    y: float
    direction: Direction


@dataclass
class GhostData(EntityData):
    type: GhostType
    state: GhostState


@dataclass
class PacmanData(EntityData):
    state: PacmanState


@dataclass
class HighscoreEntry:
    name: str
    score: int


class ModelProtocol(Protocol):
    def get_game_phase(self) -> GamePhase:
        """Tells the View which screen (Menu, Playing, Game Over) to draw."""
        ...

    def set_game_phase(self, phase: GamePhase) -> None:
        """Allows the Controller to change screens (e.g., clicking 'Start')."""
        ...

    def get_current_level(self) -> int:
        """Required for the HUD."""
        ...

    def get_remaining_time(self) -> float:
        """Returns remaining seconds for the level (Required for the HUD)."""
        ...

    def get_pacman(self) -> PacmanData:
        """Returns the player's current exact position and facing direction."""
        ...

    def get_ghosts(self) -> list[GhostData]:
        """Returns the state and position of all 4 ghosts."""
        ...

    def get_maze(self) -> list[list[CellState]]:
        """Returns the current grid."""
        ...

    def get_score(self) -> int:
        ...

    def get_lives(self) -> int:
        ...

    def is_game_over(self) -> bool:
        ...

    def update(self, delta_time: float) -> None:
        """Advances the game simulation by the given time step."""
        ...

    def set_player_input(self, direction: Direction) -> None:
        """Registers the player's intended movement for the next frame."""
        ...

    def get_top_scores(self) -> list[HighscoreEntry]:
        """Returns the top 10 scores to be displayed in the menu."""
        ...

    def submit_score(self, player_name: str) -> bool:
        """
        Saves a new highscore to disk if valid.
        Returns True if successful.
        """
        ...

    def trigger_cheat(self, cheat: CheatType) -> None:
        """Instantly mutates game rules depending on cheat type."""
        ...


class ViewProtocol(Protocol):
    def initialize(self, window_width: int, window_height: int) -> None:
        """Sets up the Raylib window, loads 3D models, textures, and sounds."""
        ...

    def render(self, model: ModelProtocol) -> None:
        """
        Reads the model state and draws the frame.
        Internally, this should call Raylib's BeginMode3D() for the main game,
        then switch to 2D drawing for the minimap and HUD.
        """
        ...

    def shutdown(self) -> None:
        """Unloads Raylib assets from VRAM and closes the window safely."""
        ...


class ControllerProtocol(Protocol):
    def run(self) -> None:
        ...
