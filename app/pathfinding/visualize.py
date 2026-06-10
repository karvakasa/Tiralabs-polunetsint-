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

def render_svg(
    grid: GridMap,
    result: SearchResult,
    start: Coord,
    goal: Coord,
    cell_size: int = 6,
) -> str:
    width = grid.width * cell_size
    height = grid.height * cell_size
    path = set(result.path)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'style="max-width: 100%; height: auto;">',
        "<title>Pathfinding result</title>",
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
    ]

    for y, row in enumerate(grid.rows):
        for x, _ in enumerate(row):
            coord = (x, y)
            fill = _cell_color(grid, result, path, coord, start, goal)
            parts.append(
                f'<rect x="{x * cell_size}" y="{y * cell_size}" '
                f'width="{cell_size}" height="{cell_size}" fill="{fill}"/>'
            )

    if len(result.path) > 1:
        points = " ".join(
            f"{x * cell_size + cell_size / 2:.1f},{y * cell_size + cell_size / 2:.1f}"
            for x, y in result.path
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="#ef4444" '
            f'stroke-width="{max(2, cell_size // 4)}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def render_html(
    grid: GridMap,
    result: SearchResult,
    start: Coord,
    goal: Coord,
    cell_size: int = 6,
    algorithm: str | None = None,
    expected: float | None = None,
) -> str:
    svg = render_svg(grid, result, start, goal, cell_size=cell_size)
    algorithm_label = algorithm or "unknown"
    path_steps = _coord_list(result.path)
    visited_cells = _coord_list(sorted(result.visited, key=lambda item: (item[1], item[0])))
    jump_points = _coord_list(sorted(result.jump_points, key=lambda item: (item[1], item[0])))
    expected_html = (
        f"<div><strong>Expected cost</strong><span>{expected:.5f}</span></div>"
        f"<div><strong>Matches expected</strong><span>{abs(result.cost - expected) <= 1e-5}</span></div>"
        if expected is not None
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pathfinding result</title>
  <style>
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f8fafc;
      color: #0f172a;
    }}
    main {{
      padding: 24px;
    }}
    h1 {{
      margin: 0 0 16px;
      font-size: 28px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }}
    .summary div {{
      border: 1px solid #cbd5e1;
      background: #ffffff;
      padding: 10px;
    }}
    .summary strong {{
      display: block;
      color: #475569;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .summary span {{
      display: block;
      margin-top: 4px;
      font-size: 18px;
      font-variant-numeric: tabular-nums;
    }}
    .map {{
      overflow: auto;
      border: 1px solid #cbd5e1;
      background: white;
      max-width: 100%;
    }}
    .map svg {{
      display: block;
      max-width: 100%;
      width: min(100%, 960px);
      height: auto;
      image-rendering: pixelated;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
      font-size: 14px;
    }}
    .legend span {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .swatch {{
      width: 14px;
      height: 14px;
      border: 1px solid #94a3b8;
    }}
    .details {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    details {{
      border: 1px solid #cbd5e1;
      background: #ffffff;
      padding: 12px;
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
    .coords {{
      margin: 10px 0 0;
      max-height: 280px;
      overflow: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.5;
    }}
    .coords li {{
      padding-right: 8px;
    }}
    .notes {{
      margin: 18px 0 0;
      color: #475569;
      max-width: 900px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Pathfinding result</h1>
    <section class="summary" aria-label="Search summary">
      <div><strong>Algorithm</strong><span>{algorithm_label}</span></div>
      <div><strong>Cost</strong><span>{result.cost:.5f}</span></div>
      {expected_html}
      <div><strong>Path cells</strong><span>{len(result.path)}</span></div>
      <div><strong>Expanded</strong><span>{result.expanded}</span></div>
      <div><strong>Visited</strong><span>{len(result.visited)}</span></div>
      <div><strong>Jump points</strong><span>{len(result.jump_points)}</span></div>
      <div><strong>Runtime ms</strong><span>{result.runtime_ms:.3f}</span></div>
      <div><strong>Start</strong><span>{start}</span></div>
      <div><strong>Goal</strong><span>{goal}</span></div>
      <div><strong>Grid</strong><span>{grid.width} x {grid.height}</span></div>
    </section>
    <div class="legend">
      <span><i class="swatch" style="background:#22c55e"></i>Start</span>
      <span><i class="swatch" style="background:#f97316"></i>Goal</span>
      <span><i class="swatch" style="background:#ef4444"></i>Path line</span>
      <span><i class="swatch" style="background:#bfdbfe"></i>Visited</span>
      <span><i class="swatch" style="background:#8b5cf6"></i>Jump point</span>
      <span><i class="swatch" style="background:#0f172a"></i>Blocked</span>
    </div>
    <div class="map">
{svg}
    </div>
    <section class="details" aria-label="Detailed search data">
      <details open>
        <summary>Final path steps ({len(result.path)})</summary>
        <ol class="coords">
{path_steps}
        </ol>
      </details>
      <details>
        <summary>Visited cells ({len(result.visited)})</summary>
        <ol class="coords">
{visited_cells}
        </ol>
      </details>
      <details>
        <summary>JPS jump points ({len(result.jump_points)})</summary>
        <ol class="coords">
{jump_points}
        </ol>
      </details>
    </section>
    <p class="notes">
      The final path steps are shown in movement order from start to goal.
      Visited cells are the cells touched by the search and are sorted by row for readability.
      JPS jump points are shown only for the JPS algorithm.
    </p>
  </main>
</body>
</html>
"""


def _coord_list(coords: list[Coord]) -> str:
    if not coords:
        return "          <li>None</li>"
    return "\n".join(f"          <li>({x}, {y})</li>" for x, y in coords)


def _cell_color(
    grid: GridMap,
    result: SearchResult,
    path: set[Coord],
    coord: Coord,
    start: Coord,
    goal: Coord,
) -> str:
    if coord == start:
        return "#22c55e"
    if coord == goal:
        return "#f97316"
    if not grid.passable(coord):
        return "#0f172a"
    if coord in result.jump_points:
        return "#8b5cf6"
    if coord in path:
        return "#fecaca"
    if coord in result.visited:
        return "#bfdbfe"
    return "#ffffff"
