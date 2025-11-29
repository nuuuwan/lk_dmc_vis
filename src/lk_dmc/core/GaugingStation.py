from dataclasses import dataclass

from lk_dmc.base.AbstractTable import AbstractTable
from lk_dmc.core.Location import Location
from lk_dmc.core.River import River
from lk_dmc.core.WaterLevel import WaterLevel


@dataclass
class GaugingStation(Location, AbstractTable):
    river_name: str
    alert_level: float
    minor_flood_level: float
    major_flood_level: float
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
    def get_basic_to_river_to_station(
        cls,
    ) -> dict[str, dict[str, "GaugingStation"]]:
        idx: dict[str, dict[str, GaugingStation]] = {}
        for station in cls.list_all():
            river = station.river
            river_basin = river.river_basin
            if river_basin.name not in idx:
                idx[river_basin.name] = {}
            if river.name not in idx[river_basin.name]:
                idx[river_basin.name][river.name] = {}
            idx[river_basin.name][river.name][station.name] = station
        return idx

    @classmethod
    def get_river_to_stations(
        cls,
    ) -> dict[str, list[str]]:
        idx: dict[str, list[GaugingStation]] = {}
        for station in cls.list_all():
            river = station.river
            if river.name not in idx:
                idx[river.name] = []
            idx[river.name].append(station.name)
        return idx
