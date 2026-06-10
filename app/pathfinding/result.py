from __future__ import annotations

from dataclasses import dataclass, field

Coord = tuple[int, int]


@dataclass(frozen=True)
class SearchResult:
    path: list[Coord]
    cost: float
    expanded: int
    visited: set[Coord] = field(default_factory=set)
    jump_points: set[Coord] = field(default_factory=set)
    runtime_ms: float = 0.0

    @property
    def found(self) -> bool:
        return bool(self.path)
