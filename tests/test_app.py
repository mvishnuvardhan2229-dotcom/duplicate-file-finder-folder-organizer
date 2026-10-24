import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_duplicate_finder"))
import app


class DuplicateFinderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "a.txt").write_text("hello", encoding="utf-8")
        (self.root / "b.txt").write_text("hello", encoding="utf-8")
        (self.root / "c.txt").write_text("world", encoding="utf-8")
        (self.root / "sub").mkdir()
        (self.root / "sub" / "d.txt").write_text("hello", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_identical_contents_with_different_names(self):
        _, count, groups, rows, waste = app.scan(self.root)
        self.assertEqual(count, 4)
        self.assertEqual(len(groups), 1)
        self.assertEqual(waste, 10)
        self.assertEqual(len(rows), 3)

    def test_different_contents_not_duplicates(self):
        _, _, groups, _, _ = app.scan(self.root)
        paths = [p for g in groups for p in g["paths"]]
        self.assertNotIn(str(self.root / "c.txt"), paths)

    def test_extension_filter(self):
        _, count, groups, _, _ = app.scan(self.root, ".txt")
        self.assertEqual(count, 4)
        self.assertEqual(len(groups), 1)

    def test_minimum_size_filter(self):
        _, count, groups, _, _ = app.scan(self.root, "All file types", 6)
        self.assertEqual(count, 0)
        self.assertEqual(len(groups), 0)

    def test_invalid_folder_rejected(self):
        with self.assertRaises(ValueError):
            app.scan(self.root / "missing")

    def test_organized_folder_is_excluded(self):
        organized = self.root / "_organized" / "txt"
        organized.mkdir(parents=True)
        (organized / "copy.txt").write_text("hello", encoding="utf-8")
        _, count, groups, _, _ = app.scan(self.root)
        self.assertEqual(count, 4)
        self.assertEqual(len(groups), 1)

    def test_plan_preserves_sources_and_unique_destinations(self):
        files = [str(self.root / "a.txt"), str(self.root / "sub" / "d.txt")]
        plan = app.build_plan(self.root, files)
        self.assertEqual(len(plan), 2)
        self.assertNotEqual(plan[0][1], plan[1][1])
        self.assertTrue(all(Path(source).exists() for source, _ in plan))

    def test_fingerprint_is_stable(self):
        self.assertEqual(app.fingerprint(self.root / "a.txt"), app.fingerprint(self.root / "b.txt"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
