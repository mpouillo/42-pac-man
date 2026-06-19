from enum import Enum, auto
from typing import List


class CellState(Enum):
    EMPTY = auto()
    WALL = auto()
    PACGUM = auto()
    SUPER_PACGUM = auto()


class CheatType(Enum):
    INVINCIBILITY = auto()
    LEVEL_SKIP = auto()
    GHOST_FREEZE = auto()
    SPEED_BOOST = auto()


class Direction(Enum):
    """(x, y)"""
    UP = (0, -1)
    LEFT = (-1, 0)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    NONE = (0, 0)

    @property
    def opposite(self) -> "Direction":
        x, y = self.value
        return Direction((-x, -y))

    @classmethod
    def best_from_points(
        cls,
        p1: tuple[float, float],
        p2: tuple[float, float]
    ) -> List["Direction"]:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        cardinals = [cls.UP, cls.DOWN, cls.LEFT, cls.RIGHT]

        return sorted(
            cardinals,
            key=lambda d: (dx * d.value[0]) + (dy * d.value[1]),
            reverse=True
        )


class GamePhase(Enum):
    MAIN_MENU = auto()
    HIGHSCORES_MENU = auto()
    INSTRUCTIONS_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    WIN = auto()


class GhostState(Enum):
    # (name: str, is_lethal: bool, is_edible: bool)
    CHASE = ("chase", True, False)
    SCATTER = ("scatter", True, False)
    FRIGHTENED = ("frightened", False, True)
    FLASHING = ("flashing", False, True)
    EATEN = ("eaten", False, False)

    def __init__(self, state_name: str, lethal: bool, edible: bool):
        self.state_name = state_name
        self.is_lethal = lethal
        self.is_edible = edible


class GhostType(Enum):
    PINK = "Pinky"
    RED = "Blinky"
    ORANGE = "Clyde"
    BLUE = "Inky"
