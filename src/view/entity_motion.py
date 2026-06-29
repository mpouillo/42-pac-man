"""Shared 3D entity facing and sway helpers."""

import math
from typing import Any

import pyray as ray

from src.constants import ENTITY_SWAY_DEGREES, ENTITY_SWAY_SPEED
from src.types.enums import Direction

DIRECTION_ROTATIONS = {
    Direction.DOWN: 0.0,
    Direction.NONE: 0.0,
    Direction.RIGHT: 90.0,
    Direction.UP: 180.0,
    Direction.LEFT: 270.0,
}


def entity_rotation(direction: Direction, elapsed: float) -> tuple[Any, float]:
    """Return shared facing plus left/right turn sway for 3D entities."""
    base_angle = DIRECTION_ROTATIONS.get(direction, 0.0)
    sway = math.sin(elapsed * ENTITY_SWAY_SPEED) * ENTITY_SWAY_DEGREES
    return ray.Vector3(0.0, 1.0, 0.0), base_angle + sway
