from __future__ import annotations

from pathfinding.grid import SQRT2
from pathfinding.result import Coord


def octile(a: Coord, b: Coord) -> float:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (SQRT2 - 1) * min(dx, dy)
