from typing import Protocol

from src.highscore import HighscoreEntry
from src.types.dataclasses import GhostData, PacmanData
from src.types.enums import CellState, CheatType, Direction, GamePhase


class ModelProtocol(Protocol):
    """Define the state management and execution logic for the game loop."""

    def get_game_phase(self) -> GamePhase:
        """Retrieve the active game phase determining the current view."""
        ...

    def set_game_phase(self, phase: GamePhase) -> None:
        """Transition the game engine loop to a new operational phase."""
        ...

    def get_current_level(self) -> int:
        """Return the current level index for tracking and rendering."""
        ...

    def get_remaining_time(self) -> float:
        """Return the remaining level time limit in seconds."""
        ...

    def get_pacman(self) -> PacmanData:
        """Get the current positional and state data for Pacman."""
        ...

    def get_ghosts(self) -> list[GhostData]:
        """Get the positional and state data for all active ghosts."""
        ...

    def get_grid(self) -> list[list[CellState]]:
        """Retrieve the structural grid layout matrix of the level."""
        ...

    def get_score(self) -> int:
        """Get the current running score accumulated by the player."""
        ...

    def get_lives(self) -> int:
        """Get the number of remaining lives available to the player."""
        ...

    def is_game_over(self) -> bool:
        """Determine whether a game over criteria has been reached."""
        ...

    def update(self, delta_time: float) -> None:
        """Advance the game simulation logic by the given time step."""
        ...

    def set_player_input(self, direction: Direction) -> None:
        """Queue the player's intended input direction for processing."""
        ...

    def get_top_scores(self, amount: int) -> list[HighscoreEntry]:
        """Retrieve a specified number of sorted highscore entries."""
        ...

    def submit_score(self, player_name: str) -> bool:
        """Save a score entry to storage if it qualifies as valid."""
        ...

    def toggle_cheat(self, cheat: CheatType) -> None:
        """Toggle a game engine modifier based on the cheat type."""
        ...


class ViewProtocol(Protocol):
    """Interface handling graphic engine contexts and hardware rendering."""

    def initialize(self, window_width: int, window_height: int) -> None:
        """Initialize window dimensions, graphics pipelines, and assets."""
        ...

    def render(self, model: ModelProtocol) -> None:
        """Read the model state data and draw the current frame.

        This evaluates 3D world space elements before rendering 2D
        overlays like HUD maps and screen menus.
        """
        ...

    def shutdown(self) -> None:
        """Deallocate graphic assets from memory and close the display."""
        ...


class ControllerProtocol(Protocol):
    """Interface managing user input mapping and runtime coordination."""

    def run(self) -> None:
        """Start and maintain the core application and execution loop."""
        ...
