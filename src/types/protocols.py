from typing import Protocol

from src.highscore import HighscoreEntry
from src.types.dataclasses import GhostData, PacmanData
from src.types.enums import CellState, CheatType, Direction, GamePhase


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

    def get_grid(self) -> list[list[CellState]]:
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

    def get_top_scores(self, amount: int) -> list[HighscoreEntry]:
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
