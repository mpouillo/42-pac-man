import heapq
import math
from typing import Any, Dict, List

from typing import Any

from src.constants import GHOST_FLASH_THRESHOLD, SPEED_FACTOR
from src.model.level import Level
from src.types.dataclasses import GhostData, PacmanData
from src.types.enums import CellState, Direction, GhostState, GhostType

Coordinates = tuple[int, int]   # (x, y)


class Ghost:
    def __init__(self, ghost_type: GhostType, level: Level) -> None:
        self.type: GhostType = ghost_type
        self._level: Level = level

        # Positions
        self.spawn: Coordinates = level.data.ghost_spawns[self.type].values
        self.x: float = float(self.spawn[0])
        self.y: float = float(self.spawn[1])

        self.direction: Direction = Direction.NONE
        self.state: GhostState = GhostState.SCATTER

        # Movement and pathing
        self._base_speed: float = (
            level.data.difficulty.ghost_speed * SPEED_FACTOR
        )
        self._speed: float = self._base_speed
        self._timer: float = 5.0
        self._target: Coordinates = (0, 0)
        self._path: list[Coordinates] = []
        self._scatter_target: Coordinates = self._init_scatter_target()

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
        print(self.type, "is chasing")
        self.state = GhostState.CHASE
        self._speed = self._base_speed * 1.5
        self._timer = 20.0
        self._path = []

    def scatter(self) -> None:
        print(self.type, "is scattering")
        self.state = GhostState.SCATTER
        self._speed = self._base_speed * 1.5
        self._timer = 5.0
        self._path = []

    def frighten(self, duration: float, pacman: PacmanData) -> None:
        print(self.type, "is frightened")
        self.state = GhostState.FRIGHTENED
        self._speed = self._base_speed
        self._timer = duration
        self._path = []

        # Turn around immediately if going in Pacman's direction
        dx = (pacman.x - self.x) * self.direction.value[0]
        dy = (pacman.y - self.y) * self.direction.value[1]
        if (dx + dy) > 0:
            self.direction = self.direction.opposite

    def die(self) -> None:
        print(self.type, "is eaten")
        self.state = GhostState.EATEN
        self._speed = self._base_speed * 2
        self._timer = 0.0
        self._path = []

        # Turn around immediately if going opposite to spawn
        if self._pick_direction(self.spawn, True) == self.direction.opposite:
            self.direction = self.direction.opposite

    def update(
        self,
        delta_time: float,
        pacman: PacmanData,
        red_ghost: GhostData
    ) -> None:
        self._snap_to_cells(delta_time)
        self._update_state_timers(delta_time)

        # At center of cell
        if self.x == math.floor(self.x) and self.y == math.floor(self.y):
            if self.state == GhostState.EATEN:
                if (math.floor(self.x), math.floor(self.y)) == self.spawn:
                    self.scatter()

            if self.state in [GhostState.FRIGHTENED, GhostState.FLASHING]:
                # Flee away from Pac-man
                dx, dy = self.x - pacman.x, self.y - pacman.y
                opposite_pacman = round(self.x + dx), round(self.y + dy)
                self.direction = self._pick_direction(opposite_pacman)
            else:
                self._compute_target(pacman, red_ghost)
                uturn = not self.state.is_lethal
                self.direction = self._pick_direction(self._target, uturn)

        self.x += self.direction.value[0] * self._speed * delta_time
        self.y += self.direction.value[1] * self._speed * delta_time

    def _init_scatter_target(self) -> Coordinates:
        if self.type == GhostType.RED:
            return (self._level.width - 2, 1)
        elif self.type == GhostType.PINK:
            return (1, 1)
        elif self.type == GhostType.BLUE:
            return (1, self._level.height - 2)
        elif self.type == GhostType.ORANGE:
            return (self._level.width - 2, self._level.height - 2)
        return (1, 1)

    def _snap_to_cells(self, delta_time: float) -> None:
        """Snap to center of cells if boundary is crossed this frame."""
        step_x = self.direction.value[0] * self._speed * delta_time
        step_y = self.direction.value[1] * self._speed * delta_time

        if step_x != 0 and math.floor(self.x) != math.floor(self.x + step_x):
            self.x = float(
                math.floor(self.x + step_x) if step_x > 0
                else math.ceil(self.x + step_x)
            )
        if step_y != 0 and math.floor(self.y) != math.floor(self.y + step_y):
            self.y = float(
                math.floor(self.y + step_y) if step_y > 0
                else math.ceil(self.y + step_y)
            )

    def _update_state_timers(self, delta_time: float) -> None:
        if self._timer > 0:
            self._timer -= delta_time

        if self.state == GhostState.CHASE and self._timer <= 0:
            self.scatter()

        elif self.state == GhostState.SCATTER and self._timer <= 0:
            self.chase()

        elif self.state == GhostState.FRIGHTENED:
            if self._timer <= GHOST_FLASH_THRESHOLD:
                self.state = GhostState.FLASHING

        elif self.state in [GhostState.FRIGHTENED, GhostState.FLASHING]:
            if self._timer <= 0:
                self.scatter()

    def _compute_target(
        self,
        pacman: PacmanData,
        red_ghost: GhostData
    ) -> None:
        if self.state == GhostState.SCATTER:
            self._pathfind_to(self._scatter_target)
            return

        if self.state == GhostState.EATEN:
            self._pathfind_to(self.spawn)
            return

        # GhostState.CHASE
        pac_x, pac_y = round(pacman.x), round(pacman.y)

        # Chase Pacman's position
        if self.type == GhostType.RED:
            self._target = (pac_x, pac_y)

        # Chase 2 cells ahead of Pacman's position
        elif self.type == GhostType.PINK:
            future_x = pac_x + pacman.direction.value[0] * 2
            future_y = pac_y + pacman.direction.value[1] * 2
            self._target = (
                max(0, min(future_x, self._level.width - 1)),
                max(0, min(future_y, self._level.height - 1))
            )

        # Chase Pacman's position, but flee to spawn if within 8 cells
        elif self.type == GhostType.ORANGE:
            distance = math.sqrt((self.x - pacman.x) ** 2 +
                                 (self.y - pacman.y) ** 2)
            if distance > 8:
                self._target = (pac_x, pac_y)
            else:
                self._target = self._scatter_target

        # Corner Pacman relative to Red's position
        elif self.type == GhostType.BLUE:
            front_x = pac_x + (pacman.direction.value[0] * 2)
            front_y = pac_y + (pacman.direction.value[1] * 2)
            vec_x = front_x - round(red_ghost.x)
            vec_y = front_y - round(red_ghost.y)
            self._target = (
                max(0, min(front_x + vec_x, self._level.width - 1)),
                max(0, min(front_y + vec_y, self._level.height - 1))
            )

    def _pathfind_to(self, destination: Coordinates) -> None:
        if not self._path or (self.x, self.y) != self._target:
            self._path = self._astar((round(self.x), round(self.y)),
                                     destination)

        if self._path:
            self._target = self._path.pop(0)
        else:
            self._target = destination

    def _pick_direction(
        self,
        target: Coordinates,
        reverse_allowed: bool = False
    ) -> Direction:
        cx, cy = int(self.x), int(self.y)
        choices = Direction.best_from_points((cx, cy), target)

        if not reverse_allowed and self.direction.opposite in choices:
            # Append opposite direction at the end as a last resort
            opposite = self.direction.opposite
            choices.remove(opposite)
            choices.append(opposite)

        for choice in choices:
            dx = max(0, min(cx + choice.value[0], self._level.width - 1))
            dy = max(0, min(cy + choice.value[1], self._level.height - 1))
            if self._level.grid[dy][dx] != CellState.WALL:
                return choice

        return Direction.NONE

    def _astar(
        self,
        start: Coordinates,
        goal: Coordinates
    ) -> list[Coordinates]:

        if start == goal:
            return [goal]

        def heuristic(a: Coordinates, b: Coordinates) -> int:
            return abs(b[0] - a[0]) + abs(b[1] - a[1])

        open_list: list[Any] = []
        heapq.heappush(open_list, (0 + heuristic(start, goal), start))

        came_from: dict[Any, Any] = {}
        g_score = {start: 0}

        while open_list:
            _, current = heapq.heappop(open_list)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            x, y = current

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (x + dx, y + dy)
                nx, ny = neighbor

                if not (
                    0 <= nx < self._level.width
                    and 0 <= ny < self._level.height
                ):
                    continue

                if self._level.grid[ny][nx] == CellState.WALL:
                    continue

                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score, neighbor))

        return []  # Path not found
