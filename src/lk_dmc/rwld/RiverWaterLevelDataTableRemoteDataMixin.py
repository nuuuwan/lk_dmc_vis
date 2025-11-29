import os
from functools import cache

import requests
from utils import Log, TSVFile

from lk_dmc.core.GaugingStation import GaugingStation
from lk_dmc.core.River import River
from lk_dmc.rwld.RiverWaterLevelData import RiverWaterLevelData

log = Log("RiverWaterLevelDataTableRemoteDataMixin")


class RiverWaterLevelDataTableRemoteDataMixin:
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
            d for d in d_list if "water level" in d["description"].lower()
        ]

        url_pdf_list = []
        for d in d_list_with_water_level:
            date_str = d["date_str"]
            year = date_str[:4]
            decade = year[:3] + "0s"
            doc_id = d["doc_id"]

            url_pdf = url_base + f"/{decade}/{year}/{doc_id}/doc.pdf"
            url_pdf_list.append(url_pdf)
        log.info(f"Found {len(url_pdf_list)} water level PDF URLs")
        return url_pdf_list

    @classmethod
    def from_url_pdf(cls, url_pdf):
        parts = url_pdf.split("/")
        assert parts[-1] == "doc.pdf", f"Invalid PDF URL: {url_pdf}"
        doc_id = parts[-2]

        json_path = os.path.join("data", "jsons", f"{doc_id}.json")
        if os.path.exists(json_path):
            return cls.from_json(json_path)

        pdf_path = os.path.join("data", "pdfs", f"{doc_id}.pdf")
        if not os.path.exists(pdf_path):
            try:
                response = requests.get(url_pdf, timeout=30)
                response.raise_for_status()
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                log.info(f"Downloaded {url_pdf} to {pdf_path}")
            except Exception as e:
                log.error(f"Failed to download {url_pdf}: {e}")
                return None

        else:
            log.debug(f"{pdf_path} Exists.")

        rwld = cls.from_pdf(pdf_path)
        if not rwld:
            return None
        rwld.to_json(json_path)
        return rwld

    @classmethod
    @cache
    def list_latest(cls):
        url_pdf_list = cls.get_latest_url_pdf_list()
        rwld_table_list = []
        for url_pdf in url_pdf_list:
            rwld_table = cls.from_url_pdf(url_pdf)
            if rwld_table:
                rwld_table_list.append(rwld_table)
        return rwld_table_list

    @classmethod
    def get_station_name_to_rwld_list(
        cls,
    ) -> dict[str, list[RiverWaterLevelData]]:
        rwld_table_list = cls.list_latest()
        idx = {}
        for rwld_table in rwld_table_list:
            for rwld in rwld_table.d_list:
                if rwld.current_water_level is None:
                    continue
                station_name = rwld.gauging_station_name
                if station_name not in idx:
                    idx[station_name] = []
                idx[station_name].append(rwld)

        for station_name in idx.keys():
            idx[station_name].sort(key=lambda x: x.time_ut)
        return idx

    @classmethod
    def get_station_to_level_velocity(cls):
        idx = cls.get_station_name_to_rwld_list()
        station_name_to_level_velocity = {}
        for station_name, rwld_list in idx.items():
            if len(rwld_list) < 2:
                continue
            rwld_latest = rwld_list[-1]
            rwld_second_latest = rwld_list[-2]
            dlevel = (
                rwld_latest.current_water_level
                - rwld_second_latest.current_water_level
            )
            dt = rwld_latest.time_ut - rwld_second_latest.time_ut
            level_velocity_mph = dlevel / dt * 3600
            station_name_to_level_velocity[station_name] = level_velocity_mph
        return station_name_to_level_velocity

    @classmethod
    def get_station_name_to_latest_rwld(
        cls,
    ) -> dict[str, RiverWaterLevelData]:
        idx = cls.get_station_name_to_rwld_list()
        for station_name, rwld_list in idx.items():
            rwld_list.sort(key=lambda x: x.time_ut, reverse=True)
            idx[station_name] = rwld_list[0]
        return idx

    @classmethod
    def latest(cls):
        idx = cls.get_station_name_to_latest_rwld()
        latest_rwld_table = cls(d_list=list(idx.values()))
        return latest_rwld_table

    @classmethod
    def get_river_to_avg_flood_score(cls) -> dict[str, float]:
        river_to_stations = GaugingStation.get_river_to_stations()
        station_to_rwld = cls.get_station_name_to_latest_rwld()
        idx = {}
        for river, stations in river_to_stations.items():
            rwlds = [station_to_rwld[station] for station in stations]
            flood_scores = [rwld.flood_score for rwld in rwlds]
            avg_level = sum(flood_scores) / len(flood_scores)
            idx[river] = avg_level

        idx = dict(
            sorted(
                idx.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )
        return idx

    @classmethod
    def get_basin_to_avg_flood_score(cls) -> dict[str, float]:
        basin_to_river = River.get_basin_to_river()
        river_to_avg_flood_score = cls.get_river_to_avg_flood_score()

        idx = {}
        for basin, rivers in basin_to_river.items():
            flood_scores = [
                river_to_avg_flood_score[river] for river in rivers
            ]
            idx[basin] = sum(flood_scores) / len(flood_scores)

        idx = dict(
            sorted(
                idx.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )
        return idx

    @classmethod
    def get_sorted_basin_to_river_to_stations(cls):
        basin_to_river_to_stations = (
            GaugingStation.get_basic_to_river_to_station()
        )
        basin_to_avg_flood_score = cls.get_basin_to_avg_flood_score()
        river_to_avg_flood_score = cls.get_river_to_avg_flood_score()
        station_name_to_latest_rwld = cls.get_station_name_to_latest_rwld()
        idx = {}
        for basin, river_to_stations in basin_to_river_to_stations.items():
            for river, station_name_to_station in river_to_stations.items():
                basin_to_river_to_stations[basin][river] = dict(
                    sorted(
                        station_name_to_station.items(),
                        key=lambda item: station_name_to_latest_rwld[
                            item[0]
                        ].flood_score,
                        reverse=True,
                    )
                )
            idx[basin] = dict(
                sorted(
                    basin_to_river_to_stations[basin].items(),
                    key=lambda x: river_to_avg_flood_score.get(x[0], 0),
                    reverse=True,
                )
            )
        idx = dict(
            sorted(
                idx.items(),
                key=lambda x: basin_to_avg_flood_score.get(x[0], 0),
                reverse=True,
            )
        )
        return idx
