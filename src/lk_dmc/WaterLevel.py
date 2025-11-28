from dataclasses import dataclass


@dataclass
class WaterLevel:
    m: float

    @classmethod
    def from_str(cls, s, unit: str) -> "WaterLevel":
        if s in ("-", "N.A."):
            return cls(0.0)
        val = float(s)
        if unit == "ft":
            val = val * 0.3048
        return cls(val)
