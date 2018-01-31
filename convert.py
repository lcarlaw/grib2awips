#!/usr/bin/env python

###############################################################################
#
# This script allows a user to artifically change the dates of archived model
# data (NAM, GFS, and RAP GRIB2 data is currently supported). The archived
# data (in .tar form) should be downloaded from the NCEI website:
# (https://www.ncdc.noaa.gov/data-access/model-data/model-datasets) and placed
# in a directory. 
#
# This script will then accept several command-line arguments, which will
# determine what model to decode, how to subset the domain to reduce data size,
# and what processID to assign the new GRIB data to "trick" AWIPS into 
# thinking this is real data. This will loop through all files in the specified
# directory of the same model type. 
#
# To see documentation on command-line arguments, type: python convert.py --help
# 
# An example to convert nam data is shown below:
# 
# python convert.py -m nam -pid 250 -path Documents/FWD/data -shifttime 2503 
# -d -minlat 27 -maxlat 40 -minlon -108 -maxlon -94
#
# Requires wgrib2 to be accessible from the command-line. 
#
###############################################################################

import os, sys
import argparse
from glob import glob
import timelib

#...Input command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-path', action='store', dest='path',
                    help='PATH to archived NCEI data files')

parser.add_argument('-m', action='store', dest='model_name',
                    help='Model Name. Acceptable values are [rap|ruc2|nam|gfs]')

parser.add_argument('-d', action='store_true', default=False,
                    dest='domain_switch', 
                    help='Limited domain boolean. Set -d for limited area')

parser.add_argument('-minlat', action='store', dest='min_lat', 
                    help='Minimum latitude in degrees N')

parser.add_argument('-maxlat', action='store', dest='max_lat', 
                    help='Maximum latitude in degrees N')

parser.add_argument('-minlon', action='store', dest='min_lon', 
                    help='Minimum longitude in degrees E (- for W)')

parser.add_argument('-maxlon', action='store', dest='max_lon', 
                    help='Maximum longitude in degrees E (- for W)')

parser.add_argument('-pid', action='store', dest='process_id',
                    help='Set the processid. Good values are 240-255')

parser.add_argument('-shifttime', action='store', dest='delta',
                    help='Number of days to add to archived data')

results = parser.parse_args()

#...Catch the bad arguments...
# Path specification
if results.path == None:
    print 'We need a path to the data files. Point us in the right direction.'
    sys.exit()

# Supported models. Sorry, no ECMWF. 
if results.model_name not in ['rap', 'ruc2', 'nam', 'gfs']:
    print 'Bad, or no model name.'
    sys.exit()

# Control the processid here
results.process_id = int(results.process_id)
if results.process_id < 240 or results.process_id > 255:
    print 'Choose a higher processID. Could interfere with real AWIPS data...'
    sys.exit()

# If user specified a limited domain, they need a set of bounding lat/lons
if results.domain_switch and (results.min_lat==None or results.max_lat==None
                            or results.min_lon==None or results.max_lon==None):
    print 'User wants a smaller domain, but did not specify bounding values'
    sys.exit()

if results.delta == None:
    results.delta = 0

#...Loop through data directory to find these model files
# Look for all files with the model_name prefix in the data directory
file_list = glob(results.path + '/' + results.model_name + '*.tar')
print file_list

for f in file_list:
    
    # First determine if these are grib1 or grib2 messages. NCEI tar files
    # with a .g2. extension will be in grib2 data format. 
    res = f.find('.g2.')
    if res > -1:
        ftype = 'grib2'
    else:
        ftype = 'grib1'
        print 'GRIB1 file type not supported at this time.'
        sys.exit()

    if results.domain_switch:
        limit = '-small_grib ' + results.min_lon + ':' + results.max_lon + \
                ' ' + results.min_lat + ':' + results.max_lat
    else:
        limit = '-GRIB '
       
    # Grab the model run date from the file name. NCEI archives data in the
    # form: MMM_GRID_YYYYMMDDHH.XX.tar where MMM is the model name, GRID is
    # the grid number, and XX is g2 (for grib2) or nothing (for grib1). All
    # we need is to find the last occurrence of the '_' character and search
    # for the next 8 characters.
    idx = f.rfind(results.model_name + '_')
    date_string = f[idx+8:idx+18]
    
    # Add the specified time delta to the model run 
    epoch = timelib.date2epoch(date_string)
    epoch = epoch + int(results.delta)*86400
    new_date = timelib.epoch2date(epoch)
    
    year = new_date[0:4]
    month = new_date[4:6]
    day = new_date[6:8]
    hour = new_date[8:10]
    
    #arg = 'cdo -settaxis,'+year+'-'+month+'-'+day+','+hour + ':00,3hour' 
    arg = 'wgrib2 ' + f + ' -set_date ' + new_date + '00  -set '+ \
          'center 7 -set subcenter 0 -set analysis_or_forecast_process_id ' + \
          str(results.process_id) + ' ' + limit + ' ' + \
          results.path + '/' + 'LDAD-GRIB-' + results.model_name + '-' +  \
          new_date + '.grb2'
    
    os.system(arg)

