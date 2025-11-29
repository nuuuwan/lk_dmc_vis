from dataclasses import asdict, dataclass

import camelot
from utils import JSONFile, Log

from lk_dmc.rwld.ChartGaugingStationMixin import ChartGaugingStationMixin
from lk_dmc.rwld.ChartMapMixin import ChartMapMixin
from lk_dmc.rwld.RiverWaterLevelData import RiverWaterLevelData
from lk_dmc.rwld.RiverWaterLevelDataTableRemoteDataMixin import \
    RiverWaterLevelDataTableRemoteDataMixin

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
    def from_df(cls, df, doc_id) -> "RiverWaterLevelDataTable":
        d_list = []
        current_river_basin = None

        for idx in range(2, len(df)):
            row = df.iloc[idx]
            rwld, current_river_basin = RiverWaterLevelData.from_df_row(
                row, current_river_basin, doc_id
            )
            if rwld:
                d_list.append(rwld)

        return RiverWaterLevelDataTable(d_list=d_list)

    @classmethod
    def from_pdf(cls, pdf_path: str) -> "RiverWaterLevelDataTable":
        doc_id = pdf_path.split("/")[-1][:-4]
        assert len(doc_id) == 28, f"Unexpected doc_id length: {doc_id}"
        tables = camelot.read_pdf(pdf_path)
        if len(tables) == 0:
            return None
        df = tables[0].df
        return cls.from_df(df, doc_id)

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
