import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from mpl_toolkits.basemap import Basemap, addcyclic, cm



def mean_trajectory(latitudes, longitudes):
    """ Get the centroid of parcels at each timestep. """
    x = np.cos(np.radians(latitudes)) * np.cos(np.radians(longitudes))
    y = np.cos(np.radians(latitudes)) * np.sin(np.radians(longitudes))
    z = np.sin(np.radians(latitudes))

    # Get average x, y, z values
    mean_x = np.mean(x, axis=1)
    mean_y = np.mean(y, axis=1)
    mean_z = np.mean(z, axis=1)

    # Convert average values to trajectory latitudes and longitudes
    mean_longitudes = np.degrees(np.arctan2(mean_y, mean_x))
    hypotenuse = np.sqrt(mean_x ** 2 + mean_y ** 2)
    mean_latitudes = np.degrees(np.arctan2(mean_z, hypotenuse))
    return mean_latitudes, mean_longitudes


class ClusterPlot:
    def __init__(
        self,
        data,
        cluster,
        proj=Basemap(projection="spstere", lon_0=180, boundinglat=-30),
    ):
        self.lat = data.sel(geo="lat").to_pandas()
        self.lon = data.sel(geo="lon").to_pandas()
        self.n_traj = len(self.lat.columns)
        self.slat = self.lat.iloc[0, 0]
        self.slon = self.lon.iloc[0, 0]
        self.cluster = cluster
        self.nclus = cluster.T.nunique().values[0]
        self.m = proj

    def get_representative_trajectories(self):
        labels = self.cluster.values[0]
        columns = self.cluster.columns
        kcount = []
        clusters = ["CLUS_" + str(i + 1) for i in np.arange(self.nclus)]
        self.rep_traj_lat = pd.DataFrame(columns=clusters)
        self.rep_traj_lon = pd.DataFrame(columns=clusters)
        for num, cluster in enumerate(clusters):
            col = columns[labels == num]
            kcount.append(len(col))
            lats, lons = mean_trajectory(self.lat[col], self.lon[col])
            self.rep_traj_lat[cluster], self.rep_traj_lon[cluster] = (lats, lons)
        return self.rep_traj_lat, self.rep_traj_lon, kcount

    def plot_representative_trajectories(self, ax=None, cmap=plt.cm.jet, lw=3, s=200):
        m = self.m
        xx, yy = m(self.slon, self.slat)
        m.scatter(xx, yy, color="r", s=s)

        lat1, lon1, kcount = self.get_representative_trajectories()
        colors = [cmap(i) for i in np.linspace(0, 1, self.nclus)]
        for count, tr in enumerate(lat1.columns):
            lwd = lw*kcount[count]/np.sum(kcount)
            xx, yy = m(lon1[tr].values, lat1[tr].values)
            m.plot(xx, yy, color=colors[count], lw=lwd)
        return ax
