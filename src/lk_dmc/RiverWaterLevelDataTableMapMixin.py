import matplotlib.pyplot as plt
from gig import Ent


class RiverWaterLevelDataTableMapMixin:
    def draw(self):
        ent_lk = Ent.from_id("LK")
        geo = ent_lk.geo()
        fig, ax = plt.subplots(figsize=(10, 10))
        geo.plot(ax=ax, color="lightblue", edgecolor="black")
        plt.show()
