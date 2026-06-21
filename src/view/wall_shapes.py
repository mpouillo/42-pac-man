"""Wall shape detection and model asset mappings."""

from enum import Enum

from src.types.enums import CellState


class WallAssetKind(Enum):
    """Identify wall model shapes with their final direction."""

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


_WALL_ASSET_BY_NEIGHBORS = {
    (False, False, False, False): WallAssetKind.ISOLATED,
    (True, False, False, False): WallAssetKind.END_UP,
    (False, True, False, False): WallAssetKind.END_RIGHT,
    (False, False, True, False): WallAssetKind.END_DOWN,
    (False, False, False, True): WallAssetKind.END_LEFT,
    (True, False, True, False): WallAssetKind.STRAIGHT_VERTICAL,
    (False, True, False, True): WallAssetKind.STRAIGHT_HORIZONTAL,
    (True, True, False, False): WallAssetKind.CORNER_UP_RIGHT,
    (False, True, True, False): WallAssetKind.CORNER_RIGHT_DOWN,
    (False, False, True, True): WallAssetKind.CORNER_DOWN_LEFT,
    (True, False, False, True): WallAssetKind.CORNER_LEFT_UP,
    (True, True, True, False): WallAssetKind.T_UP_RIGHT_DOWN,
    (False, True, True, True): WallAssetKind.T_RIGHT_DOWN_LEFT,
    (True, False, True, True): WallAssetKind.T_DOWN_LEFT_UP,
    (True, True, False, True): WallAssetKind.T_LEFT_UP_RIGHT,
    (True, True, True, True): WallAssetKind.CROSS,
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


def get_wall_asset_kind(
    grid: list[list[CellState]],
    x: int,
    y: int,
) -> WallAssetKind:
    """Return the wall asset matching neighboring walls."""
    neighbors = (
        is_wall_at(grid, x, y - 1),
        is_wall_at(grid, x + 1, y),
        is_wall_at(grid, x, y + 1),
        is_wall_at(grid, x - 1, y),
    )
    return _WALL_ASSET_BY_NEIGHBORS[neighbors]
