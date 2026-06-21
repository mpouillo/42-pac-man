import math
from typing import List

from pydantic import ValidationError

from src.constants import SPEED_BOOST_CHEAT
from src.config import ConfigData
from src.highscore import HighscoreEntry, HighscoreManager
from src.model.ghost import Ghost
from src.model.level import Level
from src.model.pacman import Pacman
from src.types.dataclasses import GhostData, PacmanData
from src.types.enums import (
    CellState,
    CheatType,
    Direction,
    GamePhase,
    GhostState,
    GhostType
)
from src.types.protocols import ModelProtocol


class GameModel(ModelProtocol):
    def __init__(self, config: ConfigData) -> None:
        self._config = config

        self._level_id: int = 0
        self._level: Level = Level(config.levels[self._level_id])

        self._phase: GamePhase = GamePhase.MAIN_MENU
        self._cheats: List[CheatType] = []
        self._highscore_manager = HighscoreManager(config.highscores)
        self._pacman: Pacman = Pacman(self._level)
        self._ghosts: List[Ghost] = [
            Ghost(ghost, self._level) for ghost in list(GhostType)
        ]

        self._score: int = 0
        self._lives: int = config.lives
        self._level_timer: float = self._level.data.time_limit
        self._animation_timer: float = 0.0

    def get_game_phase(self) -> GamePhase:
        return self._phase

    def set_game_phase(self, phase: GamePhase) -> None:
        self._phase = phase

    def get_current_level(self) -> int:
        return self._level_id

    def get_remaining_time(self) -> float:
        return self._level_timer

    def get_pacman(self) -> PacmanData:
        return self._pacman.data

    def get_ghosts(self) -> list[GhostData]:
        return [ghost.data for ghost in self._ghosts]

    def get_grid(self) -> list[list[CellState]]:
        return self._level.grid

    def get_score(self) -> int:
        return self._score

    def get_lives(self) -> int:
        return self._lives

    def is_game_over(self) -> bool:
        return self._phase == GamePhase.GAME_OVER

    def set_player_input(self, direction: Direction) -> None:
        # Instantly set direction if opposite of current
        if self._pacman.direction.opposite == direction:
            self._pacman.direction = direction
            return

        # Save direction in buffer
        self._pacman.queued_direction = direction

    def get_top_scores(self, amount: int) -> list[HighscoreEntry]:
        return self._highscore_manager.get_top_scores(amount)

    def submit_score(self, player_name: str) -> bool:
        try:
            entry = HighscoreEntry(name=player_name, score=self._score)
        except ValidationError:
            return False

        self._highscore_manager.add_entry(entry)
        self._highscore_manager.save_scores()
        return True

    def toggle_cheat(self, cheat: CheatType) -> None:
        if cheat == CheatType.LEVEL_SKIP:
            self._win_round()
            return

        if cheat in self._cheats:
            self._cheats.remove(cheat)
            return

        self._cheats.append(cheat)

    def update(self, delta_time: float) -> None:
        if self._phase == GamePhase.MAIN_MENU:
            return
        elif self._phase == GamePhase.HIGHSCORES_MENU:
            return
        elif self._phase == GamePhase.INSTRUCTIONS_MENU:
            return
        elif self._phase == GamePhase.PLAYING:
            self._level_timer -= delta_time

            if self._lives <= 0:
                self._phase = GamePhase.GAME_OVER
            if self._level.pacgums == 0:
                self._win_round()
            if self._level_timer <= 0:
                self._lose_round()

            self._pacman_actions(delta_time)
            self._ghost_actions(delta_time)
            self._check_collisions()
        elif self._phase == GamePhase.PAUSED:
            return
        elif self._phase == GamePhase.GAME_OVER:
            self._ghost_actions(delta_time)
            return

    def _win_round(self) -> None:
        # If at last level
        # if len(self._config.levels) - 1 >= self._level_id:
        if self._level_id >= len(self._config.levels) - 1:
            self._phase = GamePhase.WIN
            return

        self._level_id += 1
        self._level = Level(self._config.levels[self._level_id])
        self._reset()

    def _lose_round(self) -> None:
        self._lives -= 1
        self._reset()
        if self._lives == 0:
            self._phase = GamePhase.GAME_OVER

    def _pacman_actions(self, delta_time: float) -> None:
        pos = (round(self._pacman.x), round(self._pacman.y))
        match self._level.grid[pos[1]][pos[0]]:
            case CellState.PACGUM:
                self._level.update_cell(*pos, CellState.EMPTY)
                self._score += self._config.points_per_pacgum
            case CellState.SUPER_PACGUM:
                self._level.update_cell(*pos, CellState.EMPTY)
                self._score += self._config.points_per_super_pacgum
                for ghost in self._ghosts:
                    if not ghost.state == GhostState.EATEN:
                        ghost.frighten(
                            self._level.data.difficulty.fear_duration,
                            self.get_pacman()
                        )

        if CheatType.SPEED_BOOST in self._cheats:
            delta_time *= SPEED_BOOST_CHEAT

        self._pacman.update(delta_time)

    def _ghost_actions(self, delta_time: float) -> None:
        """Update Ghost positions."""
        if CheatType.GHOST_FREEZE in self._cheats:
            return

        red_ghost = next(
            (ghost.data for ghost in self._ghosts
             if ghost.type == GhostType.RED)
        )

        for ghost in self._ghosts:
            ghost.update(delta_time, self.get_pacman(), red_ghost)

    def _check_collisions(self) -> None:
        for ghost in self._ghosts:
            if self._did_collide(ghost):
                if ghost.state.is_edible:
                    self._score += self._config.points_per_ghost
                    ghost.die()
                elif ghost.state.is_lethal:
                    if CheatType.INVINCIBILITY in self._cheats:
                        continue
                    self._lose_round()
                    return

    def _did_collide(self, ghost: Ghost) -> bool:
        """
        Check for collisions (distance < 0.5)
        between Pac-Man and Ghosts.
        """
        ghost_pos = [ghost.x, ghost.y]
        pacman_pos = [self._pacman.x, self._pacman.y]
        if math.dist(ghost_pos, pacman_pos) < 0.5:
            return True
        return False

    def _reset(self) -> None:
        """Reset values and restart game."""
        self._phase = GamePhase.PLAYING
        self._level_timer = self._level.data.time_limit
        self._pacman = Pacman(self._level)
        self._ghosts = [Ghost(ghost, self._level) for ghost in list(GhostType)]
