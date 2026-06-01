import math

from constants import PACMAN_SPEED
from protocols import CellState, Direction, PacmanData, PacmanState
from src.model.level import Level, LevelData


class Pacman:
    def __init__(self, level_data: LevelData) -> None:
        self.x: float = level_data.pacman_spawn.x
        self.y: float = level_data.pacman_spawn.y
        self.direction: Direction = Direction.NONE
        self.queued_direction: Direction = Direction.NONE
        self.state: PacmanState = PacmanState.ALIVE

        self._speed: float = PACMAN_SPEED

    @property
    def data(self) -> PacmanData:
        return PacmanData(
            x=self.x,
            y=self.y,
            direction=self.direction,
            state=self.state
        )

    def update(self, delta_time: float, level: Level) -> None:
        if self.direction == Direction.NONE:
            return

        # Snap to center of cells
        if (
            math.dist([self.x, self.y], [round(self.x), round(self.y)])
            < delta_time * self._speed / 2
        ):
            self.x, self.y = round(self.x), round(self.y)

        # At center of cell
        if self.x == int(self.x) and self.y == int(self.y):
            cx = int(self.x)
            cy = int(self.y)

            # Check if new direction moves towards a wall
            if self.queued_direction != Direction.NONE:
                dirx = self.queued_direction.value[0]
                diry = self.queued_direction.value[1]
                if level.grid[cy + diry][cx + dirx] != CellState.WALL:
                    self.direction = self.queued_direction
                    self.queued_direction = Direction.NONE

            nx = cx + self.direction.value[0]
            ny = cy + self.direction.value[1]

            # Stop moving if facing a wall
            if level.grid[ny][nx] == CellState.WALL:
                self.direction = Direction.NONE
                self.queued_direction = Direction.NONE

        # Next position
        nx = self.x + (self.direction.value[0] * self._speed * delta_time)
        ny = self.y + (self.direction.value[1] * self._speed * delta_time)

        self.x = nx
        self.y = ny
