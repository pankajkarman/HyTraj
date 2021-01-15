import pandas as pd, numpy as np, matplotlib.pyplot as plt
import glob, pywt, pyclustering
from mpl_toolkits.basemap import Basemap

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pyclustering.cluster.elbow import elbow

import xarray as xr


class HyCluster:
    def __init__(self, data, projection=Basemap(projection="spstere", lon_0=180, boundinglat=-30), scale=False):
        self.data = data
        self.projection = projection
        self.scale = scale
        self.feat = HyWave(data, projection=projection).fit(scale=scale)

    def fit(self, kmax=50, method="KMeans", pyclus=True, scale=False):
        labels = Trajclustering(self.feat).fit(kmax=kmax, pyclus=pyclus)
        self.labels = pd.DataFrame(labels).T
        return self.labels
        
    def get_kmeans_cluster(self, n_clusters=4):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(self.feat)
        labels = pd.Series(kmeans.labels_, index=self.feat.index)
        self.labels = pd.DataFrame(labels).T
        return self.labels
        
class HyWave:
    def __init__(
        self, data, projection=Basemap(projection="spstere", lon_0=180, boundinglat=-30)
    ):
        self.data = data
        self.m = projection
        self.time = data.time.to_pandas()

    def fit(self, scale=True):
        ln, lt = self.m(
            self.data.sel(geo="lon").values, self.data.sel(geo="lat").values
        )
        ff = pd.concat([self._wavelet_features(lt), self._wavelet_features(ln)])
        ff.index = [
            "latmin",
            "lat25",
            "lat50",
            "lat75",
            "latmax",
            "lonmin",
            "lon25",
            "lon50",
            "lon75",
            "lonmax",
        ]
        if scale:
            ff = (ff - ff.min()) / (ff.max() - ff.min())
        return ff.T

    def _wavelet_features(self, data):
        wv = pywt.dwt(data.T, "haar")[0]
        wv = pd.DataFrame(wv, self.time).T.describe().iloc[3:]
        return wv


class Trajclustering:
    def __init__(self, data):
        self.traj = data

    def fit(self, kmax=50, pyclus=False):
        n, wce, labels = self.get_kmeans_cluster(kmax, plot=False, pyclus=pyclus)
        return labels

    def _elbow_method(self, kmax=50):
        wce = []
        nums = np.arange(1, kmax)
        for num in nums:
            kmeans = KMeans(n_clusters=num, random_state=0).fit(self.traj)
            wce.append(kmeans.inertia_)

        x0, y0 = 0.0, wce[0]
        x1, y1 = float(len(wce)), wce[-1]
        elbows = []
        for index_elbow in range(1, len(wce) - 1):
            x, y = float(index_elbow), wce[index_elbow]
            segment = abs((y0 - y1) * x + (x1 - x0) * y + (x0 * y1 - x1 * y0))
            norm = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            distance = segment / norm
            elbows.append(distance)
        n = nums[np.argmax(elbows) + 1]
        return n, wce

    def _optimal_cluster(self, kmax=50):
        elbow_instance = elbow(self.traj.values, 1, kmax)
        elbow_instance.process()
        amount_clusters = elbow_instance.get_amount()
        wce = elbow_instance.get_wce()
        return amount_clusters, wce

    def get_kmeans_cluster(self, kmax=50, plot=True, pyclus=False):
        if pyclus:
            n, wce = self._optimal_cluster(kmax=kmax)
        else:
            n, wce = self._elbow_method(kmax=kmax)
        kmeans = KMeans(n_clusters=n, random_state=0).fit(self.traj)
        labels = pd.Series(kmeans.labels_, index=self.traj.index)
        self.optim_k = n
        self.wce = wce
        if plot:
            self._plot_elbow_score(n, wce)
        return n, wce, labels

    def _plot_elbow_score(self, n, wce):
        nums = np.arange(1, len(wce) + 1)
        fig, ax = plt.subplots(1, 1, figsize=(14, 5))
        ax.plot(nums, wce, color="m")
        ax.scatter(n, wce[n - 1], color="red", marker=".", s=200)
        ax.axvline(n, ls="-.", color="k")
        ax.minorticks_on()
        ax.set_xlabel("Number of clusters")
        ax.set_ylabel("Within cluster Error")
        ax.set_title("Optimal number of clusters = %s" % n)
        plt.show()
