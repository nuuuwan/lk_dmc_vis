import os
import unittest
from dataclasses import asdict

from lk_dmc import RiverWaterLevelDataTable


class TestCase(unittest.TestCase):
    def test_list_from_pdf(self):
        pdf_path = os.path.join(
            "tests", "inputs", "2025-11-28-15-30-water-level.pdf"
        )
        t = RiverWaterLevelDataTable.from_pdf(pdf_path)
        self.assertEqual(len(t), 39)

        rwld = t.d_list[0]
        actual_d = asdict(rwld)
        print(actual_d)
        self.assertEqual(
            actual_d,
            {
                "gauging_station_name": "Nagalagam Street",
                "time_str": "2025-11-28 15:30:00",
                "time_ut": 1764324000.0,
                "previous_water_level": 1.7373600000000002,
                "current_water_level": 1.76784,
                "remarks": "Minor Flood",
                "rising_or_falling": "Rising",
                "rainfall_mm": 0.0,
            },
        )

    def test_to_json(self):
        pdf_path = os.path.join(
            "tests", "inputs", "2025-11-28-15-30-water-level.pdf"
        )
        t = RiverWaterLevelDataTable.from_pdf(pdf_path)

        actual_json_path = os.path.join(
            "tests", "outputs", "2025-11-28-15-30-water-level.json"
        )
        expected_json_path = os.path.join(
            "tests",
            "inputs",
            "2025-11-28-15-30-water-level.json",
        )
        t.to_json(actual_json_path)

        self.assertTrue(os.path.exists(actual_json_path))
        with open(actual_json_path, "r") as actual_file:
            with open(expected_json_path, "r") as expected_file:
                actual_content = actual_file.read()
                expected_content = expected_file.read()
                self.assertEqual(actual_content, expected_content)

    def test_pipeline(self):
        latest = RiverWaterLevelDataTable.latest()
        latest.draw_map()
