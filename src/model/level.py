from pathlib import Path
from typing import Any, Dict, List, cast

from mazegenerator import MazeGenerator
from pydantic import BaseModel, field_validator
from src.types.enums import CellState, GhostType


class Position(BaseModel):
    x: int
    y: int

    @property
    def values(self) -> tuple[int, int]:
        return self.x, self.y


class DifficultySettings(BaseModel):
    ghost_speed: float
    fear_duration: float


class LevelData(BaseModel):
    size_x: int
    size_y: int
    time_limit: int
    seed: int | None = None
    pacman_spawn: Position
    ghost_spawns: Dict[GhostType, Position]
    super_pacgums: List[Position]
    difficulty: DifficultySettings

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

    def model_post_init(self, context: Any) -> None:
        self.pacman_spawn.x = self.pacman_spawn.x * 2 + 1
        self.pacman_spawn.y = self.pacman_spawn.y * 2 + 1
        self.ghost_spawns = {
            k: Position(x=v.x * 2 + 1, y=v.y * 2 + 1)
            for k, v in self.ghost_spawns.items()
        }


class Level:
    def __init__(self, level_file: Path) -> None:
        self._level_file = level_file
        self.data: LevelData = self._load_level_data()
        self.grid: List[List[CellState]] = self._load_grid()
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height else 0
        self.pacgums = sum(
            1 for row in self.grid for cell in row
            if cell in (CellState.PACGUM, CellState.SUPER_PACGUM)
        )

    def __str__(self) -> str:
        return str(self.__dict__)

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
            self.pacgums -= 1

        self.grid[y][x] = state
        return True

    def reset(self) -> None:
        self._load_level_data()

    def _load_level_data(self) -> LevelData:
        try:
            data = self._level_file.read_text()
        except OSError as e:
            raise OSError(
                f"Error reading level data from {self._level_file}: {e}"
            )
        return LevelData.model_validate_json(data)

    def _load_grid(self) -> List[List[CellState]]:
        gen = MazeGenerator(
            size=(self.data.size_x, self.data.size_y),
            seed=cast(int, self.data.seed)
        )
        grid = self._convert_maze_to_grid(gen.maze)
        grid = self._setup_entities(grid, self.data)
        return grid

    def _convert_maze_to_grid(
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

                if not (cell == 0xF):
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

    def _setup_entities(
        self,
        grid: List[List[CellState]],
        data: LevelData
    ) -> List[List[CellState]]:
        for pos in data.super_pacgums:
            gx = pos.x * 2 + 1
            gy = pos.y * 2 + 1
            if 0 <= gy < len(grid) and 0 <= gx < len(grid[0]):
                grid[gy][gx] = CellState.SUPER_PACGUM

        grid[data.pacman_spawn.y][data.pacman_spawn.x] = CellState.EMPTY

        return grid
