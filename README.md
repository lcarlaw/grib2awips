# grib2awips

The contained code will allow a user to alter model run dates of archived data [NAM, GFS, and RAP GRIB2 data is presently supported], limit model data to a specified domain, and change the "process ID" contained in the GRIB2 files to avoid accidentally overwritting operational, real-world model data in the AWIPS2 system. 

## AN IMPORTANT NOTE BEFORE PUSHING DATA ONTO YOUR AWIPS SYSTEM

All GRIB2 files begin with metadata describing many things, among which include the "Originating/Generating Center", "Originating/Generating Subcenter", and the "ProcessID." In its present form, data output by running this script will leave the Center and Subcenter IDs untouched (for the supported files, these will always be 7 and 0, respectively), but will prompt the user to alter the ProcessID, in an effort to "trick" AWIPS into properly decoding the file to avoid inadvertent overwriting real-world operational model/analysis data. The current list of officially supported ProcessIDs can be found [here](http://www.nco.ncep.noaa.gov/pmb/docs/on388/tablea.html). 

The documentation recommends starting with a processID of 240 and working upwards to 255, which are currently "Reserved" or "Missing" products. However, it's possible that your local office utilizes local model data, or some other product with these processIDs, so it's important to check with your ITO, or someone knowledgeable about the AWIPS system to avoid potentially overwriting or corrupting real-world data. 

## Prerequisites

You'll need a few things installed before running the convert.py script:
* [wgrib2](http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/) - You can download the latest .tar file [here](http://www.ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/)
* Python2.7 - This code was developed on a machine with Python2.7 installed via [Anaconda](https://anaconda.org/anaconda/python)

## Useage

We'll run through an example on how to use the scripts here:

### Data 

We've downloaded several archived NAM model runs from the NCEI website. Typing the following:

```
cd /Volumes/External2TB/data/
ls -ltr
```

results in this output:

```
nam_218_2011022200.g2.tar
nam_218_2011022300.g2.tar
nam_218_2011022400.g2.tar
nam_218_2011022500.g2.tar
nam_218_2011022600.g2.tar
```

This is GRIB2 data (the **g2** extension before .tar), so we can decode these files. Note that GRIB1 files are not supported at this time. Don't rename any files as the converting script looks for a specific naming convention. 

Archived NAM files actually contain hourly forecast output through 36 hours, which is too bulky for any uses we have here. The **reduce_nam.py** script will delete the hourly data and re-package the file with 3-hourly forecast output. If we type:

```
python reduce_nam.py /Volumes/External2TB/data
```


