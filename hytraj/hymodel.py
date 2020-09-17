import warnings; warnings.filterwarnings("ignore")
import glob, pickle, os, cartopy.crs as ccrs
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import xarray as xr, salem, geopandas as gpd
from mpl_toolkits.basemap import Basemap, addcyclic, cm
from init import *

def surface_ozone():
    filenames=glob.glob('/home/pankaj/phd/code/airmass/data/surf_ozo/*')
    kwargs=dict(skiprows=range(30))
    data=pd.DataFrame([])
    for file in filenames:
        name=file.split('/')[-1]
        df=pd.read_csv(file, sep='\s+',skiprows=range(28),parse_dates=True)[['C32','TIME.1']]
        df.columns=['Date',name]
        df.index=pd.to_datetime(df.Date)
        df[name][abs(df[name])>100]=np.nan
        data=pd.concat([data,df], axis=1)
    data = data[['syow','mcmu','spol','neum', 'marb', 'arht']]
    return data 

def normalize(data):
    data = (data - data.min()) / (data.max() - data.min())
    return data

def get_weight(psc):
    wgt = np.ones_like(psc)
    avg = np.nanmean(psc[psc!=0])
    wgt[psc>=2*avg] = 1.0
    wgt[(avg<=psc) & (psc<2*avg)] = 0.75
    wgt[(0.5*avg<=psc) & (psc<avg)] = 0.5
    wgt[(psc<0.5*avg)] = 0.25
    return wgt    

class Receptor():
    def __init__(self, ozone, traj, station_name=None):
        self.ozone    = ozone
        self.traj     = traj
        self.lat      = traj['lat'] 
        self.lon      = traj['lon'] 
        self.dates    = traj['lat'].columns
        self.station  = station_name
        self.location = [traj[var].iloc[0, 0] for var in ['lat', 'lon']]  
        
    def get_density(self, latx = np.arange(-90, 91, 1), lonx = np.arange(-180, 181, 1), normalize=True):
        density, lonx, latx = np.histogram2d(self.lon.values.flatten(), self.lat.values.flatten(), [lonx, latx], density=normalize)
        return density
        
    def calculate_pscf(self, thresh = 0.5, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1), multi=False):
        self.ozone_threshold = self.ozone.quantile(thresh)
        sub = self.ozone[self.ozone > self.ozone_threshold]
        slat = self.traj['lat'][sub.index]
        slon = self.traj['lon'][sub.index]
        self.dates_with_more_than_threshold_ozone = sub.index
        num1, _, _ = np.histogram2d(self.lon.values.flatten(), self.lat.values.flatten(), [lonx, latx], density=False)
        num2, _, _ = np.histogram2d(slon.values.flatten(), slat.values.flatten(), [lonx, latx], density=False)
        pscf = num2 / num1
        self.rt_pscf = num2
        if not multi:
            pscf[pscf==0] = np.nan
            pscf[pscf>1.0] = 1.0
            pscf = xr.DataArray(pscf, coords=[lonx[:-1], latx[:-1]], dims=['Longitude', 'Latitude'])
            pscf.name = 'Potential Source Contribution Function'
            pscf.attrs['station_name'] = self.station
            self.pscf = pscf
            return pscf
        else:
            return num2, num1, np.sum(num1)           
        
    
    def calculate_cwt(self, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1)): 
        
        cwt = np.zeros((lonx.shape[0]-1, latx.shape[0]-1))
        tau  = np.zeros_like(cwt)
        nums = np.zeros_like(cwt)
        for column in self.lat.columns:
            ozo = self.ozone[column]
            num, _, _ = np.histogram2d(self.lon[column].values.flatten(), self.lat[column].values.flatten(), [lonx, latx], density=False)
            tlen = float(len(self.lat[column].values))
            ttau = num / tlen
            cwt += ozo * ttau 
            tau += ttau
            nums+= num
        cwt = cwt / tau
        cwt[cwt==0] = np.nan
        cwt = xr.DataArray(cwt, coords=[lonx[:-1], latx[:-1]], dims=['Longitude', 'Latitude'])
        cwt.name = 'Concentration Weighted Trajectory'
        cwt.attrs['station_name'] = self.station
        self.cwt = cwt
        self.rt_cwt = nums
        return self.cwt
    
    def get_weighted_pscf(self, thresh = 0.5, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1)):
        self.pscf = self.calculate_pscf(thresh = thresh, latx = latx, lonx = lonx)
        wgt = get_weight(self.rt_pscf)
        self.pscf *= wgt
        return self.pscf
        
    def get_weighted_cwt(self, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1)):
        self.cwt = self.calculate_cwt(latx = latx, lonx = lonx)
        wgt = get_weight(self.rt_cwt)
        self.cwt *= wgt
        return self.cwt
    
    
    def tsa(self): # to be implemented
        pass
    
    def plot_map(self, pscf, boundinglat = -20, axes=[], vmax=1.0):
        if len(axes) == 0:
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
            cax = fig.add_axes([0.15, 0.06, 0.7, 0.04])
            
        elif len(axes) == 2:
            fig, ax = axes
            cax = None
            
        else:
            fig, ax, cax = axes
        m = Basemap(projection = 'spstere', lon_0 = 180, boundinglat = boundinglat, round = True, ax = ax)
        latx, lonx = np.meshgrid(pscf['Latitude'], pscf['Longitude'])
        lonx, latx = m(lonx, latx)
