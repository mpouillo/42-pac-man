from typing import List

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
from src.config import ConfigData
from src.highscore import HighscoreManager
from src.model.ghost import Ghost
from src.model.level import Level
from src.model.pacman import Pacman


class GameModel(ModelProtocol):
    def __init__(self, config: ConfigData) -> None:
        self._config = config
        self._phase: GamePhase = GamePhase.MAIN_MENU
        self._level: Level = Level()
        self._highscore_manager = HighscoreManager(config.highscore_filename)
        self._pacman: Pacman = Pacman()
        self._ghosts: List[Ghost] = [
            Ghost(ghost, self._level.data.difficulty_settings.ghost_speed
                  if self._level.data else 1.0)
            for ghost in list(GhostType)
        ]

        self._score: int = 0
        self._lives: int = config.lives
        self._time: float = (
            self._level.data.time_limit if self._level.data else 0.0
        )

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

    def set_player_input(self, direction: Direction) -> None:
        self._pacman.direction = direction

    def get_top_scores(self) -> list[HighscoreEntry]:
        return self._highscore_manager.get_top_scores(10)

    def submit_score(self, player_name: str) -> bool:
        try:
            entry = HighscoreEntry(name=player_name, score=self._score)
        except ValueError:
            return False

        self._highscore_manager.add_entry(entry)
        self._highscore_manager.save_scores()
        return True

    def trigger_cheat(self, cheat: CheatType) -> None:
        pass

    def update(self, delta_time: float) -> None:
        self._pacman.update(delta_time)

        ghost_info = {
            ghost.type: {
                "position": (ghost.y, ghost.x),
                "target": ghost._target_tile
            }
            for ghost in self._ghosts
        }

        for ghost in self._ghosts:
            ghost.update(
                delta_time, self._level, self.get_pacman(), ghost_info
            )
