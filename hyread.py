import os, glob, xarray as xr, pickle
import numpy as np, pandas as pd
import multiprocessing as mp
import itertools
from joblib import Parallel, delayed, parallel_backend

class HyData():
    def __init__(self, files, stations):
        self.stations = stations
        self.files    = files
        print('Reading Data....')
        
    def read_all(self):
        ds = xr.Dataset()
        for station in stations:    
            ds[station] = self.read(station).to_array(dim='varn')
        return ds        
    
    def read(self, station):
        files = self.files
        dates = [filename.split('.')[-1] for filename in files]
        dates = pd.to_datetime(dates, format='%Y%m%d%H')
        lat   = pd.DataFrame(columns=dates)
        lon   = pd.DataFrame(columns=dates)
        alt   = pd.DataFrame(columns=dates)
        pre   = pd.DataFrame(columns=dates)
        dat   = [lat, lon, alt, pre]
        for filename, date in zip(files, dates):
            data = self.read_hysplit_file(filename, station)
            for var, col in zip(dat, data.columns):
                var[date] = data[col]
        data  = xr.Dataset({'lat':lat, 'lon':lon, 'alt':alt, 'pre':pre})
        data  = data.rename({'dim_0': 'step', 'dim_1': 'Date'}).astype('float')
        return data 
    
    def read_hysplit_file(self, filename, station, skp=0):
        start_index = self.stations.index(station)
        skip_lines = len(self.stations)
        columns  = ['lat', 'lon', 'height', 'pressure']
        with open(filename, 'r') as f:
            data = f.readlines()
        for num, line in enumerate(data):
            if 'PRESSURE' in line:
                skp = num 
                break
        data = data[skp+1:][start_index::skip_lines]
        data = [line.strip().split()[-4:] for line in data]
        data = pd.DataFrame(data, columns=columns)
        return data        

heights  = [500, 1000, 5000, 8000, 9000]
ddir     = '/home/pankaj/phd/airmass/data/gdas/'
tbase    = '/home/pankaj/mount/geoschem/hysplit/trajectories/gdas/all/'
stations = ['davs', 'marb', 'mcmu', 'myth', 'spol', 'syow', 'neum']


def run_parallel(hgt):
    tdir  = tbase + str(hgt) + '/data'
    files = sorted(glob.glob(tdir + '/*'))#[:10]
    data  = HyData(files, stations).read_all()
    return data

num = len(heights)
print 'Number of threads to be used: %s' % num
ds = Parallel(n_jobs = num)(delayed(run_parallel)(height) for height in heights)
for i in np.arange(num):
    ds[i].to_netcdf(ddir + '%s.gdas.nc' %heights[i])

data = xr.Dataset()
for i, height in enumerate(heights):
    data[height] = ds[i].to_array(dim='station')
data = data.to_array(name='GDAS trajectories', dim='height')
data.to_netcdf(ddir + 'all.gdas.nc')
data.to_dataset()

