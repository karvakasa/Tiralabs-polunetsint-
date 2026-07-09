from __future__ import annotations
import argparse
import sys
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from math import isclose
from pathlib import Path
from time import perf_counter
from pathfinding.astar import astar
from pathfinding.grid import GridMap
from pathfinding.jps import jps
from pathfinding.result import Coord
from pathfinding.result import SearchResult
from pathfinding.scenarios import Scenario
from pathfinding.scenarios import load_scenarios


APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


MAPS_DIR = APP_DIR / "maps"
BENCHMARKS = [
    ("Berlin.map", 300, "700-1550 length routes", True, 700, 1550),
    ("big.map", 150, "200-370 length routes", True, 200, 370),
    ("tiny.map", 50, "1-8 length routes", False, 1, 8),
]
COST_TOLERANCE = 1e-4
SearchFn = Callable[[GridMap, Coord, Coord], SearchResult]


@dataclass(frozen=True)
class TimedResult:
    result: SearchResult
    runtime_ms: float


def measure(func: SearchFn, grid: GridMap, start: Coord, goal: Coord) -> TimedResult:
    start_time = perf_counter()
    result = func(grid, start, goal)
    return TimedResult(result, (perf_counter() - start_time) * 1000)


def select_scenarios(
    scenarios: list[Scenario],
    target_count: int,
    prefer_long: bool,
    min_length: float,
    max_length: float,
) -> list[Scenario]:
    by_bucket: dict[int, list[Scenario]] = defaultdict(list)
    for scenario in scenarios:
        if not min_length <= scenario.optimal_length <= max_length:
            continue
        by_bucket[scenario.bucket].append(scenario)

    if not by_bucket:
        return []

    per_bucket = (target_count + len(by_bucket) - 1) // len(by_bucket)
    selected = []
    for bucket in sorted(by_bucket, reverse=prefer_long):
        bucket_scenarios = sorted(
            by_bucket[bucket],
            key=lambda scenario: scenario.optimal_length,
            reverse=prefer_long,
        )
        selected.extend(bucket_scenarios[:per_bucket])

    selected = selected[:target_count]
    if selected and len(selected) < target_count:
        repeats_needed = target_count - len(selected)
        selected.extend(
            selected[index % len(selected)]
            for index in range(repeats_needed)
        )
    return selected


def run_benchmark(
    map_name: str,
    target_count: int,
    profile: str,
    prefer_long: bool,
    min_length: float,
    max_length: float,
) -> int:
    map_path = MAPS_DIR / map_name
    scen_path = map_path.with_suffix(".map.scen")
    _require_file(map_path, "map")
    _require_file(scen_path, "scenario")

    print(f"Loading map:  {map_path}")
    grid = GridMap.from_file(map_path)
    print(f"  {grid.width}x{grid.height} grid loaded.")

    print(f"Loading scen: {scen_path}")
    all_scenarios = load_scenarios(scen_path)
    _validate_scenarios(all_scenarios, grid)
    print(f"  {len(all_scenarios)} scenarios found.\n")

    selected = select_scenarios(
        all_scenarios,
        target_count,
        prefer_long,
        min_length,
        max_length,
    )
    if not selected:
        raise SystemExit(
            f"No scenarios selected for {map_name} "
            f"with route length {min_length}-{max_length}."
        )

    print(
        f"Running {len(selected)} {profile} scenarios "
        f"(target {target_count} total, 1 timing run each)...\n"
    )
    lengths = [scenario.optimal_length for scenario in selected]
    print(f"Selected route lengths: {min(lengths):.2f} - {max(lengths):.2f}\n")

    bucket_astar_ms: dict[int, list[float]] = defaultdict(list)
    bucket_jps_ms: dict[int, list[float]] = defaultdict(list)
    bucket_astar_exp: dict[int, list[int]] = defaultdict(list)
    bucket_jps_exp: dict[int, list[int]] = defaultdict(list)

    for scenario_number, scenario in enumerate(selected, start=1):
        start = scenario.start
        goal = scenario.goal

        a_run = measure(astar, grid, start, goal)
        j_run = measure(jps, grid, start, goal)
        _validate_results(
            map_name,
            scenario_number,
            scenario,
            a_run.result,
            j_run.result,
        )

        bucket = scenario.bucket
        bucket_astar_ms[bucket].append(a_run.runtime_ms)
        bucket_jps_ms[bucket].append(j_run.runtime_ms)
        bucket_astar_exp[bucket].append(a_run.result.expanded)
        bucket_jps_exp[bucket].append(j_run.result.expanded)

    col = {
        "bucket": 8,
        "n": 5,
        "a_ms": 10,
        "j_ms": 10,
        "speedup": 9,
        "a_exp": 12,
        "j_exp": 12,
        "exp_ratio": 11,
    }
    header = (
        f"{'Bucket':>{col['bucket']}} "
        f"{'N':>{col['n']}} "
        f"{'A*(ms)':>{col['a_ms']}} "
        f"{'JPS(ms)':>{col['j_ms']}} "
        f"{'Speedup':>{col['speedup']}} "
        f"{'A* nodes':>{col['a_exp']}} "
        f"{'JPS nodes':>{col['j_exp']}} "
        f"{'Node ratio':>{col['exp_ratio']}}"
    )
    sep = "-" * len(header)

    print(sep)
    print(header)
    print(sep)

    total_a_ms = total_j_ms = 0.0
    total_a_exp = total_j_exp = 0

    for bucket in sorted(bucket_astar_ms):
        n = len(bucket_astar_ms[bucket])
        a_avg = sum(bucket_astar_ms[bucket]) / n
        j_avg = sum(bucket_jps_ms[bucket]) / n
        a_exp = sum(bucket_astar_exp[bucket]) // n
        j_exp = sum(bucket_jps_exp[bucket]) // n
        speedup = a_avg / j_avg if j_avg > 0 else float("inf")
        node_ratio = a_exp / j_exp if j_exp > 0 else float("inf")

        total_a_ms += sum(bucket_astar_ms[bucket])
        total_j_ms += sum(bucket_jps_ms[bucket])
        total_a_exp += sum(bucket_astar_exp[bucket])
        total_j_exp += sum(bucket_jps_exp[bucket])

        print(
            f"{bucket:>{col['bucket']}} "
            f"{n:>{col['n']}} "
            f"{a_avg:>{col['a_ms']}.3f} "
            f"{j_avg:>{col['j_ms']}.3f} "
            f"{speedup:>{col['speedup']}.2f}x "
            f"{a_exp:>{col['a_exp']},} "
            f"{j_exp:>{col['j_exp']},} "
            f"{node_ratio:>{col['exp_ratio']}.2f}x"
        )

    print(sep)

    n_total = len(selected)
    a_total_avg = total_a_ms / n_total
    j_total_avg = total_j_ms / n_total
    a_exp_avg = total_a_exp // n_total
    j_exp_avg = total_j_exp // n_total
    overall_speedup = a_total_avg / j_total_avg if j_total_avg > 0 else float("inf")
    overall_node_ratio = a_exp_avg / j_exp_avg if j_exp_avg > 0 else float("inf")

    print(
        f"{'OVERALL':>{col['bucket']}} "
        f"{n_total:>{col['n']}} "
        f"{a_total_avg:>{col['a_ms']}.3f} "
        f"{j_total_avg:>{col['j_ms']}.3f} "
        f"{overall_speedup:>{col['speedup']}.2f}x "
        f"{a_exp_avg:>{col['a_exp']},} "
        f"{j_exp_avg:>{col['j_exp']},} "
        f"{overall_node_ratio:>{col['exp_ratio']}.2f}x"
    )
    print(sep)
    print(
        f"\nConclusion: JPS is {overall_speedup:.2f}x faster than A* on average "
        f"and expands {overall_node_ratio:.2f}x fewer nodes."
    )
    return n_total


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"Missing {label} file: {path}")


