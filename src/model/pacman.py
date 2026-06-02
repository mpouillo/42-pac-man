import math

from constants import PACMAN_SPEED, SPEED_FACTOR
from protocols import CellState, Direction, PacmanData
from src.model.level import Level


class Pacman:
    def __init__(self, level: Level) -> None:
        self.x: float = level.data.pacman_spawn.x
        self.y: float = level.data.pacman_spawn.y
        self.direction: Direction = Direction.LEFT
        self.queued_direction: Direction = Direction.NONE
        self.alive: bool = True

        self._speed: float = PACMAN_SPEED * SPEED_FACTOR
        self._timer: float = 0.0
        self._level: Level = level

    @property
    def data(self) -> PacmanData:
        return PacmanData(
            x=self.x,
            y=self.y,
            direction=self.direction,
        )

    def update(self, delta_time: float) -> None:
        self._snap_to_cells(delta_time)
        self._compute_direction()
        self.x += self.direction.value[0] * self._speed * delta_time
        self.y += self.direction.value[1] * self._speed * delta_time

    def _snap_to_cells(self, delta_time: float) -> None:
        """Snap to center of cells if boundary is crossed this frame."""
        step_x = self.direction.value[0] * self._speed * delta_time
        step_y = self.direction.value[1] * self._speed * delta_time
        if step_x != 0 and math.floor(self.x) != math.floor(self.x + step_x):
            self.x = round(self.x)
        if step_y != 0 and math.floor(self.y) != math.floor(self.y + step_y):
            self.y = round(self.y)

    def _compute_direction(self) -> None:
        # At center of cell
        if self.x == math.floor(self.x) and self.y == math.floor(self.y):
            cx, cy = int(self.x), int(self.y)

            # Apply buffered direction if valid
            if self.queued_direction != Direction.NONE:
                dirx = self.queued_direction.value[0]
                diry = self.queued_direction.value[1]
                if self._level.grid[cy + diry][cx + dirx] != CellState.WALL:
                    self.direction = self.queued_direction
                    self.queued_direction = Direction.NONE

            # Stop moving if facing a wall
            dx = cx + self.direction.value[0]
            dy = cy + self.direction.value[1]
            if self._level.grid[dy][dx] == CellState.WALL:
                self.direction = Direction.NONE
                self.queued_direction = Direction.NONE
