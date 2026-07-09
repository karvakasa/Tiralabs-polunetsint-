from __future__ import annotations

import unittest

from pathfinding.astar import astar
from pathfinding.grid import GridMap
from pathfinding.jps import jps


class TestJPS(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = GridMap.from_lines([
            "type octile",
            "height 5",
            "width 5",
            "map",
            ".....",
            "..@..",
            ".....",
            "..@..",
            ".....",
        ])

    def test_jps_returns_valid_path_on_simple_grid(self) -> None:
        result = jps(self.grid, (0, 0), (4, 4))

        self.assertTrue(result.found)
        self.assertEqual(result.path[0], (0, 0))
        self.assertEqual(result.path[-1], (4, 4))
        self.assertGreaterEqual(len(result.path), 2)
        self.assertTrue(all(self.grid.passable(coord) for coord in result.path))

    def test_jps_matches_astar_cost_on_simple_grid(self) -> None:
        jps_result = jps(self.grid, (0, 0), (4, 4))
        astar_result = astar(self.grid, (0, 0), (4, 4))

        self.assertEqual(jps_result.cost, astar_result.cost)

    def test_jps_reports_goal_as_a_jump_point_for_a_found_path(self) -> None:
        result = jps(self.grid, (0, 0), (4, 4))

        self.assertTrue(result.found)
        self.assertIn((4, 4), result.jump_points)


if __name__ == "__main__":
    unittest.main()
