from dataclasses import dataclass


@dataclass
class WaterLevel:

    @staticmethod
    def from_str(s, unit: str) -> float:
        if s in ["N.A.", "NA"]:
            return None
        if s in ("-"):
            return 0.0
        val = float(s)
        if unit == "ft":
            val = val * 0.3048
        return val
