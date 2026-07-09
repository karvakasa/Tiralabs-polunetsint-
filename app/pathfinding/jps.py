from __future__ import annotations

from collections.abc import Callable
from heapq import heappop, heappush
from itertools import count
from math import inf
from time import perf_counter

from pathfinding.grid import GridMap, PASSABLE
from pathfinding.heuristics import octile
from pathfinding.result import Coord, SearchResult

SQRT2 = 1.4142135623730951
PassableFn = Callable[[int, int], bool]

_ALL_DIRS = (
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
)

def jps(grid: GridMap, start: Coord, goal: Coord) -> SearchResult:
    if not grid.passable(start):
        raise ValueError("start not passable")
    if not grid.passable(goal):
        raise ValueError("goal not passable")

    start_time = perf_counter()

    width = grid.width
    gx, gy = goal
    walkable = (
        [[False] * (width + 2)]
        + [
            [False] + [cell in PASSABLE for cell in row] + [False]
            for row in grid.rows
        ]
        + [[False] * (width + 2)]
    )

    def passable(x: int, y: int) -> bool:
        return walkable[y + 1][x + 1]

    def can_step(x: int, y: int, dx: int, dy: int) -> bool:
        nx, ny = x + dx, y + dy
        if not walkable[ny + 1][nx + 1]:
            return False
        if dx != 0 and dy != 0:
            return walkable[y + 1][nx + 1] and walkable[ny + 1][x + 1]
        return True

    def jump(x: int, y: int, dx: int, dy: int) -> tuple[Coord, float] | None:
        distance = 0.0

        while True:
            if not can_step(x, y, dx, dy):
                return None

            distance += SQRT2 if dx != 0 and dy != 0 else 1.0
            x += dx
            y += dy

            if x == gx and y == gy:
                return (x, y), distance

            if _has_forced_neighbor(walkable, x, y, dx, dy):
                return (x, y), distance

            if dx != 0 and dy != 0:
                if jump(x, y, dx, 0) is not None:
                    return (x, y), distance
                if jump(x, y, 0, dy) is not None:
                    return (x, y), distance

    open_heap: list[tuple[float, int, Coord]] = []
    order = count()
    heappush(open_heap, (octile(start, goal), next(order), start))

    g: dict[Coord, float] = {start: 0.0}
    came_from: dict[Coord, Coord] = {}
    jump_points: set[Coord] = set()
    closed: set[Coord] = set()
    visited: set[Coord] = {start}

    while open_heap:
        _, _, current = heappop(open_heap)

        if current in closed:
            continue

        closed.add(current)

        if current == goal:
            total_ms = (perf_counter() - start_time) * 1000
            return SearchResult(
                path=_reconstruct(came_from, start, goal),
                cost=g[current],
                expanded=len(closed),
                visited=visited,
                jump_points=jump_points,
                runtime_ms=total_ms,
            )

        parent = came_from.get(current)
        cx, cy = current

        for dx, dy in _prune_directions(passable, can_step, cx, cy, parent):
            result = jump(cx, cy, dx, dy)
            if result is None:
                continue

            node, distance = result
            new_cost = g[current] + distance
            if new_cost < g.get(node, inf):
                g[node] = new_cost
                came_from[node] = current
                visited.add(node)
                jump_points.add(node)
                closed.discard(node)

                heappush(
                    open_heap,
                    (new_cost + octile(node, goal), next(order), node),
                )

    total_ms = (perf_counter() - start_time) * 1000
    return SearchResult(
        [],
        inf,
        len(closed),
        visited,
        jump_points=jump_points,
        runtime_ms=total_ms,
    )


def _prune_directions(
    passable: PassableFn, can_step: Callable[[int, int, int, int], bool],
    x: int,
    y: int,
    parent: Coord | None,
) -> list[Coord]:
    # Jos solmulla ei ole vanhempaa, se on lähtöpiste, joten kaikki suunnat ovat sallittuja.
    if parent is None:
        return [
            (dx, dy)
            for dx, dy in _ALL_DIRS
            if can_step(x, y, dx, dy)
        ]

    # Lasketaan suunnat vanhemmasta solmusta nykyiseen solmuun.
    px, py = parent
    dx = x - px
    dy = y - py
    dx = 0 if dx == 0 else (1 if dx > 0 else -1)
    dy = 0 if dy == 0 else (1 if dy > 0 else -1)

    dirs: list[Coord] = []

    # Jos liike on diagonaalinen, tarkistetaan kaikki kolme mahdollista suuntaa.
    if dx != 0 and dy != 0:
        if can_step(x, y, dx, 0):
            dirs.append((dx, 0))
        if can_step(x, y, 0, dy):
            dirs.append((0, dy))
        if can_step(x, y, dx, dy):
            dirs.append((dx, dy))
        return dirs

    if dx != 0:
        if can_step(x, y, dx, 0):
            dirs.append((dx, 0))

        # Sivusuunnat lisätään vain, jos este
        # edellisessä rivissä pakottaa tutkimaan tämän vaihtoehdon.
        for side_dy in (-1, 1):
            if passable(x, y + side_dy) and not passable(x - dx, y + side_dy):
                dirs.append((0, side_dy))
                if can_step(x, y, dx, side_dy):
                    dirs.append((dx, side_dy))
        return dirs

    #
    if dy != 0:
        if can_step(x, y, 0, dy):
            dirs.append((0, dy))

        # Sivusuunnat lisätään vain, jos este
        for side_dx in (-1, 1):
            if passable(x + side_dx, y) and not passable(x + side_dx, y - dy):
                dirs.append((side_dx, 0))
                if can_step(x, y, side_dx, dy):
                    dirs.append((side_dx, dy))
        return dirs

    return dirs


def _has_forced_neighbor(
    walkable: list[list[bool]],
    x: int,
    y: int,
    dx: int,
    dy: int,
) -> bool:
    # Jos liike on diagonaalinen, tarkistetaan molemmat sivusuunnat.
    if dx != 0 and dy != 0:
        return False

    if dx != 0:
        cx = x + 1
        px = x - dx + 1
        for side_dy in (-1, 1):
            sy = y + side_dy + 1
            # Jos sivusuunta on liikuttavissa,
            #mutta edellinen solmu ei ole käveltävissä, se on pakotettu naapuri.
            if walkable[sy][cx] and not walkable[sy][px]:
                return True
        return False

    if dy != 0:
        cy = y + 1
        py = y - dy + 1
        for side_dx in (-1, 1):
            sx = x + side_dx + 1
            # Jos sivusuunta on liikuttavissa,
            # mutta edellinen solmu ei ole käveltävissä, se on pakotettu naapuri.
            if walkable[cy][sx] and not walkable[py][sx]:
                return True
        return False

    return False


def _move_cost(dx: int, dy: int) -> float:
    return SQRT2 if dx != 0 and dy != 0 else 1.0


def _reconstruct(came_from: dict[Coord, Coord], start: Coord, goal: Coord) -> list[Coord]:
    jump_path = [goal]
    current = goal

    while current != start:
        current = came_from[current]
        jump_path.append(current)

    jump_path.reverse()
    path = [start]

    for current, next_node in zip(jump_path, jump_path[1:]):
        dx = _sign(next_node[0] - current[0])
        dy = _sign(next_node[1] - current[1])
        x, y = current
        while (x, y) != next_node:
            x += dx
            y += dy
            path.append((x, y))

    return path


def _sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0
