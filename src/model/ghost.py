import math
import numpy

from constants import GHOST_FLASH_THRESHOLD, SPEED_FACTOR
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

        self._speed: float = level.data.difficulty.ghost_speed * SPEED_FACTOR
        self._behavior_timer: float = 0.0
        self._target_tile: tuple[int, int] = (0, 0)     # (x, y)

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

        # Go backwards when turning frightened
        if (
            self.state == GhostState.CHASE
            and state == GhostState.FRIGHTENED
        ):
            self.direction = self.direction.opposite

        self.state = state

    def die(self) -> None:
        print(f"dead! going to {self._target_tile}")
        self.state = GhostState.EATEN

    def update(
        self,
        delta_time: float,
        pacman: PacmanData,
        red_ghost: GhostData
    ) -> None:
        self._update_state(delta_time)
        self._snap_to_cells(delta_time)
        self._compute_target(pacman, red_ghost)
        self.direction = self._compute_direction(reverse_allowed=False)
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

    def _compute_target(
        self,
        pacman: PacmanData,
        red_ghost: GhostData
    ) -> None:
        if self.state == GhostState.SCATTER:
            # Go to spawn
            self._target_tile = self.spawn
        elif self.state == GhostState.FRIGHTENED:
            # Go opposite of Pacman's position
            dx = int(self.x) - int(pacman.x)
            dy = int(self.y) - int(pacman.y)
            self._target_tile = (int(self.x) + dx, int(self.y) + dy)
        elif self.state == GhostState.EATEN:
            # Go to spawn
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

    def _compute_direction(
        self,
        reverse_allowed: bool = False
    ) -> Direction:
        # At center of cell
        if self.x == math.floor(self.x) and self.y == math.floor(self.y):
            cx, cy = int(self.x), int(self.y)
            choices = Direction.best_from_points((cx, cy), self._target_tile)

            if not reverse_allowed and self.direction.opposite in choices:
                # Append opposite direction at the end as a last resort
                opposite = self.direction.opposite
                choices.remove(opposite)
                choices.append(opposite)
            for choice in choices:
                dx = cx + choice.value[0]
                dy = cy + choice.value[1]
                if self._level.grid[dy][dx] != CellState.WALL:
                    return choice
            return Direction.NONE

        return self.direction
