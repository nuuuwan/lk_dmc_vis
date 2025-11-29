from utils import File, Log

log = Log("ReadMe")


class ReadMe:
    PATH = "README.md"

    def get_lines(self) -> list[str]:
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
                + " [https://nuuuwan.github.io/lk_dmc_vis]"
                + "(https://nuuuwan.github.io/lk_dmc_vis/)"
            ),
            "",
            "![images/map.png](images/map.png)",
            "",
        ]

    def build(self):
        lines = self.get_lines()
        File(self.PATH).write_lines(lines)
        log.info(f"Wrote {self.PATH}")
