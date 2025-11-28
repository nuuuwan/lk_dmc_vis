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
    lat_lng: tuple[float, float]
    district_id: str

    @classmethod
    def from_df_row(cls, row, e_river) -> "GaugingStation":
        name = row[2].strip()
        if "(" in name:
            name = name.split("(")[0].strip()
        unit = row[3].strip()
        alert_level = row[4].strip()
        minor_flood_level = row[5].strip()
        major_flood_level = row[6].strip()

        e_alert_level = WaterLevel.from_str(alert_level, unit)
        e_minor_flood_level = WaterLevel.from_str(minor_flood_level, unit)
        e_major_flood_level = WaterLevel.from_str(major_flood_level, unit)

        gs = GaugingStation.from_name(name)
        assert gs.river == e_river, "River mismatch"
        assert gs.alert_level == e_alert_level, "Alert level mismatch"
        assert (
            gs.minor_flood_level == e_minor_flood_level
        ), "Minor flood level mismatch"
        assert (
            gs.major_flood_level == e_major_flood_level
        ), "Major flood level mismatch"
        return gs

    @classmethod
    def __get_d_list__(cls):
        return JSONFile(
            os.path.join("data", "static", "gauging_stations.json")
        ).read()

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            river=River.from_dict(d["river"]),
            alert_level=WaterLevel.from_dict(d["alert_level"]),
            minor_flood_level=WaterLevel.from_dict(d["minor_flood_level"]),
            major_flood_level=WaterLevel.from_dict(d["major_flood_level"]),
            lat_lng=tuple(d["lat_lng"]),
            district_id=d["district_id"],
        )

    @classmethod
    def list_all(cls):
        d_list = cls.__get_d_list__()
        return [cls.from_dict(d) for d in d_list]

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
