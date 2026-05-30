from typing import List

from constants import STARTING_LIVES
from protocols import (
    CellState,
    CheatType,
    Direction,
    GamePhase,
    GhostData,
    GhostType,
    HighscoreEntry,
    ModelProtocol,
    PacmanData
)
from src.model.ghost import Ghost
from src.model.level import Level
from src.model.pacman import Pacman


class GameModel(ModelProtocol):
    def __init__(self) -> None:
        self._phase: GamePhase = GamePhase.MAIN_MENU
        self._level: Level = Level()
        self._pacman: Pacman = Pacman()
        self._ghosts: List[Ghost] = [Ghost(GhostType(i)) for i in range(1, 4)]

        self._score: int = 0
        self._lives: int = STARTING_LIVES
        self._time: int = self._level.time_limit

    def get_game_phase(self) -> GamePhase:
        return self._phase

    def set_game_phase(self, phase: GamePhase) -> None:
        self._phase = phase

    def get_current_level(self) -> int:
        return self._level.id if self._level else 0

    def get_remaining_time(self) -> float:
        return self._time

    def get_pacman(self) -> PacmanData:
        return self._pacman.data

    def get_ghosts(self) -> list[GhostData]:
        pass

    def get_maze(self) -> list[list[CellState]]:
        pass

    def get_score(self) -> int:
        pass

    def get_lives(self) -> int:
        pass

    def is_game_over(self) -> bool:
        pass

    def update(self, delta_time: float) -> None:
        pass

    def set_player_input(self, direction: Direction) -> None:
        pass

    def get_top_scores(self) -> list[HighscoreEntry]:
        pass

    def submit_score(self, player_name: str) -> bool:
        pass

    def trigger_cheat(self, cheat: CheatType) -> None:
        pass
