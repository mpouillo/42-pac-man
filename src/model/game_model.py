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
from src.highscore import HighscoreManager
from src.model.ghost import Ghost
from src.model.level import Level
from src.model.pacman import Pacman


class GameModel(ModelProtocol):
    def __init__(self) -> None:
        self._phase: GamePhase = GamePhase.MAIN_MENU
        self._level: Level = Level()
        self._highscores = HighscoreManager()
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
        return [ghost.data for ghost in self._ghosts]

    def get_maze(self) -> list[list[CellState]]:
        return self._level.grid

    def get_score(self) -> int:
        return self._score

    def get_lives(self) -> int:
        return self._lives

    def is_game_over(self) -> bool:
        return self._level.pacgums == 0 or self._lives == 0

    def update(self, delta_time: float) -> None:
        pass

    def set_player_input(self, direction: Direction) -> None:
        pass

    def get_top_scores(self) -> list[HighscoreEntry]:
        return self._highscores.get_top_scores(10)

    def submit_score(self, player_name: str) -> bool:
        return self._highscores.add_entry(player_name, self._score)

    def trigger_cheat(self, cheat: CheatType) -> None:
        pass
