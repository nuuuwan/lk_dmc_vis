import os
from datetime import datetime, timedelta, timezone

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from utils import Log

from lk_dmc.core.Alert import Alert
from lk_dmc.core.GaugingStation import GaugingStation

SL_TIMEZONE = timezone(timedelta(hours=5, minutes=30))

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
        ts = [
            datetime.fromtimestamp(d.time_ut, tz=SL_TIMEZONE)
            for d in rwld_list_recent
        ]
        levels = [d.current_water_level for d in rwld_list_recent]
        return ts, levels, rwld_list_recent

    @classmethod
    def __draw_station_annotations__(cls, station, ax):
        ax.set_title(f"{station.name} - River Water Level")

        for level, alert in [
            (station.major_flood_level, Alert.MAJOR),
            (station.minor_flood_level, Alert.MINOR),
            (station.alert_level, Alert.ALERT),
        ]:
            ax.axhline(
                y=level,
                color=alert.color,
                linestyle="--",
                linewidth=1.5,
                label=alert.label,
                alpha=0.7,
            )

        ax.legend(loc="upper left")

        return station

    @classmethod
    def __draw_latest_annotations__(cls, ts, levels, rwld_list_recent, ax):
        latest_time = ts[-1]
        latest_level = levels[-1]
        rwld = rwld_list_recent[-1]
        time_str = latest_time.strftime("%b %d, %H:%M")
        ax.annotate(
            "\n".join(
                [
                    f"{latest_level:.2f}m",
                    rwld.alert.label,
                    time_str,
                ]
            ),
            xy=(latest_time, latest_level),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(
                boxstyle="round,pad=0.5", fc=rwld.alert.color, alpha=0.7
            ),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            fontsize=9,
        )

    @classmethod
    def __draw_extrapolation__(cls, ts, levels, ax):
        last_time = ts[-1]
        last_level = levels[-1]
        min_level = min(levels)
        cutoff_time = last_time - timedelta(days=1)
        recent_indices = [i for i, t in enumerate(ts) if t >= cutoff_time]

        if len(recent_indices) < 2:
            return

        recent_ts = [ts[i] for i in recent_indices]
        recent_levels = [levels[i] for i in recent_indices]
        ts_numeric = np.array([t.timestamp() for t in recent_ts])
        levels_numeric = np.array(recent_levels)

        coeffs = np.polyfit(ts_numeric, levels_numeric, 1)
        slope = coeffs[0]

        future_time = last_time + timedelta(days=1)
        time_delta = future_time.timestamp() - last_time.timestamp()
        future_level = last_level + slope * time_delta

        extrapolate_ts = [last_time, future_time]
        extrapolate_levels = [last_level, max(min_level, future_level)]

        ax.plot(
            extrapolate_ts,
            extrapolate_levels,
            linestyle=":",
            linewidth=2,
            color="gray",
            label="Trend",
            alpha=0.7,
        )

    @classmethod
    def __draw_for_station__(cls, station_name, rwld_list):
        ts, levels, rwld_list_recent = cls.__get_data__(rwld_list)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(ts, levels, marker="o", linestyle="-")
        cls.__draw_extrapolation__(ts, levels, ax)

        ax.set_xlabel("Time (Sri Lanka)")
        ax.set_ylabel("Water Level (m)")
        ax.grid(True)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()

        station = GaugingStation.from_name(station_name)
        cls.__draw_station_annotations__(station, ax)
        cls.__draw_latest_annotations__(ts, levels, rwld_list_recent, ax)

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
