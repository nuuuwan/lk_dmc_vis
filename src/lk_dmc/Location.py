from dataclasses import dataclass

from lk_dmc.AbstractTable import AbstractTable


@dataclass
class Location(AbstractTable):
    lat_lng: tuple[float, float]
    district_id: str
