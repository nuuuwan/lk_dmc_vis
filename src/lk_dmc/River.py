from dataclasses import dataclass

from lk_dmc.RiverBasin import RiverBasin


@dataclass
class River:
    name: str
    river_basin: RiverBasin

    @classmethod
    def from_df_row(cls, df_row, river_basin) -> "River":
        river_name = df_row[1].strip() or df_row[0].split(")")[1].strip()
        assert river_name, "River name is empty"
        return cls(name=river_name, river_basin=river_basin)
