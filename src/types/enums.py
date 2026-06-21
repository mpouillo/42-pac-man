from enum import Enum, auto


class CellState(Enum):
    """Represent the structural or item state of a single grid cell."""

    EMPTY = auto()
    WALL = auto()
    PACGUM = auto()
    SUPER_PACGUM = auto()


class CheatType(Enum):
    """Define the available cheat codes inside the game engine."""

    INVINCIBILITY = auto()
    LEVEL_SKIP = auto()
    GHOST_FREEZE = auto()
    SPEED_BOOST = auto()


class Direction(Enum):
    """Represent 2D vector coordinates for grid movement directions."""

    UP = (0, -1)
    LEFT = (-1, 0)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    NONE = (0, 0)

    @property
    def opposite(self) -> "Direction":
        """Return the inverted directional Enum member."""
        x, y = self.value
        return Direction((-x, -y))

    @classmethod
    def best_from_points(
        cls,
        p1: tuple[float, float],
        p2: tuple[float, float]
    ) -> list["Direction"]:
        """Sort cardinal directions by proximity to a target vector."""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        cardinals = [cls.UP, cls.DOWN, cls.LEFT, cls.RIGHT]

        return sorted(
            cardinals,
            key=lambda d: (dx * d.value[0]) + (dy * d.value[1]),
            reverse=True
        )


class GamePhase(Enum):
    """Represent the overarching state phases of the game loop."""

    MAIN_MENU = auto()
    HIGHSCORES_MENU = auto()
    INSTRUCTIONS_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    WIN = auto()


class GhostState(Enum):
    """Define ghost behavioral states and their associated properties."""

    CHASE = ("chase", True, False)
    SCATTER = ("scatter", True, False)
    FRIGHTENED = ("frightened", False, True)
    FLASHING = ("fashing", False, True)
    EATEN = ("eaten", False, False)

    def __init__(self, state_name: str, lethal: bool, edible: bool):
        """Assign underlying property attributes to the state member."""
        self.state_name = state_name
        self.is_lethal = lethal
        self.is_edible = edible


class GhostType(Enum):
    """Identify individual ghost entities by their canonical names."""

    PINK = "Pinky"
    RED = "Blinky"
    ORANGE = "Clyde"
    BLUE = "Inky"
