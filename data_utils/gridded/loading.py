"""
Containg methods for loading larger amounts of data

For example, let's say you want to load all of the forecasts valid today from
all years between 1985 and 2010. This module is intended to make that much
simpler.
"""

import numpy as np
from datetime import datetime
from .reading import read_grib
from string_utils.strings import replace_vars_in_string


def load_fcsts(dates, file_template, data_type, grid, num_members, fhr_range,
               variable=None, level=None, record_num=None, fhr_int=6,
               fhr_stat='mean'):
    # num_members is required
    if not num_members:
        raise ValueError('num_members is required')
    # Initialize a NumPy array to store the data for all fhrs, one member,
    # one date
    data_temp = np.empty((len(range(fhr_range[0], fhr_range[1]+1, fhr_int)),
                          grid.num_y * grid.num_x))
    # Initialize a NumPy array to store the full data array
    data = np.empty((len(dates), num_members, grid.num_y * grid.num_x))
    # Loop over dates
    for d, date in enumerate(dates):
        # Loop over members
        for m in range(num_members):
            # Loop over fhr
            for f, fhr in enumerate(range(fhr_range[0], fhr_range[1]+1, fhr_int)):
                fhr = '{:03d}'.format(fhr)
                member = '{:02d}'.format(m)
                # Convert file template to real file
                date_obj = datetime.strptime(date, '%Y%m%d')
                file = datetime.strftime(date_obj, file_template)
                var_dict = {'fhr': fhr, 'member': member}
                file = replace_vars_in_string(file, **var_dict)
                # --------------------------------------------------------------
                # grib2 data
                #
                if data_type in ['grib1', 'grib2']:
                    # Open file and read the appropriate data
                    try:
                        # Read in one forecast hour, one member
                        data_temp[f] = read_grib(file, data_type, variable,
                                                    level)
                    except OSError:
                        data_temp[f] = np.nan
            # Calculate stat (mean, total) across fhr
            if fhr_stat == 'mean':
                data[d, m] = np.nanmean(data_temp, axis=0)
            elif fhr_stat == 'sum':
                data[d, m] = np.nansum(data_temp, axis=0)
            else:
                raise ValueError('Supported fhr_stat values: mean, sum')
    # Return the data
    return data


def load_obs(dates, file_template, data_type, grid, record_num=None):
    # Initialize a NumPy array to store the data
    data = np.empty((len(dates), grid.num_y * grid.num_x))
    # Loop over dates
    for d, date in enumerate(dates):
        # Convert file template to real file
        date_obj = datetime.strptime(date, '%Y%m%d')
        file = datetime.strftime(date_obj, file_template)
        # Open file and read the appropriate data
        try:
            data[d] = np.fromfile(file, 'float32')
        except FileNotFoundError:
            data[d] = np.nan
    # Return data
    return data