#         h = m.contourf(lonx, latx, pscf)
        h = m.pcolor(lonx, latx, pscf, vmin=0, vmax=vmax)
        if cax:
            cbar = plt.colorbar(h, cax=cax, orientation='horizontal')
#         cbar.ax.locator_params(nbins=4)
        m.drawcoastlines(linewidth=1.5)
        m.drawcountries(linewidth=0.55)
        ax.set_title(self.station, fontweight='bold')
        return fig, ax, m

class MultiReceptor():
    def __init__(self, height, tdir, start='01-01-1980'):
        self.tdir = tdir
        self.height = height
        self.ozone_data = surface_ozone()[start:]
        
    def calculate_mspscf(self, stations, months, thresh=0.75, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1)):
        pa = 0
        pb = 0
        nums  = np.zeros((lonx.shape[0]-1, latx.shape[0]-1))
        for i, station in enumerate(stations):
            trfile  = '%s/%s.%s.nc' % (self.tdir, station, self.height)
            if station=='mcmu':
                ozo1 = self.ozone_data['arht'].dropna()
                ozo2 = self.ozone_data['mcmu'].dropna()
                ozone_data = pd.concat([ozo1, ozo2])
            else:
                ozone_data = self.ozone_data[station].dropna()
            ozone = ozone_data[np.isin(ozone_data.index.month, months)]
            traj = HyData(trfile).load(dates=ozone.index)
            model = Receptor(ozone, traj, station_name=station)
            m, n, tot = model.calculate_pscf(thresh=thresh, multi=True) 
            nums+= m
            pa += m/tot
            pb += n/tot
        pscf = pa/pb
        pscf[pscf==0] = np.nan
        pscf[pscf>1.0] = 1.0
        pscf = xr.DataArray(pscf, coords=[lonx[:-1], latx[:-1]], dims=['Longitude', 'Latitude'])
        pscf.name = 'Potential Source Contribution Function'
        self.pscf = pscf
        self.rt_mspscf = nums
        return pscf        
    
    def calculate_mscwt(self, stations, months, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1)):
        cwt  = np.zeros((lonx.shape[0]-1, latx.shape[0]-1))
        tau  = np.zeros_like(cwt)
        nums = np.zeros_like(cwt)
        for i, station in enumerate(stations):
            trfile  = '%s/%s.%s.nc' % (self.tdir, station, self.height)
            if station=='mcmu':
                ozo1 = self.ozone_data['arht'].dropna()
                ozo2 = self.ozone_data['mcmu'].dropna()
                ozone_data = pd.concat([ozo1, ozo2])
            else:
                ozone_data = self.ozone_data[station].dropna()
            ozone = ozone_data[np.isin(ozone_data.index.month, months)]
            traj = HyData(trfile).load(dates=ozone.index)
            model = Receptor(ozone, traj, station_name=station)
            for column in model.lat.columns:
                ozo = model.ozone[column]
                num, _, _ = np.histogram2d(model.lon[column].values.flatten(), model.lat[column].values.flatten(), [lonx, latx], density=False)
                tlen = float(len(model.lat[column].values))
                ttau = num / tlen
                cwt += ozo * ttau 
                tau += ttau
                nums+= num
        cwt = cwt / tau
        #cwt[cwt==0] = np.nan
        cwt = xr.DataArray(cwt, coords=[lonx[:-1], latx[:-1]], dims=['Longitude', 'Latitude'])
        cwt.name = 'Concentration Weighted Trajectory'
        self.cwt = cwt
        self.rt_mscwt = nums
        return self.cwt
    
    def get_weighted_pscf(self, stations, months, thresh=0.75, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1)):
        self.pscf  = self.calculate_mspscf(stations, months, thresh=thresh, latx = latx, lonx = lonx)
        self.pscf *= get_weight(self.rt_mspscf)
        return self.pscf
        
    def get_weighted_cwt(self, stations, months, latx = np.arange(-90,  91,  1), lonx = np.arange(-180, 181, 1),                         normalise=True):
        self.cwt  = self.calculate_mscwt(stations, months, latx = latx, lonx = lonx)
        self.cwt *= get_weight(self.rt_mscwt)
        if normalise:
            self.cwt  = normalize(self.cwt)
        return self.cwt
    
    def plot_map(self, pscf, boundinglat = -20, axes=None):
        if len(axes) == 0:
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
            cax = fig.add_axes([0.15, 0.06, 0.7, 0.04])
        else:
            fig, ax, cax = axes
        m = Basemap(projection = 'spstere', lon_0 = 180, boundinglat = boundinglat, round = True, ax = ax)
