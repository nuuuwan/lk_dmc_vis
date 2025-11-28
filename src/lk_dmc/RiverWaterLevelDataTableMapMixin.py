import os

import matplotlib.pyplot as plt
from gig import Ent, EntType
from utils import Log

log = Log("RiverWaterLevelDataTableMapMixin")


class RiverWaterLevelDataTableMapMixin:

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

    def __draw_station__(self, ax, rwld):
        station = rwld.gauging_station
        lat, lng = station.lat_lng
        color = "green"

        if rwld.current_water_level >= station.major_flood_level:
            color = "red"

        elif rwld.current_water_level >= station.minor_flood_level:
            color = "orange"

        elif rwld.current_water_level >= station.alert_level:
            color = "yellow"

        ax.plot(
            lng,
            lat,
            marker="o",
            markersize=5,
            color=color,
            alpha=0.7,
        )

    def __draw_stations__(self, ax):
        for rwld in self.d_list:
            self.__draw_station__(ax, rwld)

    def draw(self):
        fig, ax = plt.subplots(figsize=(9, 16))

        self.__draw_map__(ax)
        self.__draw_stations__(ax)
        ax.set_axis_off()
        for spine in ax.spines.values():
            spine.set_visible(False)

        image_path = os.path.join("images", "map.png")
        fig.savefig(image_path, dpi=300, bbox_inches="tight", pad_inches=0)
        log.info(f"Wrote {image_path}")
