#!/usr/bin/env python

# Place this file in the directory containing the archived .tar files from 
# NCEI. NAM data is available every hour during the first 36 hours of the
# forecast. This is too much data, and makes the GRIB files a bit too bulky. 
# This script will maintain every 3 forecast hours and re-tar the file together.

from glob import glob
import os
import numpy as np

save_hours = np.arange(0, 87, 3)
file_list = glob('./nam*.tar')
for file_ in file_list:
    
    #...Untar the file
    print 'Untarring ' + file_
    arg = 'tar -xvf ' + file_
    os.system(arg)

    #...Grab all of the individual files. Delete the off-3hourly files
    new_list = glob('./nam*.grb2')
    for new_file in new_list:
        if int(new_file[-8:-5]) not in save_hours:
            arg = 'rm ' + new_file
            print 'deleting ' + new_file
            os.system(arg)
    final_list = glob('./nam*.grb2')

    # Concatenate these back into a tar file
    arg = 'arr=(); for i in nam*.grb2; do arr+=(${i}); done; cat ${arr[@]} >' + \
          file_ 
    os.system(arg)  

    # Remove the individual grib2 files
    for i in final_list:
        'Deleting ' + i
        arg = 'rm ' + i
        os.system(arg)
