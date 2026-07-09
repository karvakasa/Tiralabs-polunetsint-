
from __future__ import annotations

from heapq import heappop, heappush
from itertools import count
from math import inf

from pathfinding.grid import GridMap
from pathfinding.heuristics import octile
from pathfinding.result import Coord, SearchResult


def astar(grid: GridMap, start: Coord, goal: Coord) -> SearchResult:

    # Tarkistetaan, että lähtöpiste on kulkukelpoinen

    if not grid.passable(start):
        raise ValueError(f"start is not passable: {start}")

    # Tarkistetaan, että tavoitepiste on kulkukelpoinen

    if not grid.passable(goal):
        raise ValueError(f"goal is not passable: {goal}")

    # Avoin lista solmuille, jotka odottavat käsittelyä
    # Jokainen merkintä sisältää (f-arvo, järjestysnumero, koordinaatit)
    open_heap: list[tuple[float, int, Coord]] = []
    order = count()
    # Lisätään lähtöpiste avoimeen listaan
    heappush(open_heap, (octile(start, goal), next(order), start))

    # Rakennetaan reittiä varten: {nykyinen: edellinen}
    came_from: dict[Coord, Coord] = {}
    # g-arvo (kustannus lähtöpisteestä tähän pisteeseen) kullekin solmulle
    g_score: dict[Coord, float] = {start: 0.0}
    # Suljettu lista jo käsitellyistä solmuista
    closed: set[Coord] = set()
    # Kaikki käydyt solmut hakumenetelmää varten
    visited: set[Coord] = {start}

    # Pääsilmukka: jatkuu kunnes avoin lista on tyhjä
    while open_heap:
        # Haetaan solmu, jolla on pienin f-arvo
        _, _, current = heappop(open_heap)
        # Jos solmu on jo käsitelty, ohitetaan se
        if current in closed:
            continue
        # Merkitään solmu käsitellyksi
        closed.add(current)
        # Tarkistetaan, onko maali löytynyt
        if current == goal:
            return SearchResult(
                path=_reconstruct(came_from, start, goal),
                cost=g_score[goal],
                expanded=len(closed),
                visited=visited,
            )

        # Käydään läpi kaikki naapurisolmut
        for neighbor, move_cost in grid.neighbors(current):
            # Lasketaan väliaikainen g-arvo naapurille
            tentative = g_score[current] + move_cost
            # Jos parempi reitti naapurille on jo löytynyt, ohitetaan
            if tentative >= g_score.get(neighbor, inf):
                continue
            # Päivitetään reitti ja g-arvo
            came_from[neighbor] = current
            g_score[neighbor] = tentative
            visited.add(neighbor)
            # Lisätään naapuri avoimeen listaan
            heappush(open_heap, (tentative +
                     octile(neighbor, goal), next(order), neighbor))

    # Reittiä ei löytynyt
    return SearchResult(path=[], cost=inf, expanded=len(closed), visited=visited)


def _reconstruct(came_from: dict[Coord, Coord], start: Coord, goal: Coord) -> list[Coord]:

    # Aloitetaan maalista ja seurataan polkua taaksepäin
    current = goal
    path = [current]
    # Seurataan came_from -linkityksiä kunnes saavutetaan lähtöpiste
    while current != start:
        current = came_from[current]
        path.append(current)
    # Käännetään polku oikeaan järjestykseen (alusta loppuun)
    path.reverse()
    return path
