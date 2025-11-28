from lk_dmc import RiverWaterLevelDataTable

if __name__ == "__main__":
    t_list = RiverWaterLevelDataTable.list_latest()
    latest = t_list[0]
    latest.draw()
