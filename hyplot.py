import glob, pickle, os, pywt, pyclustering, seaborn as sns
os.environ['PROJ_LIB'] = '/home/pankaj/.local/Anaconda3/share/proj'
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import xarray as xr, salem, utils, geopandas as gpd
from mpl_toolkits.basemap import Basemap, addcyclic, cm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

class TrajPlot():
    def __init__(self, lat, lon, labels):
        self.labels = labels
        self.nclus = labels.nunique()
        self.lat = lat
        self.lon = lon
        self.slat = lat.iloc[0, 0]
        self.slon = lon.iloc[0, 0]
        
    def get_basemap(self, ax = None, min_lat = -35):
        if not ax:
            fig, ax = plt.subplots(1, 1, figsize=(7, 7))
        m = Basemap(projection = 'spstere', lon_0 = 180, boundinglat = min_lat, round = True, ax = ax)
        m.drawcoastlines(linewidth=1.5)
        m.drawcountries(linewidth=0.55)
        m.drawmeridians(np.arange(0, 360, 30), labels = [0,0,1,0])
        m.drawparallels(np.arange(-80, -20, 20), labels = [1,1,0,0])
        return m
    
    @staticmethod
    def mean_trajectory(latitudes, longitudes):
        """ Get the centroid of parcels at each timestep. """
        x = (np.cos(np.radians(latitudes)) * 
            np.cos(np.radians(longitudes)))
        y = (np.cos(np.radians(latitudes)) * 
            np.sin(np.radians(longitudes)))
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
    
    def get_representative_trajectories(self):
        columns = self.labels.index
        clusters = ['CLUS_'+ str(i+1) for i in np.arange(self.nclus)]
        self.rep_traj_lat = pd.DataFrame(columns=clusters)
        self.rep_traj_lon = pd.DataFrame(columns=clusters)
        for num, cluster in enumerate(clusters):
            col = columns[labels==num]
            lats, lons = self.mean_trajectory(self.lat[col], self.lon[col])
            self.rep_traj_lat[cluster], self.rep_traj_lon[cluster] = (lats, lons)
        return self.rep_traj_lat, self.rep_traj_lon
    
    def plot_representative_trajectories(self, ax = None, cmap = plt.cm.jet, lw = 3, s = 200, min_lat = -35, scale = 30, c ='r'):        
        lw = self.labels.value_counts().sort_index()
        lw = scale*lw/lw.sum()

        m = self.get_basemap(ax = ax, min_lat = min_lat)         
        xx, yy = m(self.slon, self.slat)
        m.scatter(xx, yy, color = c, marker = '*', zorder=40, s = s)

        lat1, lon1 = self.get_representative_trajectories()
        colors = [cmap(i) for i in np.linspace(0, 1, self.nclus)]
        for count, tr in enumerate(lat1.columns):
            xx, yy = m(lon1[tr].values, lat1[tr].values)
            m.plot(xx, yy, color = colors[count], lw = lw[count])
        return ax
