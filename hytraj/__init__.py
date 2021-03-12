"""
This python library implements [**HySPLIT**](https://www.arl.noaa.gov/hysplit/hysplit/) based trajectory modeling and analysis. 

## Installation

### Install using pip:

```bash
pip install hytraj
```
or

```bash
pip install git+https://github.com/pankajkarman/HyTraj.git
```

## Dependencies

1. Plotting requires [Basemap](https://anaconda.org/anaconda/basemap).

2. Hierarchical clustering requires [traj_dist](https://github.com/djjavo/traj-dist/tree/master/traj_dist).

## Usage

```python
import hytraj as ht
```

### Generate Trajectories

```python
from hytraj import HyTraj

met_type = "ncep"
dates = pd.date_range("2010-02-01", freq="24H", end="2010-02-10")
hy = HyTraj(stations, height, run_time, working, metdir, outdir, met_type)
data = hy.run(dates, njobs=7)
hy.plot(data["Neumayer"], vertical="alt", show=True)
```
### Cluster Trajectories

#### KMeans Clustering using wavelet features

```python
from hytraj import HyCluster

labels = HyCluster(data).fit(kmax=10, method='KMeans')
```

#### Hierarchical Agglomerative Clustering (HAC)

```python
from hytraj import HyHAC

trj = HyHAC(data)
labels = trj.fit(nclus=4, metric='sspd')
trj.plot_dendrogram()
```
### Receptor Modeling

```python
from hytraj import HyReceptor, HyData

station = 'South Pole'
data = HyData(files, stations).read()[station]
model = HyReceptor(ozone, data, station_name="South Pole")
cwt = model.calculate_cwt(weighted=False)
pscf = model.calculate_pscf(thresh=0.95)
rtwc = model.calculate_rtwc(normalise=True)
model.plot_map(rtwc, boundinglat=-25)
```
"""


import os, glob
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from shutil import copyfile, copy2, rmtree
from mpl_toolkits.basemap import Basemap, addcyclic, cm


from .hygen import HyGen, HyControl, HyParallel
from .hyread import HyData
from .hymodel import HyReceptor
from .hycluster import HyCluster
from .hyagg import HyHAC
from .hyplot import ClusterPlot


class HyTraj:
    def __init__(
        self, locations, height, run_time, working, metdir, outdir, met_type="ncep"
    ):

        self.run_time = run_time
        self.height = height
        self.stations = list(locations.keys())
        self.locations = locations
        self.workpath = working
        self.metdir = metdir
        self.met_type = met_type
        self.outdir = outdir
        self.exe = self.workpath + "hyts_std"

    def run(self, dates, vertical=0, model_top=10000.0, njobs=1):
        self.dates = dates
        cdir = self.outdir + "ctrl/"
        # print(cdir)
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        hy = HyControl(
            self.locations,
            self.height,
            self.run_time,
            self.workpath,
            self.metdir,
            self.outdir,
            self.met_type,
            self.exe,
        ).run(self.dates, vertical, model_top, cdir)

        cfiles = glob.glob(cdir + "*")
        # print(cfiles)
        hy = HyParallel(cfiles, njobs, self.outdir + "/test", self.workpath).run()
        rmtree(cdir)

        files = sorted(glob.glob(self.outdir + "*"))
        data = HyData(files, list(self.locations.keys())).read()
        return data

    @staticmethod
    def plot(
        ds,
        vertical="pre",
        grid={"height_ratios": [2.1, 1.25]},
        pad=dict(wspace=0, hspace=0, left=0.06, bottom=0.09, right=0.9, top=0.99),
        proj=dict(projection="robin", lon_0=0, boundinglat=-60),
        show=True,
    ):
        fig, axes = plt.subplots(2, 1, figsize=(10, 11), gridspec_kw=grid)

        ax = axes[1]
        ax.set_xlabel("Step [hr]")
        df = ds.sel(geo=vertical).squeeze().to_pandas()
        for col in df.columns:
            ax.plot(df.index, df[col], color="grey", lw=3, alpha=0.4)
        ax.minorticks_on()
        if vertical == "alt":
            ax.set_ylabel("Altitude [m]")
        else:
            ax.set_ylabel("Pressure [hPa]")
            ax.invert_yaxis()

        ax = axes[0]
        m = Basemap(**proj, ax=ax)
        m.drawcoastlines(linewidth=0.6)
        m.drawcountries(linewidth=0.6)
        for i in np.arange(len(ds.time)):
            df = ds.sel(geo=["lat", "lon"]).isel(time=i).to_pandas().T
            xx, yy = m(df["lon"].values, df["lat"].values)
            m.plot(xx, yy, color="grey", lw=3)
        fig.subplots_adjust(**pad)
        if show:
            plt.show()
