from typing import Any, Dict, List, Optional

from constants import LEVELS_DIR
from mazegenerator import MazeGenerator
from pydantic import BaseModel, field_validator
from protocols import CellState, GhostType


class Position(BaseModel):
    x: int
    y: int


class DifficultySettings(BaseModel):
    ghost_speed: float
    frightened_duration: float


class LevelData(BaseModel):
    size_x: int
    size_y: int
    time_limit: int
    seed: int
    pacman_spawn: Position
    ghost_spawns: Dict[GhostType, Position]
    super_pacgums: List[Position]
    difficulty_settings: DifficultySettings

    @field_validator("ghost_spawns", mode="before")
    @classmethod
    def convert_ghost_string_keys(cls, val: Any) -> Any:
        if isinstance(val, dict):
            return {
                GhostType[k.upper()] if (
                    isinstance(k, str) and k.upper() in GhostType.__members__
                    ) else k: v
                for k, v in val.items()
            }
        return val


class Level:
    def __init__(self, level_id: int = 1) -> None:
        self.id: int = level_id
        self.grid: list[list[CellState]] = []
        self.time_limit: int = 0
        self.difficulty: Optional[DifficultySettings] = None

        self._remaining_pacgums: int = 0

        self._load_level_data()

    def __str__(self) -> str:
        return str(self.__dict__)

    @property
    def pacgums(self) -> int:
        """Read-only access to count of remaining pacgums in level."""
        return self._remaining_pacgums

    def update_cell(self, x: int, y: int, state: CellState) -> bool:
        """
        Update the state of a cell of the level.
        Return False if update failed (out of range), else True.
        """
        if y < 0 or y >= len(self.grid) or x < 0 or x >= len(self.grid[0]):
            return False

        # Update remaining pacgums
        if (
            self.grid[y][x] in (CellState.PACGUM, CellState.SUPER_PACGUM)
            and state == CellState.EMPTY
        ):
            self._remaining_pacgums -= 1

        self.grid[y][x] = state
        return True

    def _load_level_data(self) -> None:
        file_path = LEVELS_DIR / f"level_{self.id}.json"
        data = LevelData.model_validate_json(file_path.read_text())

        self._time_limit = data.time_limit
        self.difficulty = data.difficulty_settings

        maze = MazeGenerator(
            size=(data.size_x, data.size_y),
            seed=data.seed
        ).maze

        self.grid = self._convert_maze_togrid(maze)
        self._setup_spawns(data)

        self._remaining_pacgums = sum(
            1 for row in self.grid for cell in row
            if cell in (CellState.PACGUM, CellState.SUPER_PACGUM)
        )

    def _convert_maze_togrid(
        self,
        maze: List[List[int]]
    ) -> List[List[CellState]]:
        maze_height = len(maze)
        maze_width = len(maze[0]) if maze_height > 0 else 0

        grid_height = maze_height * 2 + 1
        grid_width = maze_width * 2 + 1

        grid: List[List[CellState]] = [
            [CellState.WALL for _ in range(grid_width)]
            for _ in range(grid_height)
        ]

        TOP: int = 1
        RIGHT: int = 2
        BOTTOM: int = 4
        LEFT: int = 8

        for cy, row in enumerate(maze):
            for cx, cell in enumerate(row):
                x = cx * 2 + 1
                y = cy * 2 + 1

                grid[y][x] = CellState.PACGUM

                if not (cell & TOP):
                    grid[y - 1][x] = CellState.PACGUM
                if not (cell & RIGHT):
                    grid[y][x + 1] = CellState.PACGUM
                if not (cell & BOTTOM):
                    grid[y + 1][x] = CellState.PACGUM
                if not (cell & LEFT):
                    grid[y][x - 1] = CellState.PACGUM

        return grid

    def _setup_spawns(self, data: LevelData) -> None:
        for pos in data.super_pacgums:
            gx = pos.x * 2 + 1
            gy = pos.y * 2 + 1
            if 0 <= gy < len(self.grid) and 0 <= gx < len(self.grid[0]):
                self.grid[gy][gx] = CellState.SUPER_PACGUM

        spawns = [data.pacman_spawn] + list(data.ghost_spawns.values())
        for pos in spawns:
            gx = pos.x * 2 + 1
            gy = pos.y * 2 + 1
            if self.grid[gy][gx] in (
                CellState.PACGUM, CellState.SUPER_PACGUM
            ):
                self.grid[gy][gx] = CellState.EMPTY
