  
  
PyHRMS: Tools For working with High Resolution Mass Spectrometry (HRMS) data in Environmental Science  
=====================================================================================================
  
  
PyHRMS is a python package for processing  high resolution Mass Spectrometry data coupled with gas  
chromatogram (GC) or liquid chromatogram (LC).  
  
It aims to provide user friendly tool to read,  process and visualize LC/GC-HRMS data for  scientist.
  
Contributers: Rui Wang  
======================
Release date: Nov.15.2021  
  
Update
======
Feb.27.2022: pyhrms 0.3.1 new features:

    * Optimized some small functions



Installation & major dependencies  
pyhrms can be installed and import as following:  
  
```
pip install pyhrms  
```

If you just want to update a new version, please update as following:

```
pip install pyhrms -U
```



pyhrms requires major dependencies: 
===================================
  
* numpy>=1.19.2  
  
* pandas>1.3.3  
  
* matplotlib>=3.3.2  
  
* pymzml>=2.4.7  
  
* scipy>=1.6.2  
  
* numba>=0.53.1  
  
* molmass>=2021.6.18

* tqdm >= 4.62.3
  
  
  
Features 
========
PyHRMS provides following functions:  
  
* Read raw LC/GC-HRMS data in mzML format;  
* Powerful and accurate peak picking function for LC/GC HRMS;  
* retention time (rt) and mass over Z stands for charge number of ions (m/z) will be aligned based on user defined error range.  
* Accurate function for comparing response between/among two or more samples;  
* Covert profile data to centroid  
* Parallel computing to improve efficiency;  
* Interactive visualizations of raw mzML data;  
* Supporting searching for Local database and massbank;  
* MS quality evaluation for ms data in profile.  
  
  
Licensing
=========
  
The package is open source and can be utilized under MIT license. Please find the detail in licence file.
