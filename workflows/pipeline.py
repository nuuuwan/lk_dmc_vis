from lk_dmc import RiverWaterLevelDataTable

if __name__ == "__main__":
    latest = RiverWaterLevelDataTable.latest()
    latest.draw_map()
