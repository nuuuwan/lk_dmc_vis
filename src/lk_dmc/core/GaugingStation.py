from dataclasses import asdict, dataclass

from lk_dmc.base.AbstractTable import AbstractTable
from lk_dmc.core.River import River
from lk_dmc.core.WaterLevel import WaterLevel


@dataclass
class GaugingStation(AbstractTable):
    river_name: str
    alert_level: float
    minor_flood_level: float
    major_flood_level: float
    lat_lng: tuple[float, float]
    district_id: str

    @property
    def river(self):
        return River.from_name(self.river_name)

    @classmethod
    def from_df_row(
        cls, row, expected_river, expected_river_basin
    ) -> "GaugingStation":
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
        assert gs.river == expected_river, f'"{gs}" != "{expected_river}"'
        assert (
            gs.name in gs.river.location_names
        ), f'"{gs.name}" not in "{gs.river.location_names}"'
        assert (
            gs.river.river_basin == expected_river_basin
        ), f'"{gs.river.river_basin}" != "{expected_river_basin}"'
        assert (
            gs.alert_level == e_alert_level
        ), f'alert_level: "{gs.alert_level}" != "{e_alert_level}"'
        assert gs.minor_flood_level == e_minor_flood_level, (
            "minor_flood_level:"
            + f' "{gs.minor_flood_level}" != "{e_minor_flood_level}"'
        )
        assert gs.major_flood_level == e_major_flood_level, (
            "major_flood_level:"
            + f' "{gs.major_flood_level}" != "{e_major_flood_level}"'
        )
        return gs

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
