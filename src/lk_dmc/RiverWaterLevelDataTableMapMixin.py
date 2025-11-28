import os

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
        1: "green",
        2: "yellow",
        3: "orange",
        4: "red",
    }

    def __draw_map__(self, ax):
        district_ents = Ent.list_from_type(EntType.DISTRICT)
        for ent in district_ents:
            geo = ent.geo()
            geo.plot(
                ax=ax,
                color=(0.9, 0.9, 0.9),
                edgecolor=(0.75, 0.75, 0.75),
                linewidth=0.5,
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

                dmin = min(abs(dx), abs(dy))
                xmid = x1 + dmin * dx / abs(dx)
                ymid = y1 + dmin * dy / abs(dy)

                ax.plot(
                    [x1, xmid, x2],
                    [y1, ymid, y2],
                    color=color,
                    linewidth=2,
                    alpha=0.7,
                )

    def __draw_locations__(self, ax):
        locations = Location.list_all()
        for location in locations:
            lat, lng = location.lat_lng
            ax.plot(
                lng,
                lat,
                marker="s",
                markersize=5,
                color="grey",
            )
            ax.text(
                lng + 0.03,
                lat,
                location.name,
                fontsize=4,
                color="grey",
            )

    def __get_station_level__(self, rwld):
        station = rwld.gauging_station

        if rwld.current_water_level >= station.major_flood_level:
            return 4

        elif rwld.current_water_level >= station.minor_flood_level:
            return 3

        elif rwld.current_water_level >= station.alert_level:
            return 2

        return 1

    def __draw_station__(self, ax, rwld):
        station = rwld.gauging_station
        lat, lng = station.lat_lng
        level = self.__get_station_level__(rwld)
        color = self.LEVEL_TO_COLOR[level]

        ax.plot(
            lng,
            lat,
            marker="o",
            markersize=10,
            color=color,
        )
        ax.text(
            lng + 0.03,
            lat,
            station.name,
            fontsize=5,
            color="black",
        )

    def __draw_stations__(self, ax):
        for rwld in self.d_list:
            self.__draw_station__(ax, rwld)

    def __draw_legend__(self, ax):
        legend_handles = []
        for color, label in [
            ("red", "Major Flood"),
            ("orange", "Minor Flood"),
            ("yellow", "Alert"),
            ("green", "Normal"),
            ("grey", "Circle = Gauging Station"),
            ("grey", "Square = Other Location"),
        ]:
            if "Square" in label:
                markersize = 5
                marker_style = "s"
            else:
                markersize = 10
                marker_style = "o"
            handle = Line2D(
                [0],
                [0],
                marker=marker_style,
                color="w",
                markerfacecolor=color,
                markersize=markersize,
                label=label,
            )
            legend_handles.append(handle)

        ax.legend(handles=legend_handles, loc="upper right", fontsize=8)

    def draw(self):
        fig, ax = plt.subplots(figsize=(16, 16))

        self.__draw_map__(ax)
        self.__draw_rivers__(ax)
        self.__draw_locations__(ax)
        self.__draw_stations__(ax)

        self.__draw_legend__(ax)
        plt.title("Sri Lanka - Flood Map", fontsize=32)
        fig.text(
            0.5,
            0.1,
            "Data source: http://dmc.gov.lk",
            ha="center",
            fontsize=8,
            color="black",
            alpha=0.7,
        )
        time_str = TimeFormat.TIME.format(Time(self.time_updated_ut))
        fig.text(
            0.5,
            0.85,
            f"As of {time_str}",
            ha="center",
            fontsize=16,
            color="black",
            alpha=0.7,
        )

        ax.set_axis_off()
        for spine in ax.spines.values():
            spine.set_visible(False)

        image_path = os.path.join("images", "map.png")
        fig.savefig(image_path, dpi=300, bbox_inches="tight", pad_inches=0)
        log.info(f"Wrote {image_path}")
