import numpy as np
import pandas as pd
import xarray as xr


class HyData:
    def __init__(self, files, stations):
        self.stations = stations
        self.files = files
        # print('Reading Data....')

    def read(self):
        ds = xr.Dataset()
        for station in self.stations:
            ds[station] = self._read(station).to_array(dim="geo")
        return ds

    def _read(self, station):
        files = self.files
        dates = [filename.split(".")[-1] for filename in files]
        dates = pd.to_datetime(dates, format="%Y%m%d%H")
        lat = pd.DataFrame(columns=dates)
        lon = pd.DataFrame(columns=dates)
        alt = pd.DataFrame(columns=dates)
        pre = pd.DataFrame(columns=dates)
        dat = [lat, lon, alt, pre]
        for filename, date in zip(files, dates):
            data = self.read_hysplit_file(filename, station)
            for var, col in zip(dat, data.columns):
                var[date] = data[col]
        data = xr.Dataset({"lat": lat, "lon": lon, "alt": alt, "pre": pre})
        data = data.rename({"dim_0": "step", "dim_1": "time"}).astype("float")
        return data

    def read_hysplit_file(self, filename, station, skp=0):
        start_index = self.stations.index(station)
        skip_lines = len(self.stations)
        columns = ["lat", "lon", "height", "pressure"]
        with open(filename, "r") as f:
            data = f.readlines()
        for num, line in enumerate(data):
            if "PRESSURE" in line:
                skp = num
                break
        data = data[skp + 1 :][start_index::skip_lines]
        data = [line.strip().split()[-4:] for line in data]
        data = pd.DataFrame(data, columns=columns)
        return data
