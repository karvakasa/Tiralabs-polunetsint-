import unittest
from math import inf, isclose

from pathfinding.astar import astar
from pathfinding.grid import GridMap
from pathfinding.scenarios import load_scenarios


class TestAStar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = GridMap.from_file("./maps/tiny.map")

    def test_astar_finds_route(self):
        result = astar(self.grid, (1, 1), (7, 4))

        self.assertEqual(result.path[0], (1, 1))
        self.assertEqual(result.path[-1], (7, 4))
        self.assertTrue(isclose(result.cost, 7.82842712474619))

    def test_scenarios_match_expected_lengths(self):
        scenarios = load_scenarios("./maps/tiny.map.scen")

        self.assertTrue(scenarios)
        for scenario in scenarios:
            result = astar(self.grid, scenario.start, scenario.goal)
            self.assertTrue(isclose(result.cost, scenario.optimal_length, abs_tol=1e-4))

    def test_astar_rejects_impassable_start(self):
        with self.assertRaisesRegex(ValueError, "start is not passable"):
            astar(self.grid, (0, 0), (7, 4))

    def test_astar_rejects_impassable_goal(self):
        with self.assertRaisesRegex(ValueError, "goal is not passable"):
            astar(self.grid, (1, 1), (0, 0))

    def test_astar_single_cell_path(self):
        result = astar(self.grid, (1, 1), (1, 1))

        self.assertEqual(result.path, [(1, 1)])
        self.assertEqual(result.cost, 0.0)
        self.assertTrue(result.found)

    def test_astar_unreachable_goal(self):
        grid = GridMap.from_lines([
            "type octile",
            "height 3",
            "width 3",
            "map",
            "...",
            "@@@",
            "...",
        ])

        result = astar(grid, (0, 0), (0, 2))

        self.assertFalse(result.found)
        self.assertEqual(result.path, [])
        self.assertEqual(result.cost, inf)

    def test_astar_rejects_out_of_bounds_start(self):
        with self.assertRaisesRegex(ValueError, "start is not passable"):
            astar(self.grid, (-1, 0), (7, 4))

    def test_astar_visited_set_tracks_all_explored_cells(self):
        result = astar(self.grid, (1, 1), (7, 4))

        self.assertIn((1, 1), result.visited)
        self.assertIn((7, 4), result.visited)
        self.assertGreaterEqual(len(result.visited), len(result.path))
        self.assertTrue(all(cell in result.visited for cell in result.path))

    def test_astar_path_is_connected(self):
        result = astar(self.grid, (1, 1), (7, 4))

        for current, next_cell in zip(result.path, result.path[1:]):
            neighbors = dict(self.grid.neighbors(current))
            self.assertIn(next_cell, neighbors, f"Path broken: {current} -> {next_cell} not adjacent")

    def test_astar_path_cost_matches_sum(self):
        result = astar(self.grid, (1, 1), (7, 4))

        calculated_cost = 0.0
        for current, next_cell in zip(result.path, result.path[1:]):
            neighbors = dict(self.grid.neighbors(current))
            calculated_cost += neighbors[next_cell]

        self.assertTrue(isclose(calculated_cost, result.cost),
                        f"Cost mismatch: calculated {calculated_cost}, got {result.cost}")


if __name__ == "__main__":
    unittest.main()
