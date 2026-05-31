import math
import numpy
from typing import Dict, Tuple

from protocols import (
    CellState,
    Direction,
    GhostData,
    GhostState,
    GhostType,
    PacmanData
)
from src.model.level import Level


class Ghost:
    def __init__(self, ghost_type: GhostType, speed: float) -> None:
        self.type: GhostType = ghost_type
        self.x: float = 0.0
        self.y: float = 0.0
        self.direction: Direction = Direction.NONE
        self.state: GhostState = GhostState.IDLE

        self._speed: float = speed
        self._behavior_timer: float = 0.0
        self._target_tile: Tuple[int, int] = (0, 0)     # (x, y)
        self._checkpoint: Tuple[float, float] = (0, 0)  # (x, y)

    @property
    def data(self) -> GhostData:
        """Return a read-only view of the ghost."""
        return GhostData(
            x=self.x,
            y=self.y,
            direction=self.direction,
            type=self.type,
            state=self.state,
        )

    def chase(self) -> None:
        self.state = GhostState.CHASE

    def scatter(self, duration: float) -> None:
        self.state = GhostState.SCATTER
        self._behavior_timer = duration

    def update(
        self,
        delta_time: float,
        level: Level,
        pacman: PacmanData,
        ghost_info: Dict[GhostType, Dict[str, tuple[float, float]]]
    ) -> None:
        self._update_state(delta_time)
        self._calculate_target_tile(pacman, level, ghost_info)
        self._move_towards_target(level, delta_time)

    def _update_state(self, delta_time: float) -> None:
        if self._behavior_timer > 0:
            self._behavior_timer -= delta_time

        if (
            self.state == GhostState.SCATTER
            and self._behavior_timer <= 0
        ):
            self._behavior_timer = 0
            self.state = GhostState.CHASE

    def _calculate_target_tile(
        self,
        pacman: PacmanData,
        level: Level,
        ghost_info: Dict[GhostType, Dict[str, tuple[float, float]]]
    ) -> None:
        if self.state == GhostState.SCATTER and level.data:
            self._target_tile = (
                int(numpy.random.randint(0, level.data.size_x)),
                int(numpy.random.randint(0, level.data.size_y))
            )
            return

        match self.type:
            case GhostType.PINK:
                # Chase 2 cells ahead of Pacman's position
                pacman_pos = numpy.array((int(pacman.x), int(pacman.y)))
                future_pos = numpy.array(pacman.direction.value) * 2
                self._target_tile = tuple(numpy.add(pacman_pos, future_pos))
            case GhostType.RED:
                # Chase Pacman's position
                self._target_tile = (int(pacman.x), int(pacman.y))
            case GhostType.ORANGE:
                # Chase Pacman's position, but flee to spawn if within 8 cells
                distance = abs(math.sqrt(
                    (self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2
                ))
                if distance <= 8:
                    spawn = level.get_ghost_spawn(self.type)
                    self._target_tile = (spawn.x, spawn.y)
                else:
                    self._target_tile = (int(pacman.x), int(pacman.y))
            case GhostType.BLUE:
                # Corners Pacman relative to Blinky's position
                red_pos = numpy.array(ghost_info[GhostType.RED]["position"])
                pink_target = numpy.array(ghost_info[GhostType.PINK]["target"])
                difference = numpy.subtract(pink_target, red_pos)
                self._target_tile = tuple(numpy.add(pink_target, difference))
            case _:
                self._target_tile = (0, 0)

    def _move_towards_target(self, level: Level, delta_time: float) -> None:
        if self._checkpoint == (0.0, 0.0):
            self._checkpoint = (float(int(self.x)), float(int(self.y)))

        dx = self._checkpoint[0] - self.x
        dy = self._checkpoint[1] - self.y
        cp_distance = math.hypot(dx, dy)

        move_distance = self._speed * delta_time

        if (
            move_distance >= cp_distance
            or self.direction == Direction.NONE
        ):
            self.x = float(self._checkpoint[0])
            self.y = float(self._checkpoint[1])
            self._choose_next_checkpoint(level)
        else:
            self.x += self.direction.value[0] * move_distance
            self.y += self.direction.value[1] * move_distance

    def _choose_next_checkpoint(self, level: Level) -> None:
        directions = [
            Direction.UP,
            Direction.LEFT,
            Direction.DOWN,
            Direction.RIGHT
        ]

        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.NONE: Direction.NONE
        }

        best_direction = self.direction
        min_distance = float('inf')

        current_x = self._checkpoint[0]
        current_y = self._checkpoint[1]
        best_checkpoint = (current_x, current_y)

        for d in directions:
            if (
                d == opposites[self.direction]
                and self.direction != Direction.NONE
            ):
                continue

            next_x = int(current_x) + d.value[0]
            next_y = int(current_y) + d.value[1]

            if (
                0 <= next_y < len(level.grid)
                and 0 <= next_x < len(level.grid[0])
                and level.grid[next_y][next_x] != CellState.WALL
            ):
                dist_sq = math.sqrt(
                    (next_x - self._target_tile[0]) ** 2
                    + (next_y - self._target_tile[1]) ** 2
                )

                if dist_sq < min_distance:
                    min_distance = dist_sq
                    best_direction = d
                    best_checkpoint = (float(next_x), float(next_y))

        self.direction = best_direction
        self._checkpoint = best_checkpoint
