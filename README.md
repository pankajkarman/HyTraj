# HyTraj

This python library implements HySPLIT based trajectory modeling and analysis.

# Goals

1. **[HyGen](./hytraj/hygen.py):** Generation of Trajectories using various meteo datasets (**NCEP and GDAS implemented**).
2. **[HyControl](./hytraj/hycontrol.py):** Generation of control files for parallel trajectory generation afterwards. Generated control files will be divided into a number of temporary folders based on the number of cpus. Each folder will have their own executable to finish the generation tasks faster. ** Implemented**.

3. **[HyData](./hytraj/hyread.py):** Reading and binning trajectories data (in NetCDF format with xarray support).** Implemented**.

4. **[HyPlot](./hytraj/hyplot.py):** Collection of functions to plot trajectories. ** Implemented**.

5. **HyRep:** Representational learning of trajectories for subsequent analysis. (**Wavelet transform done**, *AutoEncoder  (both simple and variational) in progress*.)

6. **[HyCluster](./hytraj/hycluster.py):** Clustering of trajectories (**[Quick Bundle](./hytraj/quick.py), Hierarchical and K-Means clustering done.** Self Organising map (SOM) to be implemented). *It will support different distance metrics for Hierarchical Clustering like **Dynamic time warping (DTW), Edit distance on real sequence (EDR), Longest common subsequences (LCSS) and symmetrized segment-path distance (SSPD)** on completion.*

7. **[HyModel](./hytraj/hymodel.py):** Receptor Modeling (includes both single and multi-sites based weighted and unweighted **CWT, PSCF and RWTC**). ** Implemented**. 

8. **Bayesian Inversion:** To be implemented (long-term goal).

9. **GUI:** To be implemented (Medium-term goal).

**Note:** The repository contains scripts implementing the above mentioned methods for Antarctic region at the moment. *Work on general purpose scripts in progress.* Will be released as a python package (pip installable) very soon.