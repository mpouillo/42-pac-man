from dataclasses import dataclass
from .enums import Direction, GhostState, GhostType


@dataclass
class EntityData:
    """Data schema representing an entity's position and orientation."""

    x: float
    y: float
    direction: Direction


@dataclass
class GhostData(EntityData):
    """Data schema for a ghost entity, extending basic spatial data."""

    type: GhostType
    state: GhostState


@dataclass
class PacmanData(EntityData):
    """Data schema for the Pacman player entity properties."""

    pass
