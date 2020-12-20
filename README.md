# HyTraj

This python library implements [**HYSPLIT**](https://www.arl.noaa.gov/hysplit/hysplit/) based trajectory modeling and analysis. 

## Installation

### Install using pip:

```bash
pip install git+https://github.com/pankajkarman/HyTraj.git
```
### To install from source, first clone this repo and install using:

```bash
make install
```

### Install in a conda virtual environment:

```bash
make conda
```

## Usage

See [this notebook](example3.ipynb) for example usecase.

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
![Example Trajectories](ex.png)

### Cluster Trajectories

```python
from hytraj import HyCluster

labels = HyCluster(data).fit(kmax=10, method='KMeans')

```

### Perform Receptor Modeling

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

## Features

1. **[HyTraj](./hytraj/__init__.py):** Higher level implementation of **Parallel Generation, reading and plotting** of Trajectories (**Recommended**).

2. **[HyGen](./hytraj/hygen.py):** Generation of Trajectories using various meteo datasets (**[NCEP and GDAS implemented](https://ready.arl.noaa.gov/archives.php)**).

3. **[HyControl](./hytraj/hygen.py):** Generation of control files for parallel trajectory generation afterwards. 

4. **[HyParallel](./hytraj/hygen.py):** Parallel generation of trajectories using control files produced using **HyControl**.

5. **[HyData](./hytraj/hyread.py):** Reading and binning trajectories data (NetCDF with xarray support).

6. **[HyCluster](./hytraj/hycluster.py):** Clustering of trajectories with KMeans using wavelet features.

6. **[HyReceptor](./hytraj/hymodel.py):** [Single site Receptor Modeling](https://www.sciencedirect.com/science/article/abs/pii/S1352231002008865?via%3Dihub) ( both [weighted](https://www.sciencedirect.com/science/article/abs/pii/S1352231017303898?via%3Dihub) and unweighted):
    - Concentration weighted Trajectory (CWT)
    - Potential Source Contribution Function (PSCF) 
    - Residence Time Weighted Concentration (RTWC)

## To do

1. **GUI:** Medium-term goal 

2. **Bayesian Inversion:** long-term goal


**PS:** Find **pre-built HYSPLIT executable** at [this link](https://github.com/rich-iannone/splitr/tree/master/extras/) and copy **executeble** to working directory.
