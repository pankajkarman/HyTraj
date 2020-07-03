import pandas as pd, numpy as np
import xarray as xr

class HyData():
    def __init__(self, filename, runtime=-360):
        loc = {'davs':(-69, 78), 'spol':(-90, 335), 'neum':(-71, 352), 'myth':(-70, 11),
               'syow':(-69, 40), 'marb':(-64, 303), 'mcmu':(-78, 167), 'mirn':(-66, 93)}
        self.runtime  = runtime
        self.path     = filename
        self.filename = filename.split('/')[-1]
        self.height   = self.filename.split('.')[1]
        self.station  = self.filename.split('.')[0]
        self.location = loc[self.station]
    
    def load(self, dates = []):
        ds = xr.open_dataset(self.path)
        traj = {'lat':ds.lat.to_pandas(), 'lon':ds.lon.to_pandas(), 'alt':ds.alt.to_pandas(), 'pre':ds.pre.to_pandas()} 
        date = traj['lat'].columns
        date = pd.to_datetime(date.date)
        for key in traj.keys():
            traj[key].columns = date
        if len(dates) > 0:
            for key in traj.keys():
                traj[key] = traj[key][dates]            
        self.data = traj
        return self.data 
