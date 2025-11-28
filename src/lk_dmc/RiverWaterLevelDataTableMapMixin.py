import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from gig import Ent, EntType
from matplotlib.lines import Line2D
from utils import Log, Time, TimeFormat

from lk_dmc.GaugingStation import GaugingStation
from lk_dmc.Location import Location
from lk_dmc.River import River

log = Log("RiverWaterLevelDataTableMapMixin")


class RiverWaterLevelDataTableMapMixin:
    LEVEL_TO_COLOR = {
        0: "grey",
        1: (0, 0.5, 0),
        2: (1, 0.75, 0),
        3: (1, 0.5, 0),
        4: (1, 0, 0),
    }

    LOCATION_MARKER_SHAPE = "s"
    LOCATION_MARKER_SIZE = 3
    STATION_MARKER_SHAPE = "o"
    STATION_MARKER_SIZE = LOCATION_MARKER_SIZE * 2
    RIVER_WIDTH = LOCATION_MARKER_SIZE // 1.5
    MIN_DISTANCE_FOR_LABEL = 0.004

    def __draw_map__(self, ax):
        district_ents = Ent.list_from_type(EntType.DISTRICT)
        for ent in district_ents:
            geo = ent.geo()
            geo.plot(
                ax=ax,
                color=(0.95, 1.0, 1.0),
                edgecolor=(0.75, 0.75, 0.75),
                linewidth=0.5,
                alpha=1.0,
            )

    def get_station_to_level_map(self):
        station_to_level = {}
        for rwld in self.d_list:
            station = rwld.gauging_station
            level = self.__get_station_level__(rwld)
            station_to_level[station.name] = level
        return station_to_level

    def __draw_rivers__(self, ax):
        rivers = River.list_all()

        for river in rivers:
            locations = [
                GaugingStation.from_name_safe(name)
                or Location.from_name(name)
                for name in river.location_names
            ]
            n_locations = len(locations)
            station_to_level = self.get_station_to_level_map()
            for i in range(n_locations - 1):
                loc1 = locations[i]
                loc2 = locations[i + 1]

                level1 = station_to_level.get(loc1.name, 0)
                level2 = station_to_level.get(loc2.name, 0)
                level_max = max(level1, level2)
                color = self.LEVEL_TO_COLOR[level_max]

                y1, x1 = loc1.lat_lng
                y2, x2 = loc2.lat_lng

                dx = x2 - x1
                dy = y2 - y1
                if i == n_locations - 2:
                    ax.text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        river.name,
                        horizontalalignment="center",
                        verticalalignment="center",
                        fontsize=self.RIVER_WIDTH * 1.5,
                        color="black",
                    )

                dmin = min(abs(dx), abs(dy))
                xmid1 = x1 + dmin * dx / abs(dx) / 2
                ymid1 = y1 + dmin * dy / abs(dy) / 2
                xmid2 = x2 - dmin * dx / abs(dx) / 2
                ymid2 = y2 - dmin * dy / abs(dy) / 2

                ax.plot(
                    [x1, xmid1, xmid2, x2],
                    [y1, ymid1, ymid2, y2],
                    color=color,
                    linewidth=self.RIVER_WIDTH,
                    alpha=0.75,
                )

    def __draw_locations__(self, ax):
        locations = Location.list_all()
        for location in locations:
            lat, lng = location.lat_lng
            ax.plot(
                lng,
                lat,
                marker=self.LOCATION_MARKER_SHAPE,
                markersize=self.LOCATION_MARKER_SIZE,
                color="grey",
            )
            ax.text(
                lng + self.LOCATION_MARKER_SIZE / 200,
                lat,
                location.name,
                horizontalalignment="left",
                verticalalignment="center",
                fontsize=self.LOCATION_MARKER_SIZE,
                color="black",
            )

    def __get_station_level__(self, rwld):
        station = rwld.gauging_station
        level = 1
        if rwld.current_water_level >= station.alert_level:
            level = 2
        if rwld.current_water_level >= station.minor_flood_level:
            level = 3
        if rwld.current_water_level >= station.major_flood_level:
            level = 4
        return level

    def __draw_station__(self, ax, rwld):
        station = rwld.gauging_station
        lat, lng = station.lat_lng
        level = self.__get_station_level__(rwld)
        color = self.LEVEL_TO_COLOR[level]

        # draw white-filled marker with colored edge (no connecting line)
        ax.plot(
            lng,
            lat,
            marker=self.STATION_MARKER_SHAPE,
            markersize=self.STATION_MARKER_SIZE,
            markerfacecolor="white",
            markeredgecolor=color,
            markeredgewidth=self.STATION_MARKER_SIZE // 3,
            linestyle="",
            zorder=5,
        )
        ax.text(
            lng + self.STATION_MARKER_SIZE / 200,
            lat,
            station.name,
            horizontalalignment="left",
            verticalalignment="center",
            fontsize=self.STATION_MARKER_SIZE,
            color="black",
        )

    def __draw_stations__(self, ax):
        for rwld in self.d_list:
            self.__draw_station__(ax, rwld)

    def __draw_legend__(self, ax):
        legend_handles = []
        for color, label in [
            (self.LEVEL_TO_COLOR[4], "Major Floods"),
            (self.LEVEL_TO_COLOR[3], "Minor Floods"),
            (self.LEVEL_TO_COLOR[2], "On Alert"),
            (self.LEVEL_TO_COLOR[1], "Normal"),
            ("grey", "Circle = Gauging Station"),
            ("grey", "Square = Other Location"),
        ]:
            if "Square" in label:
                markersize = self.LOCATION_MARKER_SIZE
                marker_style = self.LOCATION_MARKER_SHAPE
            else:
                markersize = self.STATION_MARKER_SIZE
                marker_style = self.STATION_MARKER_SHAPE
            handle = Line2D(
                [0],
                [0],
                marker=marker_style,
                color="w",
                markerfacecolor="white",
                markeredgecolor=color,
                markeredgewidth=markersize // 3,
                markersize=markersize,
                label=label,
            )
            legend_handles.append(handle)

        ax.legend(handles=legend_handles, loc="upper right", fontsize=8)

    def draw(self):
        fig, ax = plt.subplots(figsize=(16, 16))

        base = Path(__file__).resolve().parents[2]
        font_path = base / "fonts" / "Ubuntu-Regular.ttf"
        if font_path.exists():
            try:
                mpl.font_manager.fontManager.addfont(str(font_path))
                fp = mpl.font_manager.FontProperties(fname=str(font_path))
                font_name = fp.get_name()
                plt.rcParams["font.family"] = font_name
            except Exception:
                plt.rcParams["font.family"] = "DejaVu Sans"
        else:
            plt.rcParams["font.family"] = "DejaVu Sans"

        self.__draw_map__(ax)
        self.__draw_rivers__(ax)
        self.__draw_locations__(ax)
        self.__draw_stations__(ax)
        self.__draw_legend__(ax)
        fig.text(
            0.5,
            0.85,
            "Sri Lanka - Flood Map",
            fontsize=16,
            color="black",
            horizontalalignment="center",
            verticalalignment="center",
        )
        time_str = TimeFormat.TIME.format(Time(self.time_updated_ut))
        fig.text(
            0.5,
            0.825,
            f"As of {time_str}",
            fontsize=12,
            color="black",
            horizontalalignment="center",
            verticalalignment="center",
        )
        fig.text(
            0.5,
            0.8,
            "Data source: http://dmc.gov.lk",
            fontsize=8,
            color="black",
            horizontalalignment="center",
            verticalalignment="center",
        )

        ax.set_axis_off()
        for spine in ax.spines.values():
            spine.set_visible(False)

        image_path = os.path.join("images", "map.png")
        fig.set_size_inches(12, 12, forward=True)
        fig.savefig(image_path, dpi=300, bbox_inches="tight")
        log.info(f"Wrote {image_path}")
