from dataclasses import dataclass


@dataclass
class RiverBasin:
    code: str
    name: str

    @staticmethod
    def __validate_code__(code):
        assert code[:2] == "RB", "River Basin code must start with 'RB'"
        int_part = int(code[3:].strip())
        assert 1 <= int_part <= 200, "River Basin code must be between RB"

    @staticmethod
    def from_df_row(row) -> "RiverBasin | None":
        river_basin_str = row[0].strip()
        if not river_basin_str:
            return None
        river_basin_str = river_basin_str.replace("\n", " ").strip()
        parts = river_basin_str.split("(")
        basin_name = parts[0].strip()
        assert basin_name, "River Basin name is empty"
        basin_code = parts[1].split(")")[0].strip()
        RiverBasin.__validate_code__(basin_code)
        return RiverBasin(code=basin_code, name=basin_name)
