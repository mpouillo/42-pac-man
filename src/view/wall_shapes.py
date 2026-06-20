"""Wall shape detection and model rotation mappings."""

from enum import Enum

from src.types.enums import CellState


WALL_UP = 1
WALL_RIGHT = 2
WALL_DOWN = 4
WALL_LEFT = 8


class WallAssetKind(Enum):
    """Base wall asset type before rotation."""

    ISOLATED = "isolated"
    END = "end"
    STRAIGHT = "straight"
    CORNER = "corner"
    T_JUNCTION = "t_junction"
    CROSS = "cross"


WALL_RENDER_INFO = {
    0: (WallAssetKind.ISOLATED, 0.0),
    WALL_UP: (WallAssetKind.END, 0.0),
    WALL_RIGHT: (WallAssetKind.END, 270.0),
    WALL_DOWN: (WallAssetKind.END, 180.0),
    WALL_LEFT: (WallAssetKind.END, 90.0),
    WALL_UP | WALL_DOWN: (WallAssetKind.STRAIGHT, 0.0),
    WALL_LEFT | WALL_RIGHT: (WallAssetKind.STRAIGHT, 90.0),
    WALL_UP | WALL_RIGHT: (WallAssetKind.CORNER, 0.0),
    WALL_DOWN | WALL_RIGHT: (WallAssetKind.CORNER, 270.0),
    WALL_DOWN | WALL_LEFT: (WallAssetKind.CORNER, 180.0),
    WALL_UP | WALL_LEFT: (WallAssetKind.CORNER, 90.0),
    WALL_UP | WALL_LEFT | WALL_RIGHT: (WallAssetKind.T_JUNCTION, 0.0),
    WALL_UP | WALL_DOWN | WALL_RIGHT: (WallAssetKind.T_JUNCTION, 270.0),
    WALL_DOWN | WALL_LEFT | WALL_RIGHT: (WallAssetKind.T_JUNCTION, 180.0),
    WALL_UP | WALL_DOWN | WALL_LEFT: (WallAssetKind.T_JUNCTION, 90.0),
    WALL_UP | WALL_RIGHT | WALL_DOWN | WALL_LEFT: (
        WallAssetKind.CROSS,
        0.0,
    ),
}


def is_wall_at(
    grid: list[list[CellState]],
    x: int,
    y: int,
) -> bool:
    """Return True if the grid position is a wall."""
    if y < 0 or y >= len(grid):
        return False
    if x < 0 or x >= len(grid[y]):
        return False

    return grid[y][x] == CellState.WALL


def get_wall_mask(
    grid: list[list[CellState]],
    x: int,
    y: int,
) -> int:
    """Return wall connection mask using up/right/down/left neighbors."""
    mask = 0

    if is_wall_at(grid, x, y - 1):
        mask |= WALL_UP
    if is_wall_at(grid, x + 1, y):
        mask |= WALL_RIGHT
    if is_wall_at(grid, x, y + 1):
        mask |= WALL_DOWN
    if is_wall_at(grid, x - 1, y):
        mask |= WALL_LEFT

    return mask


def get_wall_render_info(
    grid: list[list[CellState]],
    x: int,
    y: int,
) -> tuple[WallAssetKind, float]:
    """Return the wall asset and rotation for neighboring walls."""
    mask = get_wall_mask(grid, x, y)
    return WALL_RENDER_INFO[mask]
