from utils import File, Log, Time

from lk_dmc.core import GaugingStation, RiverBasin
from lk_dmc.rwld import RiverWaterLevelDataTable

log = Log("ReadMe")


class ReadMe:
    PATH = "README.md"
    URL_IMAGE_ONLY = "https://nuuuwan.github.io/lk_dmc_vis"
    URL_DETAILS = "https://github.com/nuuuwan/lk_dmc_vis/blob/main/README.md"
    URL_SOURCE = "https://www.dmc.gov.lk"
    URL_REPO_IRRIGATION = "https://github.com/nuuuwan/lk_irrigation"
    URL_REPO_THIS = "https://github.com/nuuuwan/lk_dmc_vis"

    def __init__(self):
        self.latest = RiverWaterLevelDataTable.latest()
        self.map_image_path = self.latest.draw_map()
        self.station_to_image = RiverWaterLevelDataTable.draw_all_stations()
        self.station_to_latest_rwld = (
            RiverWaterLevelDataTable.get_station_name_to_latest_rwld()
        )

        self.basin_to_river_to_stations = (
            RiverWaterLevelDataTable.get_sorted_basin_to_river_to_stations()
        )
        self.station_to_level_velocity = (
            RiverWaterLevelDataTable.get_station_to_level_velocity()
        )

    def get_lines_header(self) -> list[str]:
        return [
            "# #SriLanka 🇱🇰 - Flood Map",
            "",
            (
                "Infographics, Charts and Data of **River Water Levels**"
                + " across Sri Lanka."
            ),
            "",
            (
                "[Data](data) from the "
                + "[Disaster Management Center]"
                + f"({self.URL_SOURCE})"
                + " of Sri Lanka."
            ),
            "",
            (
                "Updated whenever new information is released by the DMC,"
                + " usually every **3 hours**."
            ),
            "",
            (
                "High-Resolution Map Image:"
                + f" [{self.URL_IMAGE_ONLY}]"
                + f"({self.URL_IMAGE_ONLY})"
            ),
            "",
            (
                "Detailed Analysis and Projections:"
                + f" [{self.URL_DETAILS}]"
                + f"({self.URL_DETAILS})"
            ),
            "",
            f"![Map]({self.map_image_path})",
            "",
        ]

    def get_lines_for_station(self, station):
        station_name = station.name
        rwld = self.station_to_latest_rwld[station_name]
        dt_last_updated = Time.now().ut - rwld.time_ut
        dt_last_updated_hours = dt_last_updated // 3600
        emoji_late = "⌛" if dt_last_updated_hours >= 24 else ""
        alert = rwld.alert
        lines = []
        image_path = self.station_to_image.get(station_name)
        lines += [
            f"#### {alert}"
            + f" - [{station.name}]({station.url_google_maps})"
            + " Gauging Station",
            "",
            "*Last Updated"
            + f" **{dt_last_updated_hours:.0f} hours** ago*"
            + f" {emoji_late}",
            "",
            f"![{station.name}]({image_path})",
            "",
        ]
        return lines

    def get_lines_for_river(
        self, river_name, station_name_to_station
    ) -> list[str]:
        lines = []
        lines.extend(
            [
                f"### {river_name}",
                "",
            ]
        )
        for station in station_name_to_station.values():
            lines.extend(self.get_lines_for_station(station))

        return lines

    def get_lines_for_river_basin(
        self, river_basin_name, river_to_stations
    ) -> list[str]:
        lines = []
        river_basin = RiverBasin.from_name(river_basin_name)
        lines.extend(
            [
                f"## {river_basin.name} River Basin ({river_basin.code})",
                "",
            ]
        )
        for river_name, station_name_to_station in river_to_stations.items():
            lines.extend(
                self.get_lines_for_river(river_name, station_name_to_station)
            )

        return lines

    def get_lines_for_river_basins(self) -> list[str]:
        lines = []
        for (
            river_basin_name,
            river_to_stations,
        ) in self.basin_to_river_to_stations.items():
            lines.extend(
                self.get_lines_for_river_basin(
                    river_basin_name, river_to_stations
                )
            )

        return lines

    def get_lines_for_summary_table(self) -> list[str]:
        lines = ["## Summary Table", ""]
        lines.extend(
            [
                (
                    "| Gauging Station | River | River Basin "
                    "| Level (m) | Rate-of-Rise (m/hr) | Alert |"
                ),
                (
                    "|-----------------|-------|-------------|"
                    "----------:|--------------------:|-------|"
                ),
            ]
        )
        for (
            station_name,
            rwld,
        ) in self.station_to_latest_rwld.items():
            level_velocity = self.station_to_level_velocity[station_name]
            station = GaugingStation.from_name(station_name)
            river = station.river
            basin = river.river_basin

            river_name = river.name
            basin_name = basin.name

            velocity_emoji = ""
            if level_velocity >= 0.01:
                velocity_emoji = "🔺"

            velocity_str = f"{velocity_emoji}{level_velocity:.2f}"
            lines.extend(
                [
                    f"| [{station_name}]({station.url_google_maps}) "
                    + f"| {river_name} "
                    + f"| {basin_name} "
                    + f"| {rwld.current_water_level:.1f} "
                    + f"| {velocity_str} "
                    + f"| {rwld.alert} |",
                ]
            )
        lines.append("")
        return lines

    def get_lines_notice_on_lk_irrigation(self) -> list[str]:
        return [
            "## 🚨 IMPORTANT-NOTICE: Higher-Frequency River Level Data 🆕"
            + " from the Irrigation Department",
            "",
            "The Disaster Management Centre of Sri Lanka receives its river"
            + " water level data from the Hydrology and Disaster Management"
            + " Division of the Irrigation Department.",
            "",
            "The Irrigation Department publishes the same measurements,"
            + " but at a much higher frequency."
            + " If you are doing analysis or building tools",
            "related to water levels or flooding, the Department’s dataset",
            "is the better choice.",
            "",
            "I am collecting the Irrigation Department data here:",
            f"[{self.URL_REPO_IRRIGATION}]({self.URL_REPO_IRRIGATION})",
            "",
            "I will continue maintaining this repo (",
            f"[{self.URL_REPO_THIS}]({self.URL_REPO_THIS})",
            " since many users are already using it.",
            "However, if you need higher-resolution measurements,"
            + " I recommend using ",
            f"[lk_irrigation]({self.URL_REPO_IRRIGATION})",
            "",
        ]

    def get_lines(self) -> list[str]:
        return (
            self.get_lines_header()
            + self.get_lines_notice_on_lk_irrigation()
            + self.get_lines_for_summary_table()
            + self.get_lines_for_river_basins()
        )

    def build(self):
        lines = self.get_lines()
        File(self.PATH).write_lines(lines)
        log.info(f"Wrote {self.PATH}")
