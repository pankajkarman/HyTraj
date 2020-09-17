import warnings; warnings.filterwarnings("ignore")
import glob, pickle, os
from facets import facets
import pandas as pd, numpy as np, matplotlib.pyplot as plt, pysplit as py, geopandas as gpd
import traj_dist.distance as tdist, fastcluster as fc, scipy.cluster.hierarchy as sch
from mpl_toolkits.basemap import Basemap, addcyclic, cm
from matplotlib import ticker 
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def get_seasonal_columns(traj, year = 2010, season = 'summer'): 
    seas = {'winter':[6, 7, 8], 'spring':[9, 10, 11], 'summer':[12, 1, 2], 'autumn':[3, 4, 5]}
    col = traj.data['lat'].columns
    col = col[col.year==year]
    col = col[np.isin(col.month, seas[season])]
    return col

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


class TrajCluster():
    def __init__(self, lat, lon, alt = None, pre = None):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.pre = pre
        self.n_traj = len(self.lat.columns) 
        self.slat = self.lat.iloc[0,0]
        self.slon = self.lon.iloc[0,0]
        
    def plot_cluster(self):
    	fig, ax = facets(1, 1, width=10, aspect = 0.4, internal_pad = 0.3); ax = ax[0]
        ax.plot(range(1, len(self.link)+1), self.link[::-1, 2])
        ax.plot(range(2, len(self.link)), knee)
        ax.set_ylabel('Cluster Distance')
        ax.set_xlabel('Number of Clusters')
        ax.set_xlim([1, 10])
        
    def find_optimal_nclus(self, verbose = False, plot = False): 
        # optimal number of cluster based on elbow method
        knee = np.diff(self.link[::-1, 2], 2)
        self.between_variance = self.link[::-1, 2]
        
        if plot:
        	self.plot_cluster()

        k1 = knee.argmax() + 2; knee[knee.argmax()] = 0
        k2 = knee.argmax() + 2; knee[knee.argmax()] = 0
        k3 = knee.argmax() + 2
        if verbose:
            print 'First optimal number of clusters = ' + str(k1)
            print 'Second optimal number of clusters = ' + str(k2)
            print 'Third optimal number of clusters = ' + str(k3)
        return self    
        
    def get_linkage(self, metric = "sspd", method = "ward", type_d="spherical"):
        traj_list = []
        for traj in self.lat.columns:
            ds = pd.DataFrame([])
            ds['lat'] = self.lat[traj]
            ds['lon'] = self.lon[traj]
            traj_list.append(ds.values)
        self.p_dist = tdist.pdist(traj_list, metric = metric, type_d=type_d)
        self.link = fc.linkage(self.p_dist, method = method)
        return self
    
    def fit(self, nclus = 7):
        self.nclus = nclus
        self.labels = sch.fcluster(self.link, self.nclus, criterion = "maxclust")-1
        self.cluster = pd.DataFrame(data = self.labels, index = self.lat.columns).T
        return self
    
    def get_representative_trajectories(self):
        labels = self.cluster.values[0]
        columns = self.cluster.columns
        clusters = ['CLUS_'+ str(i+1) for i in np.arange(self.nclus)]
        self.rep_traj_lat = pd.DataFrame(columns=clusters)
        self.rep_traj_lon = pd.DataFrame(columns=clusters)
        for num, cluster in enumerate(clusters):
            col = columns[labels==num]
            lats, lons = mean_trajectory(self.lat[col], self.lon[col])
            self.rep_traj_lat[cluster], self.rep_traj_lon[cluster] = (lats, lons)
        return self.rep_traj_lat, self.rep_traj_lon
    
    def get_basemap(self, ax = None, min_lat = -35):
        if not ax:
            fig, ax = facets(1,1, width = 10, aspect = 0.6); ax = ax[0]
        m = Basemap(projection = 'spstere', lon_0 = 180, boundinglat = min_lat, round = True, ax = ax)
        m.drawcoastlines(linewidth=1.5)
        m.drawcountries(linewidth=0.55)
        m.drawmeridians(np.arange(0, 360, 30), labels = [0,0,1,0])
        m.drawparallels(np.arange(-80, -20, 20), labels = [1,1,0,0])
        return m
        
    
    def plot_trajectories(self, ax = None, cmap = plt.cm.jet, lw = 0.3, s = 200, min_lat = -35):
        m = self.get_basemap(ax = ax, min_lat = min_lat)                
        xx, yy = m(self.slon, self.slat)
        m.scatter(xx, yy, color = 'r', s = s)
        
        lat1, lon1 = [self.lat, self.lon]
        colors = [cmap(i) for i in np.linspace(0, 1, self.nclus)]
        for count, tr in enumerate(lat1.columns):
            c = self.cluster[tr].values[0]
            xx, yy = m(lon1[tr].values, lat1[tr].values)
            m.plot(xx, yy, color = colors[c], lw = lw)
        return ax 
        
    def plot_color_trajectories(self, ax = None, cmap = plt.cm.jet, lw = 0.3, s = 200, min_lat = -35, c ='r'):
        m = self.get_basemap(ax = ax, min_lat = min_lat)                
        xx, yy = m(self.slon, self.slat)
        m.scatter(xx, yy, color = c, marker = '*', zorder=40, s = s)

        x, y = m(self.lon.values, self.lat.values)
        h = m.scatter(x, y, c = self.pre.values, s = lw, cmap=cmap )
        return m, h
        
    def plot_clustered_trajectories(self, ax = None, cmap = plt.cm.jet, lw = 3, s = 200, min_lat = -35, scale = 10, c ='r'):        
        lw = pd.Series(self.cluster.values[0]).value_counts().sort_index()
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
    
    def plot_representative_trajectories(self, ax = None, cmap = plt.cm.jet, lw = 3, s = 200, min_lat = -35):        
        m = self.get_basemap(ax = ax, min_lat = min_lat)         
        xx, yy = m(self.slon, self.slat)
        m.scatter(xx, yy, color = 'r', s = s)
        
        lat1, lon1 = self.get_representative_trajectories()
        colors = [cmap(i) for i in np.linspace(0, 1, self.nclus)]
        for count, tr in enumerate(lat1.columns):
            xx, yy = m(lon1[tr].values, lat1[tr].values)
            m.plot(xx, yy, color = colors[count], lw = lw)
        return ax      
    
    def plot_frequency(self, ax = None, cmap = plt.cm.jet, s = 10, min_lat = -35):                
        cax = inset_axes(ax, width="4%", height="93%", loc='lower left', borderpad = 1.9,
                         bbox_to_anchor=(1.1, 0., 1, 1), bbox_transform = ax.transAxes)
        m = self.get_basemap(ax = ax, min_lat = min_lat)
        xx, yy = m(self.slon, self.slat)
        m.scatter(xx, yy, color = 'r', s = s)
        
        latx = np.arange(-90, 91, 1)
        lonx = np.arange(-180, 181, 1)
        
        c = np.zeros((lonx.shape[0], latx.shape[0]))
        
        for col in self.lat.columns:
            a = np.searchsorted(lonx, self.lon[col].values)
            b = np.searchsorted(latx, self.lat[col].values)
            c[a,b] += 1
        c[c == 0] = np.nan
        c = 100*c/self.n_traj
        
        latx, lonx = np.meshgrid(latx,lonx)
        lonx, latx = m(lonx, latx)
        h = m.contourf(lonx, latx, c)
        plt.colorbar(h, cax = cax)
        return h, m 
    
    def plot_height(self, ax = None, cmap = plt.cm.jet, lw = 0.3):
        if not ax:
            fig, ax = facets(1,1, width = 10, aspect = 0.6)
            ax = ax[0]
            
        colors = [cmap(i) for i in np.linspace(0, 1, self.nclus)]
        for count, tr in enumerate(self.alt.columns):
            c = self.cluster[tr].values[0]
            ax.plot(self.alt.index, self.alt, color = colors[c], lw = lw)
        
        ax.set_xlabel('Timestep [hr]')
        ax.set_ylabel('Height [m]')
        ax.minorticks_on()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        return ax
    
    def plot_pressure(self, ax = None, cmap = plt.cm.jet, lw = 0.3):
        if not ax:
            fig, ax = facets(1,1, width = 10, aspect = 0.6)
            ax = ax[0]
        
        colors = [cmap(i) for i in np.linspace(0, 1, self.nclus)]
        for count, tr in enumerate(self.pre.columns):
            c = self.cluster[tr].values[0]
            ax.plot(self.pre.index, self.pre, color = colors[c], lw = lw)
            
        ax.invert_yaxis()
        ax.set_yscale('log')
        ax.minorticks_on()
        ax.set_xlabel('Timestep [hr]')
        ax.set_ylabel('Pressure [hPa]')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))
        ax.yaxis.set_minor_formatter(ticker.FormatStrFormatter("%d"))
        return ax 
    
    def plot_dendrogram(self, ax=None, p=10, D=50):
        if not ax:
            fig, ax = facets(1,1, width=10, aspect=0.5); ax = ax[0]
        dn = sch.dendrogram(self.link, ax = ax, orientation='top', 
                            show_contracted=True, truncate_mode = 'lastp', p = p)
        ax.set_ylabel('Distance')
        ax.axhline(D, color = 'k', ls = '-.')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        return ax

