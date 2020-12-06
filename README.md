# HyTraj

This python library implements [**HYSPLIT**](https://www.arl.noaa.gov/hysplit/hysplit/) based trajectory modeling and analysis. **Will be released as a python package (pip installable) very soon**.

## Work in progress

1. **[HyControl](./hytraj/hycontrol.py):** Generation of control files for parallel trajectory generation afterwards. Generated control files will be divided into a number of temporary folders based on the number of cpus. Each folder will have their own executable to finish the generation tasks faster. 

2. **[HyPlot](./hytraj/hyplot.py):** Collection of functions to plot trajectories.

3. **HyRep:** Representational learning of trajectories for subsequent analysis. (**Wavelet transform done**, *AutoEncoder  (both simple and variational) in progress*.)

4. **[HyCluster](./hytraj/hycluster.py):** Clustering of trajectories (**[Quick Bundle](./hytraj/quick.py), Hierarchical and K-Means clustering done.** Self Organising map (SOM) to be implemented). *It will support different distance metrics for Hierarchical Clustering like **Dynamic time warping (DTW), Edit distance on real sequence (EDR), Longest common subsequences (LCSS) and symmetrized segment-path distance (SSPD)** on completion.*

5. **Multi-sites Receptor Modeling**

6. **GUI:** Medium-term goal 

7. **Bayesian Inversion:** long-term goal

## Implemented (Working)

1. **[HyGen](./hytraj/hygen.py):** Generation of Trajectories using various meteo datasets (**[NCEP and GDAS implemented](https://ready.arl.noaa.gov/archives.php)**).

2. **[HyData](./hytraj/hyread.py):** Reading and binning trajectories data (NetCDF with xarray support).

3. **[HyModel](./hytraj/hymodel.py):** Receptor Modeling (**single site** [weighted](https://www.sciencedirect.com/science/article/abs/pii/S1352231017303898?via%3Dihub) and unweighted **[Concentration weighted Trajectory (CWT), Potential Source Contribution Function (PSCF) and Residence Time Weighted Concentration (RTWC)](https://www.sciencedirect.com/science/article/abs/pii/S1352231002008865?via%3Dihub)**).


**PS:** Find pre-built HYSPLIT executable at [this link](https://github.com/rich-iannone/splitr/tree/master/extras/).