#         data, lonx = addcyclic(pscf.T.values, pscf['Longitude'])
#         latx, lonx = np.meshgrid(pscf['Latitude'], lonx)

        latx, lonx = np.meshgrid(pscf['Latitude'], pscf['Longitude'])
        data = pscf.T.values
        lonx, latx = m(lonx, latx)
        h = m.pcolor(lonx, latx, data.T)
        cbar = plt.colorbar(h, cax=cax, orientation='horizontal')
        cbar.ax.locator_params(nbins=4)
        cbar.ax.minorticks_on()
        m.drawcoastlines(linewidth=1.5)
        m.drawcountries(linewidth=0.55)
        return fig, ax, m
    
def calculate_rtwc(model, bcwt):
    if bcwt.name:
        bcwt = np.nan_to_num(bcwt.values)
    latx = np.arange(-90,  91,  1)
    lonx = np.arange(-180, 181, 1)
    err  = 100
    while err >=0.001:
        cwt  = np.zeros((lonx.shape[0]-1, latx.shape[0]-1))
        tau  = np.zeros_like(cwt)
        nums = np.zeros_like(cwt)
        for column in model.lat.columns:
            ozo = model.ozone[column]
            num, _, _ = np.histogram2d(model.lon[column].values.flatten(), model.lat[column].values.flatten(),[lonx, latx], density=False)
            tlen = float(len(model.lat[column].values))
            ttau = num / tlen
            tavg = np.sum(bcwt*num / tlen)
            #print ozo
            cwt += ttau * ozo * bcwt / tavg
            tau += ttau
            nums+= num
        cwt  = np.nan_to_num(cwt / tau)
        err  = (cwt - bcwt) / bcwt
        err  = np.nansum(err)
        bcwt = cwt
    cwt = normalize(cwt)
    cwt[cwt==0] = np.nan
    cwt = xr.DataArray(cwt, coords=[lonx[:-1], latx[:-1]], dims=['Longitude', 'Latitude'])
    cwt.name = 'Concentration Weighted Trajectory'
    return cwt

