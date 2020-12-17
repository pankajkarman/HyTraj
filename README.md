# HyTraj

This python library implements [**HYSPLIT**](https://www.arl.noaa.gov/hysplit/hysplit/) based trajectory modeling and analysis. 

**Will be released as a python package (pip installable) very soon**.

# Usage

See [this notebook](example3.ipynb) for example usecase.

```python
met_type = "ncep"
dates = pd.date_range("2010-02-01", freq="24H", end="2010-02-10")
hy = HyTraj(stations, height, run_time, working, metdir, outdir, met_type)
data = hy.run(dates, njobs=7)
hy.plot(data["Neumayer"], vertical="alt", show=True)
```

![Example Trajectories](ex.png){width=90%}

## Work in progress

1. **HyRep:** Representational learning of trajectories for subsequent analysis. (**Wavelet transform done**, *AutoEncoder  (both simple and variational) in progress*.)

2. **[HyCluster](./hytraj/hycluster.py):** Clustering of trajectories (**[Quick Bundle](./hytraj/quick.py), Hierarchical and K-Means clustering done.** Self Organising map (SOM) to be implemented). *It will support different distance metrics for Hierarchical Clustering like **Dynamic time warping (DTW), Edit distance on real sequence (EDR), Longest common subsequences (LCSS) and symmetrized segment-path distance (SSPD)** on completion.*

3. **Multi-sites Receptor Modeling**

4. **GUI:** Medium-term goal 

5. **Bayesian Inversion:** long-term goal

## Implemented (Working)

1. **[HyTraj](./hytraj/__init__.py):** Higher level implementation of **Parallel Generation, reading and plotting** of Trajectories (**Recommended**).

2. **[HyGen](./hytraj/hygen.py):** Generation of Trajectories using various meteo datasets (**[NCEP and GDAS implemented](https://ready.arl.noaa.gov/archives.php)**).

3. **[HyControl](./hytraj/hygen.py):** Generation of control files for parallel trajectory generation afterwards. 

4. **[HyParallel](./hytraj/hygen.py):** Parallel generation of trajectories using control files produced using **HyControl**.

5. **[HyData](./hytraj/hyread.py):** Reading and binning trajectories data (NetCDF with xarray support).

6. **[HyReceptor](./hytraj/hymodel.py):** Receptor Modeling (**single site** [weighted](https://www.sciencedirect.com/science/article/abs/pii/S1352231017303898?via%3Dihub) and unweighted **[Concentration weighted Trajectory (CWT), Potential Source Contribution Function (PSCF) and Residence Time Weighted Concentration (RTWC)](https://www.sciencedirect.com/science/article/abs/pii/S1352231002008865?via%3Dihub)**).


**PS:** Find pre-built HYSPLIT executable at [this link](https://github.com/rich-iannone/splitr/tree/master/extras/) and copy executebles to working directory.