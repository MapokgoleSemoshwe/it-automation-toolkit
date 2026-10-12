"""
tests/test_capstone.py
------------------------
Unit tests for the capstone backend modules: FileManager, LogAnalyser,
SystemMonitor, DataValidator. Run from the project root:

    python -m unittest discover tests -v
"""

import unittest
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.file_manager import FileManager, CATEGORY_MAP
from src.log_analyser import LogAnalyser
from src.system_monitor import SystemMonitor
from src.data_validator import DataValidator


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        open(os.path.join(self.temp_dir, "notes.txt"), "w").close()
        open(os.path.join(self.temp_dir, "photo.jpg"), "w").close()
        self.fm = FileManager(log_dir=tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dry_run_does_not_move_files(self):
        self.fm.organize(self.temp_dir, dry_run=True)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "notes.txt")))

    def test_real_run_sorts_into_category_folders(self):
        result = self.fm.organize(self.temp_dir, dry_run=False)
        self.assertEqual(result["moved"], 2)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "Documents", "notes.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "Images", "photo.jpg")))

    def test_category_map_known_types(self):
        self.assertEqual(CATEGORY_MAP[".py"], "Scripts")


class TestLogAnalyser(unittest.TestCase):
    def setUp(self):
        self.temp_log = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
        self.temp_log.write(
            "2026-09-14 ERROR Failed login from 10.0.0.5\n"
            "2026-09-15 ERROR Failed login from 10.0.0.5\n"
            "2026-09-15 WARNING disk low\n"
        )
        self.temp_log.close()
        self.la = LogAnalyser()

    def tearDown(self):
        os.remove(self.temp_log.name)

    def test_finds_ips(self):
        results = self.la.analyze(self.temp_log.name)
        self.assertIn("10.0.0.5", results["unique_ips"])

    def test_counts_severity(self):
        results = self.la.analyze(self.temp_log.name)
        self.assertEqual(results["severity_counts"]["ERROR"], 2)
        self.assertEqual(results["severity_counts"]["WARNING"], 1)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.la.analyze("does_not_exist.log")


class TestSystemMonitor(unittest.TestCase):
    def test_disk_check_returns_valid_structure(self):
        sm = SystemMonitor(threshold=80)
        result = sm.check_disk("/")
        self.assertIn("status", result)
        self.assertIn(result["status"], ("OK", "WARNING") or "Error" in result["status"])

    def test_check_all_returns_three_checks(self):
        sm = SystemMonitor(threshold=80)
        results = sm.check_all()
        self.assertEqual(len(results), 3)


class TestDataValidator(unittest.TestCase):
    def setUp(self):
        self.temp_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
        self.temp_csv.write("name,email\nAlice,alice@x.com\nBob,\nAlice,alice@x.com\n")
        self.temp_csv.close()
        self.dv = DataValidator()

    def tearDown(self):
        os.remove(self.temp_csv.name)

    def test_flags_missing_field(self):
        results = self.dv.validate_csv(self.temp_csv.name)
        self.assertEqual(len(results["invalid_rows"]), 1)

    def test_flags_duplicate(self):
        results = self.dv.validate_csv(self.temp_csv.name)
        self.assertEqual(len(results["duplicate_rows"]), 1)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.dv.validate_csv("nope.csv")

    def test_missing_required_column_raises(self):
        bad_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
        bad_csv.write("name\nAlice\n")
        bad_csv.close()
        with self.assertRaises(ValueError):
            self.dv.validate_csv(bad_csv.name)
        os.remove(bad_csv.name)


if __name__ == "__main__":
    unittest.main()
