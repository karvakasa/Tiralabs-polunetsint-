from __future__ import annotations
from math import sqrt
from pathfinding.result import Coord

sqrt2 = sqrt(2)


def octile(a: Coord, b: Coord) -> float:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (sqrt2 - 1) * min(dx, dy)

def step_cost(a: Coord, b: Coord) -> float:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    if dx == 0 and dy == 0:
        return 0.0
    if dx == dy:
        return dx * sqrt2
    return max(dx, dy) + (sqrt2 - 1) * min(dx, dy)
