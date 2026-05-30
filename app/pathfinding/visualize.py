from __future__ import annotations

from pathfinding.grid import GridMap
from pathfinding.result import Coord, SearchResult


def render_ascii(grid: GridMap, result: SearchResult, start: Coord, goal: Coord) -> str:
    path = set(result.path)
    lines: list[str] = []
    for y, row in enumerate(grid.rows):
        chars: list[str] = []
        for x, terrain in enumerate(row):
            coord = (x, y)
            if coord == start:
                chars.append("S")
            elif coord == goal:
                chars.append("E")
            elif coord in path:
                chars.append("*")
            elif coord in result.visited:
                chars.append("+")
            elif not grid.passable(coord):
                chars.append("#")
            else:
                chars.append(".")
        lines.append("".join(chars))
    return "\n".join(lines)
