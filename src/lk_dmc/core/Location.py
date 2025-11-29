from dataclasses import dataclass

from lk_dmc.base.AbstractTable import AbstractTable


@dataclass
class Location(AbstractTable):
    lat_lng: tuple[float, float]

    @property
    def url_google_maps(self) -> str:
        lat, lng = self.lat_lng
        return f"https://www.google.com/maps/place/{lat},{lng}"
