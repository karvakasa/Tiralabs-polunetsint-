from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from math import sqrt

from pathfinding.paths import resolve_project_path

Coord = tuple[int, int]

PASSABLE = {".", "G"}
BLOCKED = {"@", "O", "T"}
SQRT2 = sqrt(2)


@dataclass(frozen=True)
class GridMap:
    width: int
    height: int
    rows: tuple[str, ...]

    @classmethod
    def from_file(cls, path: str | Path) -> "GridMap":
        lines = resolve_project_path(path).read_text(
            encoding="utf-8").splitlines()
        return cls.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: list[str]) -> "GridMap":
        header: dict[str, str] = {}
        map_index = None
        for index, raw in enumerate(lines):
            line = raw.strip()
            if not line:
                continue
            if line == "map":
                map_index = index + 1
                break
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                header[parts[0]] = parts[1]

        if map_index is None:
            raise ValueError("missing 'map' marker")
        if header.get("type") != "octile":
            raise ValueError("only Moving AI 'type octile' maps are supported")

        width = int(header["width"])
        height = int(header["height"])
        rows = tuple(line.rstrip("\n")
                     for line in lines[map_index: map_index + height])
        if len(rows) != height:
            raise ValueError(f"expected {height} map rows, got {len(rows)}")
        if any(len(row) != width for row in rows):
            raise ValueError("all map rows must match declared width")
        return cls(width=width, height=height, rows=rows)

    def in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height

    def terrain(self, coord: Coord) -> str:
        x, y = coord
        return self.rows[y][x]

    def passable(self, coord: Coord) -> bool:
        return self.in_bounds(coord) and self.terrain(coord) in PASSABLE

    def can_move(self, current: Coord, direction: Coord) -> bool:
        dx, dy = direction
        if dx == 0 and dy == 0:
            return False
        if abs(dx) > 1 or abs(dy) > 1:
            raise ValueError("direction must be normalized")
        x, y = current
        target = (x + dx, y + dy)
        if not self.passable(target):
            return False
        if dx != 0 and dy != 0:
            return self.passable((x + dx, y)) and self.passable((x, y + dy))
        return True

    def neighbors(self, coord: Coord) -> list[tuple[Coord, float]]:
        found: list[tuple[Coord, float]] = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if self.can_move(coord, (dx, dy)):
                    cost = SQRT2 if dx != 0 and dy != 0 else 1.0
                    x, y = coord
                    found.append(((x + dx, y + dy), cost))
        return found
