from dataclasses import dataclass
from .enums import Direction, GhostState, GhostType


@dataclass
class EntityData:
    x: float
    y: float
    direction: Direction


@dataclass
class GhostData(EntityData):
    type: GhostType
    state: GhostState


@dataclass
class PacmanData(EntityData):
    ...
