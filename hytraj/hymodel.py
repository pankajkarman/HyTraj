import glob
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic, cm


def normalize(data):
    data = (data - data.min()) / (data.max() - data.min())
    return data


class HyReceptor:
    def __init__(
        self,
        ozone,
        traj,
        station_name="Davis",
        latx=np.arange(-90, 91, 1),
        lonx=np.arange(-180, 181, 1),
    ):
        self.ozone = ozone
        self.traj = traj[station_name]
        self.lat = self.traj.sel(geo="lat").to_pandas()
        self.lon = self.traj.sel(geo="lon").to_pandas()
        self.latx = latx
        self.lonx = lonx
        self.dates = self.lat.columns
        self.station = station_name
        self.location = self.traj.isel(step=0, time=0).sel(geo=["lat", "lon"]).values

    def get_density(self, lon, lat, density=True):
        density, lonx, latx = np.histogram2d(
            lon, lat, [self.lonx, self.latx], density=density
        )
        return density

    def get_weight(self, psc):
        wgt = np.ones_like(psc)
        avg = np.average(psc)
        wgt[psc >= 2 * avg] = 1.0
        wgt[(avg <= psc) & (psc < 2 * avg)] = 0.75
        wgt[(0.5 * avg <= psc) & (psc < avg)] = 0.5
        wgt[(psc < 0.5 * avg)] = 0.25
        return wgt

    def to_nc(self, data, name="Potential Source Contribution Function"):
        pscf = xr.DataArray(
            data,
            coords=[self.lonx[:-1], self.latx[:-1]],
            dims=["Longitude", "Latitude"],
        )
        pscf.name = name
        pscf.attrs["station_name"] = self.station
        return pscf

    def calculate_pscf(self, thresh=0.5, multi=False, weighted=True):
        self.ozone_threshold = self.ozone.quantile(thresh)
        sub = self.ozone[self.ozone > self.ozone_threshold]
        slat = self.lat[sub.index]
        slon = self.lon[sub.index]
        self.dates_with_more_than_threshold_ozone = sub.index
        num1 = self.get_density(
            self.lon.values.flatten(), self.lat.values.flatten(), density=False
        )
        num2 = self.get_density(
            slon.values.flatten(), slat.values.flatten(), density=False
        )
        self.pscf = num2 / num1
        self.rt_pscf = num2
        if weighted:
            wgt = self.get_weight(self.rt_pscf)
            self.pscf *= wgt
        self.pscf = self.to_nc(self.pscf, name="PSCF")
        if not multi:
            return self.pscf
        else:
            return num2, num1, np.sum(num1)

    def calculate_cwt(self, weighted=True):
        cwt = np.zeros((self.lonx.shape[0] - 1, self.latx.shape[0] - 1))
        tau = np.zeros_like(cwt)
        nums = np.zeros_like(cwt)
        for column in self.lat.columns:
            tlen = float(len(self.lat[column].values))
            num = self.get_density(
                self.lon[column].values.flatten(),
                self.lat[column].values.flatten(),
                density=False,
            )
            ttau = num / tlen
            cwt += ttau * self.ozone[column]
            tau += ttau
            nums += num
        self.cwt = cwt / tau
        self.rt_cwt = nums
        if weighted:
            wgt = self.get_weight(self.rt_cwt)
            self.cwt *= wgt
        self.cwt = self.to_nc(self.cwt, name="CWT")
        return self.cwt

    def calculate_rtwc(self, normalise=True):
        err = 100
        bcwt = self.calculate_cwt(weighted=True)
        bcwt = np.nan_to_num(bcwt.values)
        while err >= 0.001:
            cwt = np.zeros((self.lonx.shape[0] - 1, self.latx.shape[0] - 1))
            tau = np.zeros_like(cwt)
            nums = np.zeros_like(cwt)
            for column in self.lat.columns:
                ozo = self.ozone[column]
                num = self.get_density(
                    self.lon[column].values.flatten(),
                    self.lat[column].values.flatten(),
                    density=False,
                )
                tlen = float(len(self.lat[column].values))
                ttau = num / tlen
                tavg = np.sum(bcwt * num / tlen)
                cwt += ttau * ozo * bcwt / tavg
                tau += ttau
                nums += num
            cwt = np.nan_to_num(cwt / tau)
            err = (cwt - bcwt) / bcwt
            err = np.nansum(err)
            bcwt = cwt
        if normalise:
            bcwt = normalize(bcwt)
        bcwt[bcwt == 0] = np.nan
        self.rtwc = self.to_nc(bcwt, name="RTWC")
        return self.rtwc

    def plot_map(self, pscf, boundinglat=-20, axes=[]):
        if len(axes) == 0:
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
            cax = fig.add_axes([0.15, 0.06, 0.7, 0.04])
        else:
            fig, ax, cax = axes
        m = Basemap(
            projection="spstere", lon_0=180, boundinglat=boundinglat, round=True, ax=ax
        )
        data, lonx = addcyclic(pscf.T.values, pscf["Longitude"])
        latx, lonx = np.meshgrid(pscf["Latitude"], lonx)
        lonx, latx = m(lonx, latx)
        if pscf.max().values <= 1:
            h = m.contourf(lonx, latx, data.T, levels=np.arange(0, 1.1, 0.1))
        else:
            levels = np.arange(0, pscf.max(), 2)
            h = m.contourf(lonx, latx, data.T, levels=levels)
        plt.colorbar(h, cax=cax, orientation="horizontal")
        m.drawcoastlines(linewidth=1.5)
        m.drawcountries(linewidth=0.55)
        ax.set_title(self.station, fontweight="bold")
        return fig, ax, m
