from utils import File, Log

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

    def get_lines_for_gauging_stations(self) -> list[str]:
        lines = []
        for station_name, image_path in self.station_to_image.items():
            lines += [
                f"## {station_name}",
                "",
                f"![{station_name}]({image_path})",
                "",
            ]
        return lines

    def get_lines(self) -> list[str]:
        return self.get_lines_header() + self.get_lines_for_gauging_stations()

    def build(self):
        lines = self.get_lines()
        File(self.PATH).write_lines(lines)
        log.info(f"Wrote {self.PATH}")
