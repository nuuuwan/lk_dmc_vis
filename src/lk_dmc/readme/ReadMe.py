from utils import File, Log, Time

from lk_dmc.core import GaugingStation, RiverBasin
from lk_dmc.rwld import RiverWaterLevelDataTable

log = Log("ReadMe")


class ReadMe:
    PATH = "README.md"
    URL_IMAGE_ONLY = "https://nuuuwan.github.io/lk_dmc_vis"

    def __init__(self):
        self.latest = RiverWaterLevelDataTable.latest()
        self.map_image_path = self.latest.draw_map()
        self.station_to_latest_rwld = (
            RiverWaterLevelDataTable.get_station_name_to_latest_rwld()
        )
        self.station_to_image = RiverWaterLevelDataTable.draw_all_stations()
        self.basin_to_avg_flood_score = (
            RiverWaterLevelDataTable.get_basin_to_avg_flood_score()
        )
        self.river_to_avg_flood_score = (
            RiverWaterLevelDataTable.get_river_to_avg_flood_score()
        )

    def get_lines_header(self) -> list[str]:
        return [
            "# #SriLanka 🇱🇰 - Flood Map",
            "",
            (
                "This is a schematic diagram of river water levels"
                + " across gauging stations in Sri Lanka."
            ),
            "",
            (
                "Data from the "
                + "[Disaster Management Center]"
                + "(https://www.dmc.gov.lk/index.php)"
                + " of Sri Lanka."
            ),
            "",
            (
                "Updated whenever new information is released by the DMC,"
                + " usually every 3 hours."
            ),
            "",
            (
                "Image only link:"
                + f" [{self.URL_IMAGE_ONLY}]"
                + f"({self.URL_IMAGE_ONLY})"
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
        station_names = sorted(
            station_name_to_station.keys(),
            key=lambda station_name: self.station_to_latest_rwld[
                station_name
            ].flood_score,
            reverse=True,
        )
        for station_name in station_names:
            station = station_name_to_station[station_name]
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
        rivers = sorted(
            river_to_stations.keys(),
            key=lambda river_name: self.river_to_avg_flood_score.get(
                river_name, 0
            ),
            reverse=True,
        )
        for river_name in rivers:
            idx3 = river_to_stations[river_name]
            lines.extend(self.get_lines_for_river(river_name, idx3))

        return lines

    def get_lines_for_river_basins(self) -> list[str]:
        idx1 = GaugingStation.get_basic_to_river_to_station()
        lines = []
        for river_basin_name in self.basin_to_avg_flood_score.keys():
            idx2 = idx1[river_basin_name]
            lines.extend(
                self.get_lines_for_river_basin(river_basin_name, idx2)
            )

        return lines

    def get_lines(self) -> list[str]:
        return self.get_lines_header() + self.get_lines_for_river_basins()

    def build(self):
        lines = self.get_lines()
        File(self.PATH).write_lines(lines)
        log.info(f"Wrote {self.PATH}")
