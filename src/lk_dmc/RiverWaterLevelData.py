from dataclasses import dataclass
from datetime import datetime

from utils import Log

from lk_dmc.GaugingStation import GaugingStation
from lk_dmc.River import River
from lk_dmc.RiverBasin import RiverBasin
from lk_dmc.WaterLevel import WaterLevel

log = Log("RiverWaterLevelData")


@dataclass
class RiverWaterLevelData:
    river: River
    gauging_station: GaugingStation
    time_str: str
    time_ut: int
    previous_water_level: WaterLevel
    current_water_level: WaterLevel
    remarks: str
    rising_or_falling: str
    rainfall_mm: float

    @property
    def expected_remarks(self) -> str:
        if self.current_water_level.m == 0:
            return ""

        if (
            self.current_water_level.m
            >= self.gauging_station.major_flood_level.m
        ):
            return "Major Flood"
        elif (
            self.current_water_level.m
            >= self.gauging_station.minor_flood_level.m
        ):
            return "Minor Flood"
        elif self.current_water_level.m >= self.gauging_station.alert_level.m:
            return "Alert"

        else:
            return "Normal"

    def validate(self):
        assert self.river, "River is None"
        assert self.gauging_station, "Gauging Station is None"
        assert self.time_str, "Time string is empty"
        assert (
            isinstance(self.time_ut, int) and self.time_ut > 0
        ), "Invalid time_ut"
        assert self.previous_water_level, "Previous Water Level is None"
        assert self.current_water_level, "Current Water Level is None"
        assert self.remarks is not None, "Remarks is None"
        assert self.remarks == self.expected_remarks, (
            f"Remarks '{self.remarks}' do not match expected "
            f"'{self.expected_remarks}'"
        )
        assert self.rising_or_falling in (
            "Rising",
            "Falling",
            "",
        ), "Invalid rising_or_falling value"
        assert (
            isinstance(self.rainfall_mm, float) and self.rainfall_mm >= 0.0
        ), "Invalid rainfall_mm"

    @classmethod
    def from_df_row(
        cls, row, river_basin: RiverBasin | None
    ) -> tuple["RiverWaterLevelData | None", RiverBasin | None]:
        river_basin = RiverBasin.from_df_row(row) or river_basin
        river = River.from_df_row(row, river_basin)
        assert river, "River could not be created from row"

        unit = row[3].strip()
        assert unit in ("m", "ft"), f"Unknown unit: {unit}"
        remarks = row[9].strip()
        rising_falling = row[10].strip()
        rainfall = row[11].strip()

        gauging_station = GaugingStation.from_df_row(row)
        previous_water_level = WaterLevel.from_str(row[7].strip(), unit)
        current_water_level = WaterLevel.from_str(row[8].strip(), unit)
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
            previous_water_level=previous_water_level,
            current_water_level=current_water_level,
            remarks=remarks,
            rising_or_falling=rising_falling,
            rainfall_mm=rainfall_mm,
        )
        rwld.validate()

        return rwld, river_basin

    def to_dict_flat(self) -> dict:
        return dict(
            river_basin_name=self.river.river_basin.name,
            river_basin_code=self.river.river_basin.code,
            river_name=self.river.name,
            gauging_station_name=self.gauging_station.name,
            alert_level_m=self.gauging_station.alert_level.m,
            minor_flood_level_m=self.gauging_station.minor_flood_level.m,
            major_flood_level_m=self.gauging_station.major_flood_level.m,
            time_str=self.time_str,
            time_ut=self.time_ut,
            previous_water_level_m=self.previous_water_level.m,
            current_water_level_m=self.current_water_level.m,
            remarks=self.remarks,
            rising_or_falling=self.rising_or_falling,
            rainfall_mm=self.rainfall_mm,
        )
