from dataclasses import dataclass

from lk_dmc.base.AbstractTable import AbstractTable


@dataclass
class Location(AbstractTable):
    lat_lng: tuple[float, float]
