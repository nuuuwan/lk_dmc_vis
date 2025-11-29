from dataclasses import dataclass

from utils import Log, Time, TimeFormat

from lk_dmc.core.Alert import Alert
from lk_dmc.core.GaugingStation import GaugingStation
from lk_dmc.core.River import River
from lk_dmc.core.RiverBasin import RiverBasin
from lk_dmc.core.WaterLevel import WaterLevel

log = Log("RiverWaterLevelData")


@dataclass
class RiverWaterLevelData:
    gauging_station_name: str
    time_str: str
    time_ut: int
    previous_water_level: float
    current_water_level: float
    remarks: str
    rising_or_falling: str
    rainfall_mm: float

    @property
    def gauging_station(self) -> GaugingStation:
        return GaugingStation.from_name(self.gauging_station_name)

    @property
    def flood_score(self) -> float:
        # Intepretation
        # > 1 Major
        # 0-1 Minor
        # < 0 Normal
        station = self.gauging_station
        major = station.major_flood_level
        minor = station.minor_flood_level
        current = self.current_water_level
        flood_score = (current - minor) / (major - minor)
        return flood_score

    @property
    def alert(self) -> Alert:  # noqa: CFQ004
        station = self.gauging_station
        if self.current_water_level >= station.major_flood_level:
            return Alert.MAJOR
        elif self.current_water_level >= station.minor_flood_level:
            return Alert.MINOR
        elif self.current_water_level >= station.alert_level:
            return Alert.ALERT
        else:
            return Alert.NORMAL

    @classmethod
    def from_df_row(
        cls, row, current_river_basin: RiverBasin, time_ut: str
    ) -> tuple["RiverWaterLevelData", str]:
        river_basin = RiverBasin.from_df_row(row) or current_river_basin
        river = River.from_df_row(row, river_basin)
        assert river, "River could not be created from row"

        unit = row[3].strip()
        assert unit in ("m", "ft"), f"Unknown unit: {unit}"
        remarks = row[9].strip()
        rising_falling = row[10].strip()
        rainfall = row[11].strip()

        gauging_station = GaugingStation.from_df_row(row, river, river_basin)
        previous_water_level = WaterLevel.from_str(row[7].strip(), unit)
        current_water_level = WaterLevel.from_str(row[8].strip(), unit)
        rainfall_mm = (
            float(rainfall)
            if rainfall and rainfall not in ("-", "N.A.")
            else 0.0
        )

        time_str = TimeFormat("%Y-%m-%d %H:%M:%S").format(Time(time_ut))

        rwld = cls(
            gauging_station_name=gauging_station.name,
            time_str=time_str,
            time_ut=time_ut,
            previous_water_level=previous_water_level,
            current_water_level=current_water_level,
            remarks=remarks,
            rising_or_falling=rising_falling,
            rainfall_mm=rainfall_mm,
        )

        return rwld, river_basin

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
