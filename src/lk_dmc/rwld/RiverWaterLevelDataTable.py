from dataclasses import asdict, dataclass

import camelot
import pymupdf
from utils import JSONFile, Log, TimeFormat

from lk_dmc.rwld.ChartGaugingStationMixin import ChartGaugingStationMixin
from lk_dmc.rwld.ChartMapMixin import ChartMapMixin
from lk_dmc.rwld.RiverWaterLevelData import RiverWaterLevelData
from lk_dmc.rwld.RiverWaterLevelDataTableRemoteDataMixin import (
    RiverWaterLevelDataTableRemoteDataMixin,
)

log = Log("RiverWaterLevelDataTable")


@dataclass
class RiverWaterLevelDataTable(
    RiverWaterLevelDataTableRemoteDataMixin,
    ChartMapMixin,
    ChartGaugingStationMixin,
):
    d_list: list[RiverWaterLevelData]

    @property
    def time_updated_ut(self) -> int:
        return max(rwld.time_ut for rwld in self.d_list)

    @classmethod
    def from_df(cls, df, time_ut) -> "RiverWaterLevelDataTable":
        d_list = []
        current_river_basin = None

        for idx in range(2, len(df)):
            row = df.iloc[idx]
            rwld, current_river_basin = RiverWaterLevelData.from_df_row(
                row, current_river_basin, time_ut
            )
            if rwld:
                d_list.append(rwld)

        return RiverWaterLevelDataTable(d_list=d_list)

    @classmethod
    def get_date_time_from_pdf(cls, pdf_path: str):
        doc = pymupdf.open(pdf_path)
        page = doc[0]
        content = page.get_text()
        lines = content.splitlines()
        n_lines = len(lines)

        date_str = None
        time_str = None
        for i in range(n_lines - 1):
            line = lines[i].replace(" ", "")
            next_line = lines[i + 1].replace(" ", "")
            if line.startswith("DATE:"):
                date_str = next_line
            elif line.startswith("TIME:"):
                time_str = next_line

        if date_str is None or time_str is None:
            raise ValueError(f"Could not find date/time in PDF: {pdf_path}")

        date_time_str = f"{date_str} {time_str}"
        ut = TimeFormat("%d-%b-%Y %I:%M%p").parse(date_time_str).ut
        return ut

    @classmethod
    def from_pdf(cls, pdf_path: str) -> "RiverWaterLevelDataTable":
        tables = camelot.read_pdf(pdf_path)
        if len(tables) == 0:
            return None

        time_ut = cls.get_date_time_from_pdf(pdf_path)
        assert time_ut is not None, f"Could not get time from PDF: {pdf_path}"

        df = tables[0].df
        return cls.from_df(df, time_ut)

    def __len__(self):
        return len(self.d_list)

    def to_json(self, json_path: str):
        json_file = JSONFile(json_path)
        json_file.write(asdict(self))
        log.info(f"Wrote {json_file}")

    @classmethod
    def from_dict(cls, d):
        return cls(
            d_list=[RiverWaterLevelData.from_dict(d) for d in d["d_list"]]
        )

    @classmethod
    def from_json(cls, json_path: str) -> "RiverWaterLevelDataTable":
        json_file = JSONFile(json_path)
        data = json_file.read()
        return cls.from_dict(data)
