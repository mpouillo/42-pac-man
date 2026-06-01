import math
from typing import List

from constants import SPEED_BOOST_CHEAT
from protocols import (
    CellState,
    CheatType,
    Direction,
    GamePhase,
    GhostData,
    GhostState,
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
        self._cheats: List[CheatType] = []
        self._level: Level = Level()
        self._highscore_manager = HighscoreManager(config.highscore_filename)
        self._pacman: Pacman = Pacman(self._level)
        self._ghosts: List[Ghost] = [
            Ghost(ghost, self._level) for ghost in list(GhostType)
        ]

        self._score: int = 0
        self._lives: int = config.lives
        self._level_timer: float = self._level.data.time_limit

    def get_game_phase(self) -> GamePhase:
        return self._phase

    def set_game_phase(self, phase: GamePhase) -> None:
        self._phase = phase

    def get_current_level(self) -> int:
        return self._level.id if self._level else 0

    def get_remaining_time(self) -> float:
        return self._level_timer

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
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.NONE: Direction.NONE
        }

        if (
            opposites[self._pacman.direction] == direction
            or self._pacman.direction == Direction.NONE
        ):
            self._pacman.direction = direction
            return

        self._pacman.queued_direction = direction

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

    def toggle_cheat(self, cheat: CheatType) -> None:
        if cheat == CheatType.LEVEL_SKIP:
            self._level.go_next()
            return

        if cheat in self._cheats:
            self._cheats.remove(cheat)
        self._cheats.append(cheat)

    def update(self, delta_time: float) -> None:
        if self._phase != GamePhase.PLAYING:
            return

        self._level_timer -= delta_time

        if self._lives <= 0:
            self._phase = GamePhase.GAME_OVER
        if self._level.pacgums == 0:
            self._phase = GamePhase.WIN
        if self._level_timer <= 0:
            self._lose_round()

        self._pacman_actions(delta_time)
        self._ghost_actions(delta_time)

        for ghost in self._ghosts:
            if self._did_collide(ghost):
                if ghost.state.is_edible:
                    self._score += self._config.points_per_ghost
                    ghost.die()
                elif ghost.state.is_lethal:
                    if CheatType.INVINCIBILITY in self._cheats:
                        return
                    self._lose_round()
                    return

    def _lose_round(self) -> None:
        self._lives -= 1
        self._reset()

    def _pacman_actions(self, delta_time: float) -> None:
        rpos = (round(self._pacman.x), round(self._pacman.y))
        match self._level.grid[rpos[1]][rpos[0]]:
            case CellState.PACGUM:
                self._level.update_cell(*rpos, CellState.EMPTY)
                self._score += self._config.points_per_pacgum
            case CellState.SUPER_PACGUM:
                self._level.update_cell(*rpos, CellState.EMPTY)
                self._score += self._config.points_per_super_pacgum
                for ghost in self._ghosts:
                    ghost.set_state(
                        GhostState.FRIGHTENED,
                        self._level.data.difficulty.fear_duration
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
             if ghost.type == GhostType.RED),
            Ghost(GhostType.RED, self._level).data
        )

        for ghost in self._ghosts:
            ghost.update(delta_time, self.get_pacman(), red_ghost)

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
