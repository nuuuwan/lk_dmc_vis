from dataclasses import dataclass

from lk_dmc.WaterLevel import WaterLevel


@dataclass
class GaugingStation:
    name: str
    alert_level: WaterLevel
    minor_flood_level: WaterLevel
    major_flood_level: WaterLevel

    @classmethod
    def from_df_row(cls, row) -> "GaugingStation":
        name = row[2].strip()
        unit = row[3].strip()
        alert_level = row[4].strip()
        minor_flood_level = row[5].strip()
        major_flood_level = row[6].strip()

        return cls(
            name=name,
            alert_level=WaterLevel.from_str(alert_level, unit),
            minor_flood_level=WaterLevel.from_str(minor_flood_level, unit),
            major_flood_level=WaterLevel.from_str(major_flood_level, unit),
        )
