import unittest
from pathlib import Path

from pathfinding.paths import resolve_project_path


class TestResolveProjectPath(unittest.TestCase):
    def test_resolve_absolute_path(self):
        temp_file = Path.cwd() / "test.txt"
        try:
            temp_file.touch()
            resolved = resolve_project_path(temp_file)
            self.assertTrue(resolved.is_absolute())
            self.assertEqual(resolved, temp_file)
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def test_resolve_existing_relative_path(self):
        dummy_file = Path("dummy_test_file.txt")
        try:
            dummy_file.touch()
            resolved = resolve_project_path(dummy_file)
            self.assertEqual(resolved, dummy_file)
        finally:
            if dummy_file.exists():
                dummy_file.unlink()

    def test_resolve_app_relative_path(self):
        resolved = resolve_project_path("maps/tiny.map")
        self.assertTrue(resolved.exists())
        self.assertEqual(resolved.name, "tiny.map")
        self.assertIn("app/maps", resolved.as_posix())

    def test_resolve_nonexistent_path(self):
        resolved = resolve_project_path("nonexistent_directory/nonexistent_file.map")
        self.assertEqual(resolved, Path("nonexistent_directory/nonexistent_file.map"))


if __name__ == "__main__":
    unittest.main()
