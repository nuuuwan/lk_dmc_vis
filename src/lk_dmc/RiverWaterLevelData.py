from dataclasses import dataclass
from datetime import datetime

from utils import Log

from lk_dmc.GaugingStation import GaugingStation
from lk_dmc.River import River
from lk_dmc.RiverBasin import RiverBasin

log = Log("RiverWaterLevelData")


@dataclass
class RiverWaterLevelData:
    river: River
    gauging_station: GaugingStation
    time_str: str
    time_ut: int
    current_water_level_m: float
    remarks: str
    rising_or_falling: str
    rainfall_mm: float

    @classmethod
    def from_df_row(
        cls, row, river_basin: RiverBasin | None
    ) -> tuple["RiverWaterLevelData | None", RiverBasin | None]:
        river_basin = RiverBasin.from_df_row(row) or river_basin
        river = River.from_df_row(row, river_basin)
        assert river, "River could not be created from row"
        gauging_station_name = row[2].strip()
        unit = row[3].strip()
        water_level_6am = row[8].strip()
        remarks = row[9].strip()
        rising_falling = row[10].strip()
        rainfall = row[11].strip()

        if (
            not gauging_station_name
            or not river_basin
            or not water_level_6am
            or water_level_6am in ("-", "N.A.")
        ):
            return None, river_basin

        gauging_station = GaugingStation.from_df_row(row)
        current_water_level = float(water_level_6am)
        current_water_level_m = GaugingStation.convert_to_meters(
            current_water_level, unit
        )
        rainfall_mm = (
            float(rainfall)
            if rainfall and rainfall not in ("-", "N.A.")
            else 0.0
        )

        now = datetime.now()
        time_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)

        rwld = cls(
            river=river,
            gauging_station=gauging_station,
            time_str=now.strftime("%Y-%m-%d 06:00:00"),
            time_ut=int(time_6am.timestamp()),
            current_water_level_m=current_water_level_m,
            remarks=remarks,
            rising_or_falling=rising_falling,
            rainfall_mm=rainfall_mm,
        )

        return rwld, river_basin
