from constants import PACMAN_SPEED
from protocols import Direction, PacmanData, PacmanState


class Pacman:
    def __init__(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.direction: Direction = Direction.NONE
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

    def update(self, delta_time: float) -> None:
        match self.direction:
            case Direction.UP:
                self.y -= delta_time * self._speed
            case Direction.DOWN:
                self.y += delta_time * self._speed
            case Direction.LEFT:
                self.x -= delta_time * self._speed
            case Direction.RIGHT:
                self.x += delta_time * self._speed
