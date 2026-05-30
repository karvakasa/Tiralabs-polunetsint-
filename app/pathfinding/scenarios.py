from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pathfinding.paths import resolve_project_path
from pathfinding.result import Coord


@dataclass(frozen=True)
class Scenario:
    bucket: int
    map_path: str
    width: int
    height: int
    start: Coord
    goal: Coord
    optimal_length: float


def load_scenarios(path: str | Path) -> list[Scenario]:
    scenarios: list[Scenario] = []
    for line in resolve_project_path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("version"):
            continue
        fields = stripped.split()
        if len(fields) != 9:
            raise ValueError(f"scenario line must have 9 fields: {line}")
        scenarios.append(
            Scenario(
                bucket=int(fields[0]),
                map_path=fields[1],
                width=int(fields[2]),
                height=int(fields[3]),
                start=(int(fields[4]), int(fields[5])),
                goal=(int(fields[6]), int(fields[7])),
                optimal_length=float(fields[8]),
            )
        )
    return scenarios
