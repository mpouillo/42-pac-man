from pathlib import Path
from typing import Any, Dict, List, cast

from mazegenerator import MazeGenerator
from pydantic import BaseModel, field_validator
from src.types.enums import CellState, GhostType


class Position(BaseModel):
    """Represent an integer coordinate position on a 2D grid."""

    x: int
    y: int

    @property
    def values(self) -> tuple[int, int]:
        """Return the coordinate pair as a standard (x, y) tuple."""
        return self.x, self.y


class DifficultySettings(BaseModel):
    """Store configuration modifiers for game difficulty settings."""

    ghost_speed: float
    fear_duration: float


class LevelData(BaseModel):
    """Hold the serialized configuration data for a game level."""

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
        """Normalize ghost dictionary string keys into GhostType enums."""
        if isinstance(val, dict):
            return {
                GhostType[k.upper()] if (
                    isinstance(k, str) and k.upper() in GhostType.__members__
                ) else k: v
                for k, v in val.items()
            }
        return val

    def model_post_init(self, context: Any) -> None:
        """Scale coordinates to align with the expanded maze grid."""
        self.pacman_spawn.x = self.pacman_spawn.x * 2 + 1
        self.pacman_spawn.y = self.pacman_spawn.y * 2 + 1
        self.ghost_spawns = {
            k: Position(x=v.x * 2 + 1, y=v.y * 2 + 1)
            for k, v in self.ghost_spawns.items()
        }
        for pos in self.super_pacgums:
            pos.x = pos.x * 2 + 1
            pos.y = pos.y * 2 + 1


class Level:
    """Manage the active runtime map layout, state, and entities."""

    def __init__(self, level_file: Path) -> None:
        """Initialize the map runtime state from a level file source."""
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
        """Return a scannable string summary of the level metadata."""
        return (
            f"Level(file={self._level_file.name}, width={self.width}, "
            f"height={self.height}, pacgums={self.pacgums})"
        )

    def update_cell(self, x: int, y: int, state: CellState) -> bool:
        """Update a cell's state and handle active pacgum decrementing."""
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

    def _load_level_data(self) -> LevelData:
        """Read and parse the raw JSON file into a LevelData model."""
        try:
            data = self._level_file.read_text()
        except OSError as e:
            raise OSError(
                f"Error reading level data from {self._level_file}: {e}"
            )
        return LevelData.model_validate_json(data)

    def _load_grid(self) -> List[List[CellState]]:
        """Construct and populate a clean map grid using the generator."""
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
        """Transform a raw bitmask maze layout into a CellState grid."""
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

    def _setup_entities(
        self,
        grid: List[List[CellState]],
        data: LevelData
    ) -> List[List[CellState]]:
        """Place super pacgums and entity spawns onto the active grid."""
        # Place Super Pacgums
        for pos in data.super_pacgums:
            if 0 <= pos.y < len(grid) and 0 <= pos.x < len(grid[0]):
                grid[pos.y][pos.x] = CellState.SUPER_PACGUM

        # Clear out Pacman's spawn point
        if (
            0 <= data.pacman_spawn.y < len(grid)
            and 0 <= data.pacman_spawn.x < len(grid[0])
        ):
            grid[data.pacman_spawn.y][data.pacman_spawn.x] = CellState.EMPTY

        # Clear out Ghost spawns
        for ghost_pos in data.ghost_spawns.values():
            if (
                0 <= ghost_pos.y < len(grid)
                and 0 <= ghost_pos.x < len(grid[0])
            ):
                grid[ghost_pos.y][ghost_pos.x] = CellState.EMPTY

        return grid
