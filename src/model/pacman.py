from constants import PACMAN_SPEED
from protocols import Direction, PacmanData, PacmanState


class Pacman:
    def __init__(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.direction: Direction = Direction.UP
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
