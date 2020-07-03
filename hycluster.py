import glob, pickle, os, pywt, pyclustering, seaborn as sns
os.environ['PROJ_LIB'] = '/home/pankaj/.local/Anaconda3/share/proj'
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import xarray as xr, salem, utils, geopandas as gpd
from mpl_toolkits.basemap import Basemap, addcyclic, cm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
# from pyclustering.cluster.elbow import elbow

class TrajMining():
    def __init__(self, station, height, station_name = None, tdir='/home/pankaj/phd/tropo/antarctic/causal/data/traj',                  projection = Basemap(projection = 'spstere', lon_0 = 180, boundinglat= -30)):
        name = {'spol': 'South Pole', 'neum':'Neumayer', 'mcmu':'McMurdo', 'arht':'Arrival Height', 'syow':'Syowa', 'marb':'Marambio', 'davs':'Davis', 'mirn':'Mirny', 'myth':'Maitri'}
        self.station = station
        self.height = height
        self.filename = '%s/%s.%s.nc' % (tdir, station, height)
        self.traj = HyData(self.filename).load()
        self.m = projection  
        if station_name is not None:
            self.station_name = station_name
        else:
            self.station_name = name[station]
    
    def get_projected_trajectory(self, traj):
        mlat = []
        mlon = []
        for i, col in enumerate(traj['lat'].columns):
            latx = traj['lat'].iloc[:,i].values
            lonx = traj['lon'].iloc[:,i].values
            lonx, latx = self.m(lonx, latx)
            mlat.append(latx)
            mlon.append(lonx)
        mlat = pd.DataFrame(np.array(mlat).T, columns=traj['lat'].columns)
        mlon = pd.DataFrame(np.array(mlon).T, columns=traj['lat'].columns)
        return mlat, mlon
    
    def get_wavelet_feature(self, scale=True):
        ff = []
        cols = ['latmin', 'lat25', 'lat50', 'lat75', 'latmax', 'lonmin', 'lon25', 'lon50', 'lon75', 'lonmax']
        mlat, mlon = self.get_projected_trajectory(traj = self.traj)
        lat = mlat.T.values
        lon = mlon.T.values
        
        def wavelet_feature(lat):
            ca = pd.Series(pywt.dwt(lat, 'haar')[0]).describe().values[3:]
            return ca
            
        for num in np.arange(lat.shape[0]):
            ca = wavelet_feature(lat[num,:])
            cb = wavelet_feature(lon[num,:])
            cc = np.hstack((ca, cb))
            ff.append(cc)
        ff = pd.DataFrame(ff, index=mlat.columns, columns=cols)
        ff[ff.abs()>=1e8] = np.nan
        if scale:
            ff = (ff - ff.min()) / (ff.max() - ff.min())
        return ff  

class Trajclustering():
    def __init__(self, data):
        self.traj = data
        
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
            sns.distplot(labels, kde=False)
            plt.show()
        return n, wce, labels
    
    def _plot_elbow_score(self, n, wce):
        nums = np.arange(1, len(wce)+1)
        fig, ax = plt.subplots(1, 1, figsize=(14, 5))
        ax.plot(nums, wce)
        ax.scatter(n, wce[n-1], color='red', marker='*')
        ax.minorticks_on()
        ax.set_xlabel('Number of clusters')
        ax.set_ylabel('Within cluster Error')
        ax.set_title('Optimal number of clsters = %s' % n, y=0.9)
        plt.show()
