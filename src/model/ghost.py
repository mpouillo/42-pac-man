import math
import numpy

from constants import GHOST_FLASH_THRESHOLD
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
    def __init__(self, ghost_type: GhostType, level: Level) -> None:
        self.type: GhostType = ghost_type
        self._level: Level = level
        self.spawn: tuple[int, int] = level.data.ghost_spawns[self.type].values
        self.x: float = self.spawn[0]
        self.y: float = self.spawn[1]
        self.direction: Direction = Direction.NONE
        self.state: GhostState = GhostState.CHASE

        self._speed: float = level.data.difficulty.ghost_speed
        self._behavior_timer: float = 0.0
        self._target_tile: tuple[int, int] = (0, 0)     # (x, y)
        self._checkpoint: tuple[float, float] = (0, 0)  # (x, y)

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

    def set_state(self, state: GhostState, duration: float = 0) -> None:
        if duration:
            self._behavior_timer = duration
        self.state = state

    def die(self) -> None:
        print(f"dead! going to {self._target_tile}")
        self.state = GhostState.EATEN
        self.direction = self._choose_best_direction(reverse_allowed=True)

    def update(
        self,
        delta_time: float,
        pacman: PacmanData,
        red_ghost: GhostData
    ) -> None:
        self._update_state(delta_time)
        self._calculate_target_tile(pacman, red_ghost)
        self._move_towards_target(delta_time)

    def _update_state(self, delta_time: float) -> None:
        if self._behavior_timer > 0:
            self._behavior_timer -= delta_time

        if self.state == GhostState.FRIGHTENED:
            if self._behavior_timer <= GHOST_FLASH_THRESHOLD:
                self.set_state(GhostState.FLASHING)

        if self.state == GhostState.FLASHING:
            if self._behavior_timer <= 0:
                self.set_state(GhostState.CHASE)

        elif self.state == GhostState.EATEN:
            if (self.x, self.y) == self.spawn:
                self.set_state(GhostState.CHASE)

    def _calculate_target_tile(
        self,
        pacman: PacmanData,
        red_ghost: GhostData
    ) -> None:
        if self.state == GhostState.SCATTER:
            self._target_tile = self.spawn
        elif self.state == GhostState.FRIGHTENED:
            self._target_tile = (
                int(numpy.random.randint(0, self._level.data.size_x)),
                int(numpy.random.randint(0, self._level.data.size_y))
            )
        elif self.state == GhostState.EATEN:
            self._target_tile = self.spawn
        else:
            if self.type == GhostType.PINK:
                # Chase 2 cells ahead of Pacman's position
                pacman_pos = numpy.array((int(pacman.x), int(pacman.y)))
                future_pos = numpy.array(pacman.direction.value) * 2
                self._target_tile = tuple(numpy.add(pacman_pos, future_pos))
            elif self.type == GhostType.RED:
                # Chase Pacman's position
                self._target_tile = (int(pacman.x), int(pacman.y))
            elif self.type == GhostType.ORANGE:
                # Chase Pacman's position, but flee to spawn if within 8 cells
                distance = abs(math.sqrt(
                    (self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2
                ))
                if distance <= 8 and self._level.data:
                    spawn = self._level.data.ghost_spawns[self.type]
                    self._target_tile = (spawn.x, spawn.y)
                else:
                    self._target_tile = (int(pacman.x), int(pacman.y))
            elif self.type == GhostType.BLUE:
                # Corners Pacman relative to Blinky's position
                pacman_pos = numpy.array((int(pacman.x), int(pacman.y)))
                future_pos = numpy.array(pacman.direction.value) * 2
                pink_target = tuple(numpy.add(pacman_pos, future_pos))
                red_pos = numpy.array([red_ghost.x, red_ghost.y])
                difference = numpy.subtract(pink_target, red_pos)
                self._target_tile = tuple(numpy.add(pink_target, difference))
            else:
                self._target_tile = (0, 0)

    def _move_towards_target(self, delta_time: float) -> None:
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
            self.direction = self._choose_best_direction()
        else:
            self.x += self.direction.value[0] * move_distance
            self.y += self.direction.value[1] * move_distance

    def _choose_best_direction(
        self,
        reverse_allowed: bool = False
    ) -> Direction:
        directions = [
            Direction.UP,
            Direction.LEFT,
            Direction.DOWN,
            Direction.RIGHT
        ]

        best_direction = self.direction
        min_distance = float('inf')

        current_x = self._checkpoint[0]
        current_y = self._checkpoint[1]
        best_checkpoint = (current_x, current_y)

        for i, d in enumerate(directions):
            if (
                not reverse_allowed
                and d == self.direction.opposite
                and self.direction != Direction.NONE
            ):
                continue

            next_x = int(current_x) + d.value[0]
            next_y = int(current_y) + d.value[1]

            if (
                0 <= next_y < len(self._level.grid)
                and 0 <= next_x < len(self._level.grid[0])
                and self._level.grid[next_y][next_x] != CellState.WALL
            ):
                dist_sq = math.sqrt(
                    (next_x - self._target_tile[0]) ** 2
                    + (next_y - self._target_tile[1]) ** 2
                )

                if dist_sq < min_distance:
                    min_distance = dist_sq
                    best_direction = d
                    best_checkpoint = (float(next_x), float(next_y))

            # Prevent getting stuck in dead ends
            if (
                i == len(directions) - 1
                and best_checkpoint == (current_x, current_y)
            ):
                best_direction = self.direction.opposite

        self._checkpoint = best_checkpoint
        return best_direction
