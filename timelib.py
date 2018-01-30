#!/usr/bin/env python

import time, calendar

"""
timelib.py

This script contains frequently called functions relating to time conversions.
"""

def date2epoch(dateStr):
    """ 
    Convert a datestring of the form YYYYMMDDHH to seconds since epoch,
    where YYYY 4-digit year, MM is 2-digit month, DD is 2-digit day, and HH is
    2-digit hour
    """
    epoch_seconds = calendar.timegm(time.strptime(dateStr, '%Y%m%d%H'))
    return epoch_seconds

def epoch2date(epochSeconds):
    """
    Convert seconds since epoch to a formatted date string
    YYYYMMDDHH where YYYY 4-digit year, MM is 2-digit month, DD is 2-digit
    day, and HH is 2-digit hour
    """

    dateStr = time.strftime('%Y%m%d%H', time.gmtime(epochSeconds))
    return dateStr
