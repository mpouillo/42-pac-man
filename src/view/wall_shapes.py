from enum import Enum

from src.types.enums import CellState


WALL_UP = 1
WALL_RIGHT = 2
WALL_DOWN = 4
WALL_LEFT = 8


class WallShape(Enum):
    """All possible wall neighbor connection shapes."""

    ISOLATED = "isolated"

    END_UP = "end_up"
    END_RIGHT = "end_right"
    END_DOWN = "end_down"
    END_LEFT = "end_left"

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    CORNER_UP_LEFT = "corner_up_left"
    CORNER_UP_RIGHT = "corner_up_right"
    CORNER_DOWN_LEFT = "corner_down_left"
    CORNER_DOWN_RIGHT = "corner_down_right"

    T_UP_LEFT_RIGHT = "t_up_left_right"
    T_DOWN_LEFT_RIGHT = "t_down_left_right"
    T_UP_DOWN_LEFT = "t_up_down_left"
    T_UP_DOWN_RIGHT = "t_up_down_right"

    CROSS = "cross"


class WallAssetKind(Enum):
    """Base wall asset type before rotation."""

    ISOLATED = "isolated"
    END = "end"
    STRAIGHT = "straight"
    CORNER = "corner"
    T_JUNCTION = "t_junction"
    CROSS = "cross"


WALL_MASK_TO_SHAPE = {
    0: WallShape.ISOLATED,

    WALL_UP: WallShape.END_UP,
    WALL_RIGHT: WallShape.END_RIGHT,
    WALL_DOWN: WallShape.END_DOWN,
    WALL_LEFT: WallShape.END_LEFT,

    WALL_UP | WALL_DOWN: WallShape.VERTICAL,
    WALL_LEFT | WALL_RIGHT: WallShape.HORIZONTAL,

    WALL_UP | WALL_LEFT: WallShape.CORNER_UP_LEFT,
    WALL_UP | WALL_RIGHT: WallShape.CORNER_UP_RIGHT,
    WALL_DOWN | WALL_LEFT: WallShape.CORNER_DOWN_LEFT,
    WALL_DOWN | WALL_RIGHT: WallShape.CORNER_DOWN_RIGHT,

    WALL_UP | WALL_LEFT | WALL_RIGHT: WallShape.T_UP_LEFT_RIGHT,
    WALL_DOWN | WALL_LEFT | WALL_RIGHT: WallShape.T_DOWN_LEFT_RIGHT,
    WALL_UP | WALL_DOWN | WALL_LEFT: WallShape.T_UP_DOWN_LEFT,
    WALL_UP | WALL_DOWN | WALL_RIGHT: WallShape.T_UP_DOWN_RIGHT,

    WALL_UP | WALL_RIGHT | WALL_DOWN | WALL_LEFT: WallShape.CROSS,
}


WALL_SHAPE_RENDER_INFO = {
    WallShape.ISOLATED: (WallAssetKind.ISOLATED, 0.0),

    WallShape.END_UP: (WallAssetKind.END, 0.0),
    WallShape.END_RIGHT: (WallAssetKind.END, 270.0),
    WallShape.END_DOWN: (WallAssetKind.END, 180.0),
    WallShape.END_LEFT: (WallAssetKind.END, 90.0),

    WallShape.VERTICAL: (WallAssetKind.STRAIGHT, 0.0),
    WallShape.HORIZONTAL: (WallAssetKind.STRAIGHT, 90.0),

    WallShape.CORNER_UP_RIGHT: (WallAssetKind.CORNER, 0.0),
    WallShape.CORNER_DOWN_RIGHT: (WallAssetKind.CORNER, 270.0),
    WallShape.CORNER_DOWN_LEFT: (WallAssetKind.CORNER, 180.0),
    WallShape.CORNER_UP_LEFT: (WallAssetKind.CORNER, 90.0),

    WallShape.T_UP_LEFT_RIGHT: (WallAssetKind.T_JUNCTION, 0.0),
    WallShape.T_UP_DOWN_RIGHT: (WallAssetKind.T_JUNCTION, 270.0),
    WallShape.T_DOWN_LEFT_RIGHT: (WallAssetKind.T_JUNCTION, 180.0),
    WallShape.T_UP_DOWN_LEFT: (WallAssetKind.T_JUNCTION, 90.0),

    WallShape.CROSS: (WallAssetKind.CROSS, 0.0),
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


def get_wall_shape(
    grid: list[list[CellState]],
    x: int,
    y: int,
) -> WallShape:
    """Return the wall shape according to neighboring walls."""
    mask = get_wall_mask(grid, x, y)
    return WALL_MASK_TO_SHAPE[mask]
