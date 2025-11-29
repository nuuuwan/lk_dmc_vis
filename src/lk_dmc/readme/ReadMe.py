from utils import File, Log

from lk_dmc.core import GaugingStation, RiverBasin
from lk_dmc.rwld import RiverWaterLevelDataTable

log = Log("ReadMe")


class ReadMe:
    PATH = "README.md"
    URL_IMAGE_ONLY = "https://nuuuwan.github.io/lk_dmc_vis"

    def __init__(self):
        self.latest = RiverWaterLevelDataTable.latest()
        self.map_image_path = self.latest.draw_map()
        self.station_to_image = RiverWaterLevelDataTable.draw_all_stations()

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

    def get_lines_for_station(self, station_name, station):
        lines = []
        image_path = self.station_to_image.get(station_name)
        lines += [
            f"#### {station.name} Gauging Station",
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
        for station_name, station in station_name_to_station.items():
            lines.extend(self.get_lines_for_station(station_name, station))

        return lines

    def get_lines_for_river_basin(self) -> list[str]:
        idx1 = GaugingStation.get_basic_to_river_to_station()
        lines = []
        for river_basin_name, idx2 in idx1.items():
            river_basin = RiverBasin.from_name(river_basin_name)
            lines.extend(
                [
                    f"## {river_basin.name} River Basin ({river_basin.code})",
                    "",
                ]
            )
            for river_name, idx3 in idx2.items():
                lines.extend(self.get_lines_for_river(river_name, idx3))

        return lines

    def get_lines(self) -> list[str]:
        return self.get_lines_header() + self.get_lines_for_river_basin()

    def build(self):
        lines = self.get_lines()
        File(self.PATH).write_lines(lines)
        log.info(f"Wrote {self.PATH}")
