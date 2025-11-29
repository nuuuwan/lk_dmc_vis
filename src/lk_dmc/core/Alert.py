from dataclasses import dataclass


@dataclass
class Alert:
    level: int
    name: str
    color: tuple[float, float, float]
    emoji: str

    @property
    def label(self) -> str:
        return self.name

    def __lt__(self, other) -> bool:
        assert isinstance(other, Alert)
        return self.level < other.level

    def __gt__(self, other) -> bool:
        assert isinstance(other, Alert)
        return self.level > other.level

    def __str__(self) -> str:
        return f"{self.emoji} {self.name}"


Alert.MAJOR = Alert(4, "Major Flood", (1.0, 0.0, 0.0), "🔴")
Alert.MINOR = Alert(3, "Minor Flood", (1.0, 0.5, 0.0), "🟠")
Alert.ALERT = Alert(2, "Alert", (1.0, 0.75, 0.0), "🟡")
Alert.NORMAL = Alert(1, "Normal", (0.0, 0.75, 0.0), "🟢")
Alert.NO_DATA = Alert(0, "No Data", (0.5, 0.5, 0.5), "⚪")
Alert.list_all = lambda: [
    Alert.MAJOR,
    Alert.MINOR,
    Alert.ALERT,
    Alert.NORMAL,
    Alert.NO_DATA,
]
