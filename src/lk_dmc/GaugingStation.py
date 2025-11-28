import os
from dataclasses import asdict, dataclass

from utils import JSONFile

from lk_dmc.River import River
from lk_dmc.WaterLevel import WaterLevel


@dataclass
class GaugingStation:
    name: str
    river: River
    alert_level: WaterLevel
    minor_flood_level: WaterLevel
    major_flood_level: WaterLevel

    @classmethod
    def from_df_row(cls, row, river) -> "GaugingStation":
        name = row[2].strip()
        unit = row[3].strip()
        alert_level = row[4].strip()
        minor_flood_level = row[5].strip()
        major_flood_level = row[6].strip()

        return cls(
            name=name,
            river=river,
            alert_level=WaterLevel.from_str(alert_level, unit),
            minor_flood_level=WaterLevel.from_str(minor_flood_level, unit),
            major_flood_level=WaterLevel.from_str(major_flood_level, unit),
        )

    @classmethod
    def __get_d_list__(cls):
        return JSONFile(
            os.path.join("data", "static", "gauging_stations.json")
        ).read()

    @classmethod
    def from_d(cls, d):
        return cls(
            name=d["name"],
            river=River.from_dict(d),
            alert_level=WaterLevel.from_str(d["alert_level"], "m"),
            minor_flood_level=WaterLevel.from_str(
                d["minor_flood_level"], "m"
            ),
            major_flood_level=WaterLevel.from_str(
                d["major_flood_level"], "m"
            ),
        )

    @classmethod
    def list_all(cls):
        d_list = cls.__get_d_list__()
        return [cls.from_d(d) for d in d_list]

    @classmethod
    def from_name(cls, name):
        gs_list = cls.list_all()
        for gs in gs_list:
            if gs.name == name:
                return gs
        raise ValueError(f"Gauging Station with name '{name}' not found")

    def __eq__(self, other):
        if not isinstance(other, GaugingStation):
            return False
        return asdict(self) == asdict(other)

    def validate(self):
        gauging_station_from_name = GaugingStation.from_name(self.name)
        assert (
            self.name == gauging_station_from_name.name
        ), f"{self.name} != {gauging_station_from_name.name}"
        assert (
            self.river == gauging_station_from_name.river
        ), f"{self.river} != {gauging_station_from_name.river}"
        assert (
            self.alert_level == gauging_station_from_name.alert_level
        ), "Alert Level does not match"
        assert (
            self.minor_flood_level
            == gauging_station_from_name.minor_flood_level
        ), "Minor Flood Level does not match"
        assert (
            self.major_flood_level
            == gauging_station_from_name.major_flood_level
        ), "Major Flood Level does not match"
