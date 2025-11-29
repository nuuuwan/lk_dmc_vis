from dataclasses import dataclass

from lk_dmc.base.AbstractTable import AbstractTable
from lk_dmc.core.RiverBasin import RiverBasin


@dataclass
class River(AbstractTable):
    river_basin_name: str
    location_names: list[str]

    @classmethod
    def from_df_row(cls, df_row, expected_river_basin) -> "River":
        river_name = df_row[1].strip() or df_row[0].split(")")[1].strip()
        river = River.from_name(river_name)
        assert (
            river.river_basin == expected_river_basin
        ), f"{river.river_basin} != {expected_river_basin}"
        return river

    @property
    def river_basin(self):
        return RiverBasin.from_name(self.river_basin_name)

    @classmethod
    def get_basin_to_river(cls) -> dict[str, list[str]]:
        basin_to_river = {}
        rivers = cls.list_all()
        for river in rivers:
            basin_name = river.river_basin_name
            if basin_name not in basin_to_river:
                basin_to_river[basin_name] = []
            basin_to_river[basin_name].append(river.name)
        return basin_to_river
