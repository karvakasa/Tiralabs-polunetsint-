from __future__ import annotations

import argparse
from dataclasses import replace
from math import isinf
from time import perf_counter
from pathlib import Path
from pathfinding.astar import astar
from pathfinding.jps import jps
from pathfinding.grid import GridMap
from pathfinding.scenarios import load_scenarios
from pathfinding.visualize import render_ascii , render_html, render_svg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pathfinding")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run one pathfinding query")
    run_parser.add_argument("--map", required=True,
                            help="path to Moving AI .map file")
    run_parser.add_argument("--start", type=_coord,
                            help="start coordinate as X,Y")
    run_parser.add_argument("--goal", type=_coord,
                            help="goal coordinate as X,Y")
    run_parser.add_argument("--scen", help="path to Moving AI .scen file")
    run_parser.add_argument(
        "--case", type=int, help="1-based scenario case number to run")
    run_parser.add_argument("--algorithm", choices=["astar", "jps"], default="astar")
    run_parser.add_argument("--show", action="store_true",
                            help="print ASCII visualization")
    run_parser.add_argument("--output",
                            help="write HTML visualization to this path")

    subparsers.add_parser(
        "interactive", help="choose route options from prompts")

    args = parser.parse_args(argv)
    if args.command == "run":
        return _run(args)
    if args.command == "interactive":
        return _interactive()
    return 2


def _coord(raw: str) -> tuple[int, int]:
    try:
        x_raw, y_raw = raw.split(",", maxsplit=1)
        return int(x_raw), int(y_raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "coordinate must use X,Y format") from exc


def _run(args: argparse.Namespace) -> int:
    grid = GridMap.from_file(args.map)
    start, goal, expected = _route_request(args)
    start_time = perf_counter()
    algorithm_fn = astar if args.algorithm == "astar" else jps
    result = replace(algorithm_fn(grid, start, goal), runtime_ms=(
        perf_counter() - start_time) * 1000)
    _print_result(args.algorithm, result)
    if expected is not None:
        print(f"expected: {expected:.5f}")
        print(f"matches_expected: {abs(result.cost - expected) <= 1e-5}")
    if args.show:
        print()
        print(render_ascii(grid, result, start, goal))
    if args.output:
        output_path = Path(args.output)
        visual = (
            render_html(grid, result, start, goal, algorithm=args.algorithm, expected=expected)
            if output_path.suffix.lower() in {".html", ".htm"}
            else render_svg(grid, result, start, goal)
        )
        output_path.write_text(visual, encoding="utf-8")

        if args.output == "route.html":
            print(f"wrote: {args.output}")

    return 0 if result.found else 1


def _route_request(args: argparse.Namespace) -> tuple[tuple[int, int], tuple[int, int], float | None]:
    if args.scen or args.case:
        if not args.scen or args.case is None:
            raise SystemExit("--scen and --case must be used together")
        scenarios = load_scenarios(args.scen)
        if args.case < 1 or args.case > len(scenarios):
            raise SystemExit(f"--case must be between 1 and {len(scenarios)}")
        scenario = scenarios[args.case - 1]
        return scenario.start, scenario.goal, scenario.optimal_length

    if args.start is None or args.goal is None:
        raise SystemExit(
            "provide either --start and --goal, or --scen and --case")
    return args.start, args.goal, None


def _interactive() -> int:
    print("Pathfinding CLI")
    map_path = _prompt("Map file", default="./maps/tiny.map")
    print("Route source")
    print("1) Manual start/goal coordinates")
    print("2) Scenario case from .scen file")
    route_source = _choice("Choose route source", {"1", "2"}, default="1")

    start = None
    goal = None
    scen = None
    case = None
    if route_source == "2":
        scen = _prompt("Scenario file", default="./maps/tiny.map.scen")
        case = int(_prompt("Scenario case number", default="1"))
    else:
        start = _coord(_prompt("Start coordinate X,Y", default="1,1"))
        goal = _coord(_prompt("Goal coordinate X,Y", default="7,4"))

    print("Algorithm")
    print("1) A*")
    print("2) JPS")
    algorithm_choice = _choice("Choose algorithm", {"1", "2"}, default="1")
    algorithm = "astar" if algorithm_choice == "1" else "jps"

    show = _yes_no("Show ASCII result", default=True)
    make_html = _yes_no("Create HTML result", default=True)
    output = "route.html" if make_html else None
    args = argparse.Namespace(
        map=map_path,
        start=start,
        goal=goal,
        scen=scen,
        case=case,
        algorithm=algorithm,
        show=show,
        output=output or None,
    )
    return _run(args)


def _prompt(label: str, default: str) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def _choice(label: str, choices: set[str], default: str) -> str:
    while True:
        value = _prompt(label, default=default)
        if value in choices:
            return value
        print(f"Choose one of: {', '.join(sorted(choices))}")


def _yes_no(label: str, default: bool) -> bool:
    default_text = "y" if default else "n"
    while True:
        value = _prompt(f"{label} [y/n]", default=default_text).lower()
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Choose y or n")


def _print_result(name: str, result) -> None:
    cost = "inf" if isinf(result.cost) else f"{result.cost:.5f}"
    print(f"algorithm: {name}")
    print(f"found: {result.found}")
    print(f"cost: {cost}")
    print(f"path_length: {len(result.path)}")
    print(f"expanded: {result.expanded}")
    print(f"visited: {len(result.visited)}")
    print(f"jump_points: {len(result.jump_points)}")
    print(f"runtime_ms: {result.runtime_ms:.3f}")
