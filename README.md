# grib2awips

The contained code will allow a user to alter model run dates of archived data [NAM, GFS, and RAP GRIB2 data is presently supported], limit model data to a specified domain, and change the "process ID" contained in the GRIB2 files to avoid accidentally overwritting operational, real-world model data in the AWIPS2 system. 

Currently, only GRIB2 files are supported. 

## AN IMPORTANT NOTE BEFORE PUSHING DATA ONTO YOUR AWIPS SYSTEM

All GRIB2 files begin with metadata describing many things, among which include the "Originating/Generating Center", "Originating/Generating Subcenter", and the "ProcessID." In its present form, data output by running this script will leave the Center and Subcenter IDs untouched (for the supported files, these will always be 7 and 0, respectively), but will prompt the user to alter the ProcessID, in an effort to "trick" AWIPS into properly decoding the file to avoid inadvertently overwriting real-world operational model/analysis data. The current list of officially supported ProcessIDs can be found [here](http://www.nco.ncep.noaa.gov/pmb/docs/on388/tablea.html). 

The documentation recommends starting with a processID of 240 and working upwards to 255, which are currently "Reserved" or "Missing" products. However, it's possible that your local office utilizes local model data, or some other product with these processIDs, so it's important to check with your ITO, or someone knowledgeable about the AWIPS system to avoid potentially overwriting or corrupting real-world data. 

Once your data has been decoded and output, (it will be called something like LDAD-GRIB-foobar.grb2), you may want to run a command something like:

```
wgrib2 LDAD-GRIB-foobar.grb2 -processid > output.txt
```

Read the output.txt file to ensure that all of the parameters in the GRIB file show a **forecast generating process** number equal to the pid you set during the conversion.  

Finally, it's probably also a good idea to monitor some of the real-world NAM/GFS/RAP data coming into AWIPS to ensure there are no inventory hiccups. The AWIPS system should keep your archived data separate from the operational data flow with the altered processid if all has gone well, however. 

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
nam_218_2017050100.g2.tar
nam_218_2017050200.g2.tar
```

This is GRIB2 data (the **g2** extension before .tar), so we can decode these files. Note that GRIB1 files are not supported at this time. Don't rename any files as the converting script looks for a specific naming convention. 

Archived NAM files actually contain hourly forecast output through 36 hours, which is too bulky for any uses we have here. The **reduce_nam.py** script will delete the hourly data and re-package the file with 3-hourly forecast output. If we type:

```
python reduce_nam.py /Volumes/External2TB/data
```

the extraneous data will be removed from the data files. 

### Conversion Process

Running the conversion script is fairly straightforward, but requires a few command-line inputs:

```
python convert.py -m nam -pid 250 -path /Volumes/External2TB/data -shifttime 365 -d -minlat 27 -maxlat 40 -minlon -108 -maxlon -94
```

In this example, the convert.py script is being told to look for NAM data, assign a process ID of 250 to the output files, limit the output to a domain between 27 and 40 degrees N, and 108 to 94 degrees W, and to shift the valid dates and times ahead by 365 days.

Once this script finishes running (this will take some time...these files are pretty big!), two new files are present in the **/Volumes/External2TB/data** directory:

```
LDAD-GRIB-nam-2018050100.grb2
LDAD-GRIB-nam-2018050200.grb2
```

These files can now be loaded into AWIPS.

### Transferring data into AWIPS2

1. Once these files are transferred onto the AWIPS system, open up a terminal window and type:
```
ssh dx3
```
A standard WARNING message will appear. 

2. Move or copy your files in **/awips2/edex/data/manual.** For example, if your files are located in **/tmp**, you can type:

```
mv /tmp/LDAD-GRIB-nam* /awips2/edex/data/manual
```

3. Within a few seconds, this file should be swept up out of manual ingest and will no longer appear in **/awips2/edex/data/manual.** If you'd like to check the status of the decoding, you can type:

```
grep LDAD-GRIB-nam* /awips2/edex/logs/edex-ingestGrib-YYYYMMDD.log
```
where YYYYMMDD correspond to the current Year, Month, and Day. Each line of text will correspond to a particular record from the GRIB2 file being decoded into the **/data_store** directory. 

4. Type:
```
ssh dx2
cd /awips2/edex/data/hdf5/grid
ls -ltr
```

In this example, we should see a new directory called **GribModel:7:0:250.** This will contain new HDF5 files, which the AWIPS2 system will use to display data in CAVE. 

### Displaying data in CAVE

1. Open up a CAVE perspective and navigate to **CAVE > Data Browsers > Product Browsers** to reveal the Produce Browser Window. 

2. Scroll down and look for the **GribModel:7:0:250** entry. Expand the entry by clicking the triangle on the left. Various fields can be displayed by nagivating through various levels and parameters, which won't be discussed here. 

### Making data available through the Volume Browser

Since individually selecting fields through the Product Browser is difficult, and certain routine fields used by forecasters are computed "on-the-fly" in AWIPS, making the data viewable through the Volume Browser is helpful. 

1. In the Localization window (click the symbol off to the right of the Warngen button with a little plus in the top right and click "Localization."

2. Navigate to **D2D > Volume Browser > VbSources > Local**

3. Right click on **SITE (WFO)**, and select ***Copy To > User (username)***. We'll edit this file first to make sure it works, and then copy over to SITE later. 

4. Double click the new file and display the source code (lower left tab next to "Design"). 

5. Insert the following lines:

```
<?xml version=’1.0’ encoding=’UTF-8’?>
<vbSourceList>
<vbSource category=”Local” key=”GribModel:7:0:250” />
<vbSourceList>
```

Add additional <vbSource.../> lines for each additional model/processID you have. 

6. Save and restart your CAVE. A **GribModel:7:0:255** selection should be available in the Volume Browser under the Local Sources dropdown. 

7. Once you're happy with the results, copy the file to SITE so everyone has access. 

An added bonus of making data available in the Volume Browser is that users will also be able to display sounding data in NSHARP from the GribModel output. 

### Clearing the model data inventory

As you import newer model runs, AWIPS will automatically update the available model inventory, eventually overwriting older model runs. Should you need to start over and clear the inventory out, or see older model data, follow these steps. This will require AWIPS user privileges. 

1. In a terminal window, type (carefully!):

```
psql metadata
delete from grid where info_id in (select id from grid_info where datasetid = ‘GribModel:7:0:250’) and reftime < ‘2018-02-01’;
```

This will purge the inventory for our model data before the specified reference time. 
2. Next, we'll need to delete the HDF5 files. Type:

```
ssh dx2
cd /awips2/edex/data/hdf5/grid
ls -ltr
```

You should see **GribModel:7:0:250**. Remove this directory and everything within it (carefully!):

```
rm -rf GribModel:7:0:250
```


