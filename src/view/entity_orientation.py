"""Shared 3D entity orientation helpers."""

from __future__ import annotations

import math

from src.types.enums import Direction


def direction_to_rotation(direction: Direction) -> float:
    """Return model Y-axis rotation from entity direction."""
    match direction:
        case Direction.RIGHT:
            return 90.0
        case Direction.UP:
            return 180.0
        case Direction.LEFT:
            return 270.0
        case Direction.DOWN | Direction.NONE:
            return 0.0
    return 0.0


def direction_from_delta(delta_x: float, delta_z: float) -> Direction:
    """Convert a path segment vector to a gameplay direction."""
    if abs(delta_x) > abs(delta_z):
        if delta_x > 0.0:
            return Direction.RIGHT
        return Direction.LEFT

    if delta_z < 0.0:
        return Direction.UP
    return Direction.DOWN


def yaw_sway_rotation(
    direction: Direction,
    elapsed: float,
    speed: float,
    degrees: float,
) -> float:
    """Return Y-axis rotation with a simple left/right turning sway."""
    sway_degrees = math.sin(elapsed * speed) * degrees
    return direction_to_rotation(direction) + sway_degrees
