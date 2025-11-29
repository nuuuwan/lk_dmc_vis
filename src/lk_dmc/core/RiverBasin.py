import re
from dataclasses import dataclass

from lk_dmc.base.AbstractTable import AbstractTable


@dataclass
class RiverBasin(AbstractTable):
    code: str

    @staticmethod
    def __parse_name__(river_basin_str: str) -> str:
        river_basin_str = river_basin_str.replace("\n", " ").strip()
        parts = river_basin_str.split("(")
        basin_name = parts[0].strip()
        assert basin_name, "River Basin name is empty"
        return basin_name

    @staticmethod
    def __parse_code__(river_basin_str: str) -> str:
        parts = river_basin_str.split("(")
        basin_code = parts[1].split(")")[0].strip()
        basin_code = re.sub(r"\s+", " ", basin_code)
        return basin_code

    @staticmethod
    def from_df_row(row) -> "RiverBasin | None":
        river_basin_str = row[0].strip()
        if not river_basin_str:
            return None
        name = RiverBasin.__parse_name__(river_basin_str)
        code = RiverBasin.__parse_code__(river_basin_str)

        river_basin = RiverBasin.from_name(name)
        assert river_basin.name == name, "River Basin name mismatch"
        assert river_basin.code == code, "River Basin code mismatch"
        return river_basin
