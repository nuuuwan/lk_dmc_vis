from dataclasses import dataclass

import camelot

from lk_dmc.RiverWaterLevelData import RiverWaterLevelData


@dataclass
class RiverWaterLevelDataTable:
    d_list: list[RiverWaterLevelData]

    @classmethod
    def from_df(cls, df) -> list["RiverWaterLevelData"]:
        d_list = []
        current_river_basin = None

        for idx in range(2, len(df)):
            row = df.iloc[idx]
            rwld, current_river_basin = RiverWaterLevelData.from_df_row(
                row, current_river_basin
            )
            if rwld:
                d_list.append(rwld)

        return RiverWaterLevelDataTable(d_list=d_list)

    @classmethod
    def from_pdf(cls, pdf_path: str) -> list["RiverWaterLevelData"]:
        tables = camelot.read_pdf(pdf_path)
        assert len(tables) > 0, f"No tables found in PDF: {pdf_path}"
        df = tables[0].df
        return cls.from_df(df)

    def __len__(self):
        return len(self.d_list)
