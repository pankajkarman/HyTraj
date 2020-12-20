import pandas as pd, numpy as np, matplotlib.pyplot as plt
import traj_dist.distance as tdist
import fastcluster as fc, scipy.cluster.hierarchy as sch

class HyHAC:
    def __init__(self, data):
        self.lat = data.sel(geo="lat").to_pandas()
        self.lon = data.sel(geo="lon").to_pandas()
        self.n_traj = len(self.lat.columns)
        self.slat = self.lat.iloc[0, 0]
        self.slon = self.lon.iloc[0, 0]

    def get_linkage(self, metric="sspd", method="ward", type_d="euclidean"):
        traj_list = []
        for traj in self.lat.columns:
            ds = pd.DataFrame([])
            ds["lat"] = self.lat[traj]
            ds["lon"] = self.lon[traj]
            traj_list.append(ds.values)
        self.p_dist = tdist.pdist(traj_list, metric=metric, type_d=type_d)
        self.link = fc.linkage(self.p_dist, method=method)
        return self

    def fit(self, nclus=5, metric='sspd', method="ward", type_d="spherical"):
        self.nclus = nclus
        self.get_linkage(metric, method, type_d)
        self.labels = sch.fcluster(self.link, self.nclus, criterion="maxclust") - 1
        self.cluster = pd.DataFrame(data=self.labels, index=self.lat.columns).T
        return self.cluster

    def plot_dendrogram(self, ax=None, p=10, D=50):
        if not ax:
            fig, ax = plt.subplots(1, 1, figsize=(14, 5))
        dn = sch.dendrogram(
            self.link,
            ax=ax,
            orientation="top",
            show_contracted=True,
            truncate_mode="lastp",
            p=p,
        )
        ax.set_ylabel("Distance")
        ax.axhline(D, color="k", ls="-.")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        return ax
