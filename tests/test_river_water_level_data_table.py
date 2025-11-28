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
        self.assertEqual(len(t), 33)

        rwld = t.d_list[0]
        self.assertEqual(
            asdict(rwld),
            {
                "river": {
                    "name": "Kelani Ganga",
                    "river_basin": {"code": "RB 01", "name": "Kelani Ganga"},
                },
                "gauging_station": {
                    "name": "Nagalagam Street",
                    "alert_level_m": 1.2192,
                    "minor_flood_level_m": 1.524,
                    "major_flood_level_m": 2.1336,
                },
                "time_str": "2025-11-28 06:00:00",
                "time_ut": 1764289800,
                "current_water_level_m": 1.6459200000000003,
                "remarks": "Minor Flood",
                "rising_or_falling": "Rising",
                "rainfall_mm": 0.0,
            },
        )
