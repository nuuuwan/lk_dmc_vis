import os
from dataclasses import dataclass

import camelot
import pandas as pd
import requests
from utils import Log, TSVFile

from lk_dmc.RiverWaterLevelData import RiverWaterLevelData

log = Log("RiverWaterLevelDataTable")


@dataclass
class RiverWaterLevelDataTable:
    d_list: list[RiverWaterLevelData]

    @classmethod
    def from_df(cls, df) -> "RiverWaterLevelDataTable":
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
    def from_pdf(cls, pdf_path: str) -> "RiverWaterLevelDataTable":
        tables = camelot.read_pdf(pdf_path)
        assert len(tables) > 0, f"No tables found in PDF: {pdf_path}"
        df = tables[0].df
        return cls.from_df(df)

    def __len__(self):
        return len(self.d_list)

    def to_csv(self, csv_path: str):

        data = []
        for rwld in self.d_list:
            data.append(rwld.to_dict_flat())
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)

    @classmethod
    def get_latest_url_pdf_list(cls) -> list[str]:
        url_base = (
            "https://raw.githubusercontent.com"
            + "/nuuuwan/lk_dmc/refs/heads"
            + "/data_lk_dmc_river_water_level_and_flood_warnings"
            + "/data/lk_dmc_river_water_level_and_flood_warnings"
        )
        remote_url = url_base + "/docs_last100.tsv"
        tsv_path = os.path.join("data", "docs_last100.tsv")

        response = requests.get(remote_url, timeout=30)
        response.raise_for_status()
        with open(tsv_path, "wb") as f:
            f.write(response.content)

        d_list = TSVFile(tsv_path).read()
        d_list_with_water_level = [
            d for d in d_list if d["description"] == "Water Level"
        ]

        url_pdf_list = []
        for d in d_list_with_water_level:
            date_str = d["date_str"]
            num = d["num"]
            year = date_str[:4]
            decade = year[:3] + "0s"
            url_pdf = url_base + f"/{decade}/{year}/{date_str}-{num}/doc.pdf"
            url_pdf_list.append(url_pdf)
        log.info(f"Found {len(url_pdf_list)} water level PDF URLs")
        return url_pdf_list

    @classmethod
    def from_url_pdf(cls, url_pdf) -> "RiverWaterLevelDataTable":
        parts = url_pdf.split("/")
        assert parts[-1] == "doc.pdf", f"Invalid PDF URL: {url_pdf}"
        doc_id = parts[-2]
        pdf_path = os.path.join("data", "pdfs", f"{doc_id}.pdf")
        if not os.path.exists(pdf_path):
            response = requests.get(url_pdf, timeout=30)
            response.raise_for_status()
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            log.info(f"Downloaded {url_pdf} to {pdf_path}")

        else:
            log.debug(f"{pdf_path} Exists.")
        return cls.from_pdf(pdf_path)

    @classmethod
    def list_latest(cls):
        url_pdf_list = cls.get_latest_url_pdf_list()
        rwld_table_list = []
        for url_pdf in url_pdf_list:
            rwld_table = cls.from_url_pdf(url_pdf)
            rwld_table_list.append(rwld_table)
        latest = rwld_table_list[-1]
        latest.to_csv(os.path.join("data", "latest.csv"))
        return rwld_table_list
