from typing import Protocol
from dataclasses import dataclass
from enum import Enum, auto


class GamePhase(Enum):
    MAIN_MENU = auto()
    HIGHSCORES_MENU = auto()
    INSTRUCTIONS_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    WIN = auto()


class CheatType(Enum):
    INVINCIBILITY = auto()
    LEVEL_SKIP = auto()
    GHOST_FREEZE = auto()
    SPEED_BOOST = auto()
    WALL_JUMP = auto()


class Direction(Enum):
    """(x, y)"""
    UP = (0, -1)
    LEFT = (-1, 0)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    NONE = (0, 0)


class CellState(Enum):
    EMPTY = auto()
    WALL = auto()
    PACGUM = auto()
    SUPER_PACGUM = auto()


class GhostState(Enum):
    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class PacmanState(Enum):
    ALIVE = auto()
    POWERED = auto()
    DEAD = auto()


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

    def toggle_cheat(self, cheat: CheatType) -> None:
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