def _validate_scenarios(
    scenarios: list[Scenario],
    grid: GridMap,
) -> None:
    if not scenarios:
        raise SystemExit("Scenario file did not contain any usable scenarios.")

    for index, scenario in enumerate(scenarios, start=1):
        if scenario.width != grid.width or scenario.height != grid.height:
            raise SystemExit(
                f"Scenario {index} dimensions are {scenario.width}x{scenario.height}, "
                f"but map is {grid.width}x{grid.height}."
            )
        if not grid.passable(scenario.start):
            raise SystemExit(f"Scenario {index} start is not passable: {scenario.start}")
        if not grid.passable(scenario.goal):
            raise SystemExit(f"Scenario {index} goal is not passable: {scenario.goal}")


def _validate_results(
    map_name: str,
    scenario_number: int,
    scenario: Scenario,
    astar_result: SearchResult,
    jps_result: SearchResult,
) -> None:
    label = (
        f"{map_name} scenario {scenario_number} "
        f"{scenario.start}->{scenario.goal}"
    )
    if not astar_result.found:
        raise SystemExit(f"A* did not find a path for {label}.")
    if not jps_result.found:
        raise SystemExit(f"JPS did not find a path for {label}.")
    if not isclose(astar_result.cost, scenario.optimal_length, abs_tol=COST_TOLERANCE):
        raise SystemExit(
            f"A* cost mismatch for {label}: "
            f"got {astar_result.cost:.8f}, expected {scenario.optimal_length:.8f}."
        )
    if not isclose(jps_result.cost, scenario.optimal_length, abs_tol=COST_TOLERANCE):
        raise SystemExit(
            f"JPS cost mismatch for {label}: "
            f"got {jps_result.cost:.8f}, expected {scenario.optimal_length:.8f}."
        )
    if not isclose(astar_result.cost, jps_result.cost, abs_tol=COST_TOLERANCE):
        raise SystemExit(
            f"A* and JPS disagree for {label}: "
            f"{astar_result.cost:.8f} vs {jps_result.cost:.8f}."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the full 500-scenario benchmark",
    )
    args = parser.parse_args()
    if not args.full:
        raise SystemExit("Usage: python3 app/benchmark.py --full")

    total_scenarios = 0
    print(f"Benchmarking {len(BENCHMARKS)} map/scenario pair(s).\n")
    for index, benchmark in enumerate(BENCHMARKS, start=1):
        map_name = benchmark[0]
        scen_name = f"{map_name}.scen"
        print(f"=== Pair {index}/{len(BENCHMARKS)}: {map_name} + {scen_name} ===")
        total_scenarios += run_benchmark(*benchmark)
        print()

    print(
        f"Full benchmark checked {len(BENCHMARKS)} map/scenario pair(s), "
        f"{total_scenarios} scenario(s)."
    )


if __name__ == "__main__":
    main()
