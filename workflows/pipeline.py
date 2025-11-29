from lk_dmc import ReadMe, RiverWaterLevelDataTable

if __name__ == "__main__":
    latest = RiverWaterLevelDataTable.latest()
    latest.draw_map()
    ReadMe().build()
