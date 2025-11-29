from dataclasses import dataclass


@dataclass
class Alert:
    level: int
    name: str
    color: tuple[float, float, float]

    @property
    def label(self) -> str:
        return self.name

    @classmethod
    def from_rwld(cls, rwld) -> "Alert":
        station = rwld.gauging_station
        if rwld.current_water_level >= station.major_flood_level:
            level = 4
        elif rwld.current_water_level >= station.minor_flood_level:
            level = 3
        elif rwld.current_water_level >= station.alert_level:
            level = 2
        else:
            level = 1

        return Alert.from_level(level)

    @classmethod
    def from_level(cls, level: int) -> "Alert":
        for alert in cls.list_all():
            if alert.level == level:
                return alert
        raise ValueError(f"No alert found for level {level}")


Alert.MAJOR = Alert(4, "Major Flood", (1.0, 0.0, 0.0))
Alert.MINOR = Alert(3, "Minor Flood", (1.0, 0.5, 0.0))
Alert.ALERT = Alert(2, "Alert", (1.0, 0.75, 0.0))
Alert.NORMAL = Alert(1, "Normal", (0.0, 0.75, 0.0))
Alert.NO_DATA = Alert(0, "No Data", (0.5, 0.5, 0.5))

Alert.list_all = lambda: [
    Alert.MAJOR,
    Alert.MINOR,
    Alert.ALERT,
    Alert.NORMAL,
    Alert.NO_DATA,
]
