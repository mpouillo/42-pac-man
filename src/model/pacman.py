import math

from src.constants import PACMAN_SPEED, SPEED_FACTOR
from src.model.level import Level
from src.types.dataclasses import PacmanData
from src.types.enums import CellState, Direction


class Pacman:
    """Represent the Pacman player entity and handle its movement logic."""

    def __init__(self, level: Level) -> None:
        """Initialize Pacman with positional, directional, and speed states."""
        self.x: float = level.data.pacman_spawn.x
        self.y: float = level.data.pacman_spawn.y
        self.direction: Direction = Direction.NONE
        self.queued_direction: Direction = Direction.NONE
        self.alive: bool = True

        self._speed: float = PACMAN_SPEED * SPEED_FACTOR
        self._timer: float = 0.0
        self._level: Level = level

    @property
    def data(self) -> PacmanData:
        """Return a read-only data snapshot view of Pacman."""
        return PacmanData(
            x=self.x,
            y=self.y,
            direction=self.direction,
        )

    def update(self, delta_time: float) -> None:
        """Advance Pacman's position and update direction rules per frame."""
        self._snap_to_cells(delta_time)
        self._compute_direction()
        self.x += self.direction.value[0] * self._speed * delta_time
        self.y += self.direction.value[1] * self._speed * delta_time

    def _snap_to_cells(self, delta_time: float) -> None:
        """Snap Pacman to the nearest cell center when crossing a boundary."""
        step_x = self.direction.value[0] * self._speed * delta_time
        step_y = self.direction.value[1] * self._speed * delta_time
        if step_x != 0 and math.floor(self.x) != math.floor(self.x + step_x):
            self.x = float(round(self.x))
        if step_y != 0 and math.floor(self.y) != math.floor(self.y + step_y):
            self.y = float(round(self.y))

    def _compute_direction(self) -> None:
        """Evaluate grid surroundings to change or halt movement direction."""
        # Use tolerance checking to clean up floating point inaccuracy
        if (
            math.isclose(self.x, round(self.x), abs_tol=1e-9)
            and math.isclose(self.y, round(self.y), abs_tol=1e-9)
        ):
            self.x = float(round(self.x))
            self.y = float(round(self.y))
            cx, cy = int(self.x), int(self.y)

            # Apply buffered direction if valid
            if self.queued_direction != Direction.NONE:
                dirx = self.queued_direction.value[0]
                diry = self.queued_direction.value[1]
                nx = max(0, min(cx + dirx, self._level.width - 1))
                ny = max(0, min(cy + diry, self._level.height - 1))
                if self._level.grid[ny][nx] != CellState.WALL:
                    self.direction = self.queued_direction
                    self.queued_direction = Direction.NONE

            # Stop moving if facing a wall
            dx = max(
                0, min(cx + self.direction.value[0], self._level.width - 1)
            )
            dy = max(
                0, min(cy + self.direction.value[1], self._level.height - 1)
            )
            if self._level.grid[dy][dx] == CellState.WALL:
                self.direction = Direction.NONE
