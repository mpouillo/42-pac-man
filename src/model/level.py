from typing import List

from constants import LEVELS_DIR
from mazegenerator import MazeGenerator
from pydantic import BaseModel
from protocols import CellState


class LevelData(BaseModel):
    size_x: int
    size_y: int
    time_limit: int
    seed: int


class Level:
    def __init__(self, level_id: int = 1) -> None:
        self.id: int = level_id
        self.grid: list[list[int]] = []
        self.time_limit: int = 0

        self._load_level_data()

    @property
    def data(self) -> List[List[CellState]]:
        TOP: int = 1
        RIGHT: int = 2
        BOTTOM: int = 4
        LEFT: int = 8

        orig_height = len(self.grid)
        orig_width = len(self.grid[0]) if orig_height > 0 else 0

        new_height = orig_height * 2 + 1
        new_width = orig_width * 2 + 1

        grid: List[List[CellState]] = [
            [CellState.WALL for _ in range(new_width)]
            for _ in range(new_height)
        ]

        for cy, row in enumerate(self.grid):
            for cx, cell in enumerate(row):
                x = cx * 2 + 1
                y = cy * 2 + 1

                grid[x][y] = CellState.EMPTY

                if not (cell & TOP):
                    grid[y - 1][x] = CellState.EMPTY
                if not (cell & RIGHT):
                    grid[y][x + 1] = CellState.EMPTY
                if not (cell & BOTTOM):
                    grid[y + 1][x] = CellState.EMPTY
                if not (cell & LEFT):
                    grid[y][x - 1] = CellState.EMPTY

        return grid

    def _load_level_data(self) -> None:
        file_path = LEVELS_DIR / f"level_{self.id}.json"
        data = LevelData.model_validate_json(file_path.read_text())

        self.grid = MazeGenerator(
            size=(data.size_x, data.size_y),
            seed=data.seed
        ).maze
        self.time_limit = data.time_limit
