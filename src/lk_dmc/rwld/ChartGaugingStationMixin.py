import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from utils import Log

from lk_dmc.core.GaugingStation import GaugingStation

log = Log("ChartGaugingStationMixin")


class ChartGaugingStationMixin:

    TIME_WINDOW_DAYS = 7
    DIR_IMAGES_STATIONS = os.path.join("images", "stations")

    @classmethod
    def __get_data__(cls, rwld_list):
        min_time_ut = rwld_list[0].time_ut - cls.TIME_WINDOW_DAYS * 86_000
        rwld_list_recent = [
            rwld for rwld in rwld_list if rwld.time_ut > min_time_ut
        ]
        ts = [datetime.fromtimestamp(d.time_ut) for d in rwld_list_recent]
        levels = [d.current_water_level for d in rwld_list_recent]
        return ts, levels

    @classmethod
    def __draw_station_annotations__(cls, station, ax):
        ax.set_title(f"{station.name} - River Water Level")

        flood_levels = [
            (station.major_flood_level, "red", "Major Flood"),
            (station.minor_flood_level, "darkorange", "Minor Flood"),
            (station.alert_level, "orange", "Alert"),
        ]

        for level, color, label in flood_levels:
            ax.axhline(
                y=level,
                color=color,
                linestyle="--",
                linewidth=1.5,
                label=label,
                alpha=0.7,
            )

        ax.legend(loc="upper left")

        return station

    @classmethod
    def __draw_for_station__(cls, station_name, rwld_list):
        ts, levels = cls.__get_data__(rwld_list)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(ts, levels, marker="o", linestyle="-")

        ax.set_xlabel("Time")
        ax.set_ylabel("Water Level (m)")
        ax.grid(True)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()

        station = GaugingStation.from_name(station_name)
        cls.__draw_station_annotations__(station, ax)

        os.makedirs(cls.DIR_IMAGES_STATIONS, exist_ok=True)
        image_path = os.path.join(
            cls.DIR_IMAGES_STATIONS, f"{station.file_prefix}.png"
        )
        fig.savefig(image_path, dpi=300, bbox_inches="tight")
        log.info(f"Wrote {image_path}")
        plt.close(fig)
        return image_path

    @classmethod
    def draw_all_stations(cls) -> dict[str, str]:
        idx = cls.get_station_name_to_rwld_list()
        station_to_image = {}
        for station_name, rwld_list in idx.items():
            image_path = cls.__draw_for_station__(station_name, rwld_list)
            station_to_image[station_name] = image_path
        return station_to_image
