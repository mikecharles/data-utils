"""
Containg methods for loading larger amounts of data

For example, let's say you want to load all of the forecasts valid today from
all years between 1985 and 2010. This module is intended to make that much
simpler.
"""

import numpy as np
from datetime import datetime
import logging
from .reading import read_grib
from string_utils.strings import replace_vars_in_string


logger = logging.getLogger(__name__)

def load_ens_fcsts(dates, file_template, data_type, grid, num_members,
                   fhr_range, variable=None, level=None, record_num=None,
                   fhr_int=6, fhr_stat='mean', collapse=False):
    """
    Load ensemble forecast data

    Data is loaded over a given range of dates, forecast hours, and ensemble
    members. If collapse==True, then the information retrieved is collapsed
    into an object containing the following information:

        - Ensemble mean (dates, x * y)
        - Ensemble spread (dates, x * y)

    If collapse==False, then the object returned will contain a single array
    with all the members in tact (dates, members, x * y)

    Parameters
    ----------

    - dates - *list of strings* - list of dates in YYYYMMDD format
    - file_template - *string* - file template containing date formats and
    bracketed variables
    - data_type
    - grid
    - num_members
    - fhr_range
    - variable
    - level
    - record_num
    - fhr_int
    - fhr_stat
    - collapse - *boolean* - collapse the array so that the ensemble member
    information is summarized (default: False)


    """
    # num_members is required
    if not num_members:
        raise ValueError('num_members is required')
    # Initialize data arrays
    data_f = np.empty((len(range(fhr_range[0], fhr_range[1] + 1, fhr_int)),
                       grid.num_y * grid.num_x))
    if collapse:
        data_m = np.empty((num_members, grid.num_y * grid.num_x))
        ens_mean = np.empty((len(dates), grid.num_y * grid.num_x))
        ens_spread = np.empty((len(dates), grid.num_y * grid.num_x))
    else:
        data = np.empty((len(dates), num_members, grid.num_y * grid.num_x))
    # Loop over dates
    for d, date in enumerate(dates):
        logger.debug('Date: {}'.format(date))
        date_obj = datetime.strptime(date, '%Y%m%d')
        # Loop over members
        for m in range(num_members):
            member = '{:02d}'.format(m)
            logger.debug('  Member: {}'.format(member))
            # Loop over fhr
            for f, fhr in enumerate(range(fhr_range[0], fhr_range[1]+1, fhr_int)):
                fhr = '{:03d}'.format(fhr)
                logger.debug('    Fhr: {}'.format(fhr))
                # Convert file template to real file
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
                        data_f[f] = read_grib(file, data_type, variable,
                                                    level)
                    except OSError:
                        data_f[f] = np.nan
            # Calculate stat (mean, total) across fhr
            if fhr_stat == 'mean':
                if collapse:
                    data_m[m] = np.nanmean(data_f, axis=0)
                else:
                    data[d, m] = np.nanmean(data_f, axis=0)
            elif fhr_stat == 'sum':
                if collapse:
                    data_m[m] = np.nansum(data_f, axis=0)
                else:
                    data[d, m] = np.nansum(data_f, axis=0)
            else:
                raise ValueError('Supported fhr_stat values: mean, sum')
        # Calculate ensemble mean and spread (if collapse==True)
        # TODO: Add QCing
        if collapse:
            ens_mean[d] = np.nanmean(data_m, axis=0)
            ens_spread[d] = np.nanstd(data_m, axis=0)

    # Return the data
    if collapse:
        return ens_mean, ens_spread
    else:
        return data


def load_obs(dates, file_template, data_type, grid, record_num=None):
    # Initialize a NumPy array to store the data
    data = np.empty((len(dates), grid.num_y * grid.num_x))
    # Loop over dates
    for d, date in enumerate(dates):
        logger.debug('Loading data from {}'.format(date))
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