class Trajectory():
    def __init__(self, station = 'myth', height = '5000', runtime = 360,
                 base = '/mnt/repo4/hysplit/antarctic/gdas/', ddir = './data/gdas/'):
        self.station = station
        self.height = height
        self.runtime = runtime
        self.ddir = ddir
        self.filename = self.ddir + self.station + '.' + self.height +  '.pkl' 
        
        loc = {'davs':(-69, 78), 'spol':(-90, 335), 'neum':(-71, 352), 'myth':(-70, 11),
               'syow':(-69, 40), 'marb':(-64, 303), 'mcmu':(-78, 167), 'mirn':(-66, 93)}
        
        self.location = loc[self.station]
        self.working_dir = base + self.station + '/working/'
        self.storage_dir = base + self.station + '/storage/'
    
    def save(self):        
        trajg = py.make_trajectorygroup(self.storage_dir + '*' + self.height + '*')
        self.trajs = py.TrajectoryGroup([traj for traj in trajg if len(traj.data.index) == self.runtime + 1])

        lat = pd.DataFrame([]); lon = pd.DataFrame([])
        alt = pd.DataFrame([]); pre = pd.DataFrame([])
        for count, traj in enumerate(self.trajs):
            date = traj.data.DateTime[0]
            col = pd.to_datetime(date)#.date()
            geom = traj.data.geometry.centroid
            lat[col] = geom.y
            lon[col] = geom.x
            pre[col] = traj.data['Pressure']
            alt[col] = traj.data.geometry.apply(lambda p: p.z)

        if not os.path.exists(self.ddir):
            os.makedirs(self.ddir)
        with open(self.filename, 'w') as outfile:
            pickle.dump({'lat': lat, 'lon': lon, 'alt' : alt, 'pre' : pre}, outfile)
        return self
    
    def load(self):
        if not os.path.exists(self.filename):
            self.save()
        self.data = pd.read_pickle(self.filename)
        return self 
