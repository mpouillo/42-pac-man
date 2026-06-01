import math

from constants import PACMAN_SPEED
from protocols import CellState, Direction, PacmanData, PacmanState
from src.model.level import Level


class Pacman:
    def __init__(self, level: Level) -> None:
        self.x: float = level.data.pacman_spawn.x
        self.y: float = level.data.pacman_spawn.y
        self.direction: Direction = Direction.LEFT
        self.queued_direction: Direction = Direction.NONE
        self.state: PacmanState = PacmanState.ALIVE

        self._speed: float = PACMAN_SPEED
        self._timer: float = 0.0
        self._level: Level = level

    @property
    def data(self) -> PacmanData:
        return PacmanData(
            x=self.x,
            y=self.y,
            direction=self.direction,
            state=self.state
        )

    def run(self) -> None:
        print("run!")
        self.state = PacmanState.ALIVE

    def power_up(self, duration: float) -> None:
        print("powered up!")
        self.state = PacmanState.POWERED
        self._timer = duration

    def die(self) -> None:
        self.state = PacmanState.DEAD

    def update(self, delta_time: float) -> None:
        self._calculate_movement(delta_time)
        self._update_state(delta_time)

    def _calculate_movement(self, delta_time: float) -> None:
        if self.direction == Direction.NONE or self.state == PacmanState.DEAD:
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
                if self._level.grid[cy + diry][cx + dirx] != CellState.WALL:
                    self.direction = self.queued_direction
                    self.queued_direction = Direction.NONE

            nx = cx + self.direction.value[0]
            ny = cy + self.direction.value[1]

            # Stop moving if facing a wall
            if self._level.grid[ny][nx] == CellState.WALL:
                self.direction = Direction.NONE
                self.queued_direction = Direction.NONE

        # Next position
        nx = self.x + (self.direction.value[0] * self._speed * delta_time)
        ny = self.y + (self.direction.value[1] * self._speed * delta_time)

        self.x = nx
        self.y = ny

    def _update_state(self, delta_time: float) -> None:
        if self._timer > 0:
            self._timer -= delta_time

        match self.state:
            case PacmanState.POWERED:
                if self._timer <= 0:
                    self._timer = 0
                    self.run()
