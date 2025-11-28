from dataclasses import dataclass


@dataclass
class WaterLevel:
    m: float

    @classmethod
    def from_str(cls, s, unit: str) -> "WaterLevel":
        if s in ("-", "N.A.", "NA"):
            return cls(0.0)
        val = float(s)
        if unit == "ft":
            val = val * 0.3048
        return cls(val)

    def __eq__(self, value):
        if not isinstance(value, WaterLevel):
            return False
        return abs(self.m - value.m) < 1e-6

    @classmethod
    def from_dict(cls, d):
        return cls(m=d["m"])
