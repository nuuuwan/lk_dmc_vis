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

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["river_name"],
            river_basin=RiverBasin.from_dict(d),
        )

    def __eq__(self, value):
        if not isinstance(value, River):
            return False
        return (
            self.name == value.name and self.river_basin == value.river_basin
        )
