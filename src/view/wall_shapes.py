"""Wall shape detection and model asset mappings."""

from enum import Enum

from src.types.enums import CellState


WALL_UP = 1
WALL_RIGHT = 2
WALL_DOWN = 4
WALL_LEFT = 8


class WallAssetKind(Enum):
    """Wall asset type with final direction already included."""

    ISOLATED = "isolated"

    END_UP = "end_up"
    END_RIGHT = "end_right"
    END_DOWN = "end_down"
    END_LEFT = "end_left"

    STRAIGHT_VERTICAL = "straight_vertical"
    STRAIGHT_HORIZONTAL = "straight_horizontal"

    CORNER_UP_RIGHT = "corner_up_right"
    CORNER_RIGHT_DOWN = "corner_right_down"
    CORNER_DOWN_LEFT = "corner_down_left"
    CORNER_LEFT_UP = "corner_left_up"

    T_UP_RIGHT_DOWN = "t_up_right_down"
    T_RIGHT_DOWN_LEFT = "t_right_down_left"
    T_DOWN_LEFT_UP = "t_down_left_up"
    T_LEFT_UP_RIGHT = "t_left_up_right"

    CROSS = "cross"


WALL_ASSET_BY_MASK = {
    0: WallAssetKind.ISOLATED,
    WALL_UP: WallAssetKind.END_UP,
    WALL_RIGHT: WallAssetKind.END_RIGHT,
    WALL_DOWN: WallAssetKind.END_DOWN,
    WALL_LEFT: WallAssetKind.END_LEFT,
    WALL_UP | WALL_DOWN: WallAssetKind.STRAIGHT_VERTICAL,
    WALL_LEFT | WALL_RIGHT: WallAssetKind.STRAIGHT_HORIZONTAL,
    WALL_UP | WALL_RIGHT: WallAssetKind.CORNER_UP_RIGHT,
    WALL_RIGHT | WALL_DOWN: WallAssetKind.CORNER_RIGHT_DOWN,
    WALL_DOWN | WALL_LEFT: WallAssetKind.CORNER_DOWN_LEFT,
    WALL_LEFT | WALL_UP: WallAssetKind.CORNER_LEFT_UP,
    WALL_UP | WALL_RIGHT | WALL_DOWN: WallAssetKind.T_UP_RIGHT_DOWN,
    WALL_RIGHT | WALL_DOWN | WALL_LEFT: WallAssetKind.T_RIGHT_DOWN_LEFT,
    WALL_DOWN | WALL_LEFT | WALL_UP: WallAssetKind.T_DOWN_LEFT_UP,
    WALL_LEFT | WALL_UP | WALL_RIGHT: WallAssetKind.T_LEFT_UP_RIGHT,
    WALL_UP | WALL_RIGHT | WALL_DOWN | WALL_LEFT: WallAssetKind.CROSS,
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


def get_wall_asset_kind(
    grid: list[list[CellState]],
    x: int,
    y: int,
) -> WallAssetKind:
    """Return the wall asset matching neighboring walls."""
    mask = get_wall_mask(grid, x, y)
    return WALL_ASSET_BY_MASK[mask]
