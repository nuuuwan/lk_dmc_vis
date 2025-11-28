import os
import unittest
from dataclasses import asdict

from lk_dmc import RiverWaterLevelDataTable


class TestCase(unittest.TestCase):
    def test_list_from_pdf(self):
        pdf_path = os.path.join(
            "tests", "inputs", "test_river_water_level_data_table.pdf"
        )
        t = RiverWaterLevelDataTable.from_pdf(pdf_path)
        self.assertEqual(len(t), 39)

        rwld = t.d_list[0]
        actual_d = asdict(rwld)
        print(actual_d)
        self.assertEqual(
            actual_d,
            {
                "gauging_station": {
                    "name": "Nagalagam Street",
                    "river": {
                        "name": "Kelani Ganga",
                        "river_basin": {
                            "code": "RB 01",
                            "name": "Kelani Ganga",
                        },
                    },
                    "alert_level": {"m": 1.2192},
                    "minor_flood_level": {"m": 1.524},
                    "major_flood_level": {"m": 2.1336},
                },
                "time_str": "2025-11-28 06:00:00",
                "time_ut": 1764289800,
                "previous_water_level": {"m": 1.61544},
                "current_water_level": {"m": 1.6459200000000003},
                "remarks": "Minor Flood",
                "rising_or_falling": "Rising",
                "rainfall_mm": 0.0,
            },
        )

    def test_to_json(self):
        pdf_path = os.path.join(
            "tests", "inputs", "test_river_water_level_data_table.pdf"
        )
        t = RiverWaterLevelDataTable.from_pdf(pdf_path)

        actual_json_path = os.path.join(
            "tests", "outputs", "test_river_water_level_data_table.json"
        )
        expected_json_path = os.path.join(
            "tests",
            "inputs",
            "test_river_water_level_data_table.json",
        )
        t.to_json(actual_json_path)

        self.assertTrue(os.path.exists(actual_json_path))
        with open(actual_json_path, "r") as actual_file:
            with open(expected_json_path, "r") as expected_file:
                actual_content = actual_file.read()
                expected_content = expected_file.read()
                self.assertEqual(actual_content, expected_content)

    @unittest.skip("slow")
    def test_list_latest(self):
        t_list = RiverWaterLevelDataTable.list_latest()
        self.assertGreaterEqual(len(t_list), 1)
