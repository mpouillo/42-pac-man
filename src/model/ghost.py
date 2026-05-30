from constants import GHOST_SPEED
from protocols import (
    Direction,
    GhostBehavior,
    GhostData,
    GhostState,
    GhostType
)


class Ghost:
    def __init__(self, ghost_type: GhostType) -> None:
        self.type: GhostType = ghost_type
        self.x: float = 0.0
        self.y: float = 0.0
        self.direction: Direction = Direction.UP
        self.state: GhostState = GhostState.CHASING
        self.behavior: GhostBehavior = GhostBehavior.CHASE

        self._speed: float = GHOST_SPEED

    @property
    def data(self) -> GhostData:
        """Return a clean, read-only view of the ghost."""
        return GhostData(
            x=self.x,
            y=self.y,
            direction=self.direction,
            type=self.type,
            state=self.state,
            behavior=self.behavior
        )

    def update(self) -> None:
        pass
