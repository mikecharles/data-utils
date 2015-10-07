"""
Contains methods for loading larger amounts of data than a single day

For example, let's say you want to load all of the forecasts valid today's
month and day from all years between 1985 and 2010. This module is intended
to make that much simpler.
"""

import numpy as np
from datetime import datetime
import logging
from .reading import read_grib
from string_utils.strings import replace_vars_in_string


logger = logging.getLogger('root')


def load_ens_fcsts(dates, file_template, data_type, grid, num_members,
                   fhr_range, variable=None, level=None, record_num=None,
                   fhr_int=6, fhr_stat='mean', collapse=False, yrev=False,
                   remove_dup_fhrs=None):
    """
    Loads ensemble forecast data

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
    any of the following supported bracketed variables: {fhr}, {member} -
    these are replaced with the appropriate fhr and member when looping over
    files within the fhr_range and num_members.
    - data_type - *string* - input data type (bin, grib1, grib2)
    - grid - *Grid* - Grid associated with the input data
    - num_members - *int* - number of ensemble members to read int
    - fhr_range - *tuple* - first and last forecast hours to process
    - variable - *string* - variable name (grib only)
    - level - *string* - vertical level that the variable sits at (grib only)
    - record_num - *int* - record to extract (binary only)
    - fhr_int - *int* - interval between forecast hours
    - fhr_stat - *string* - statistic to calculate over the forecast hour
    range (mean [default], sum)
    - collapse - *boolean* - collapse the array so that the ensemble member
    information is summarized (default: False)
    - yrev - *boolean* - whether fcst data is reversed in the y-direction (
    default: False)
    - remove_dup_fhrs - *boolean* (optional) - remove potential duplicate
    fhrs from the grib files - sets the `grep_fhr` parameter to the current
    fhr when calling `read_grib()`,  which greps for the fhr in the given
    grib file - this is useful for gribs that may for some reason have
    duplicate records for a given variable but with different fhrs. This way you
    can get the record for the correct fhr.

    Returns
    -------

    If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
    mean and ensemble spread). For example:

        >>> ens_mean, ens_spread = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP

    If `collapse=False`, a single NumPy array will be returned. For example:

        >>> ens_fcst = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP

    Examples
    --------

    Load ensemble mean and spread from forecasts initialized on a given
    month/day from 1981-2010

        >>> from string_utils.dates import generate_date_list
        >>> from data_utils.gridded.grid import Grid
        >>> from data_utils.gridded.loading import load_obs
        >>> dates = generate_date_list('19810525', '20100525', interval='years')
        >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{'
        ... 'member}.grb'
        >>> data_type = 'grib2'
        >>> grid = Grid('1deg-global')
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> num_members = 11
        >>> fcst_ens_mean, fcst_ens_spread = \  # doctest: +SKIP
        load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
        ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
        ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
        ...            collapse=True)  # doctest: +SKIP
    """
    # --------------------------------------------------------------------------
    # num_members is required
    #
    if not num_members:
        raise ValueError('num_members is required')
    # --------------------------------------------------------------------------
    # variable and level are required for data_type = grib1/grib2
    #
    if data_type in ['grib1', 'grib2']:
        if not (variable and level):
            raise ValueError('variable and level are required for grib data')
    # --------------------------------------------------------------------------
    # Initialize data arrays
    #
    data_f = np.empty((len(range(fhr_range[0], fhr_range[1] + 1, fhr_int)),
                       grid.num_y * grid.num_x)) * np.nan
    # If collapse==True, then we need a temp data_m array to store the
    # separate ensemble members before averaging, and we need mean and spread
    # arrays
    if collapse:
        data_m = np.empty((num_members, grid.num_y * grid.num_x)) * np.nan
        ens_mean = np.empty((len(dates), grid.num_y * grid.num_x)) * np.nan
        ens_spread = np.empty((len(dates), grid.num_y * grid.num_x)) * np.nan
    # If collapse==False, then we need a single data array to store the
    # separate ensemble members
    else:
        data = np.empty((len(dates), num_members, grid.num_y * grid.num_x))
    # --------------------------------------------------------------------------
    # Loop over dates
    #
    for d, date in enumerate(dates):
        logger.debug('Date: {}'.format(date))
        date_obj = datetime.strptime(date, '%Y%m%d')
        # ----------------------------------------------------------------------
        # Loop over members
        #
        for m in range(num_members):
            member = '{:02d}'.format(m)
            logger.debug('  Member: {}'.format(member))
            # ------------------------------------------------------------------
            # Loop over fhr
            #
            for f, fhr in enumerate(range(fhr_range[0], fhr_range[1]+1,
                                          fhr_int)):
                # Grep for the fhr hour in case there are any duplicate grib
                # records (same var, different fhr)
                if remove_dup_fhrs is not None:
                    grep_fhr = ':anl' if fhr == 0 else ':{:d}'.format(fhr)
                else:
                    grep_fhr = None
                fhr = '{:03d}'.format(fhr)
                logger.debug('    Fhr: {}'.format(fhr))
                # --------------------------------------------------------------
                # Convert file template to real file
                #
                file = datetime.strftime(date_obj, file_template)
                var_dict = {'fhr': fhr, 'member': member}
                file = replace_vars_in_string(file, **var_dict)
                # --------------------------------------------------------------
                # Read data file
                #
                # grib1 or grib2
                if data_type in ['grib1', 'grib2']:
                    # Open file and read the appropriate data
                    logger.debug('Loading data from {}...'.format(file))
                    try:
                        # Read in one forecast hour, one member
                        data_f[f] = read_grib(file, data_type, variable,
                                              level, grep_fhr=grep_fhr,
                                              grid=grid, yrev=yrev)
                    except OSError:
                        data_f[f] = np.nan
                elif data_type == 'bin':
                    logger.debug('Loading data from {}...'.format(file))
                    # Open file and read the appropriate data
                    try:
                        # Read in one forecast hour, one member
                        data_f[f] = np.fromfile(file, dtype='float32')
                    except:
                        data_f[f] = np.nan
            # ------------------------------------------------------------------
            # Calculate stat (mean, total) across fhr
            #
            if fhr_stat == 'mean':
                if collapse:
                    if np.all(np.isnan(data_f)):
                        data_m[m] = np.empty(data_f.shape[1]) * np.nan
                    else:
                        data_m[m] = np.nanmean(data_f, axis=0)
                else:
                    if np.all(np.isnan(data_f)):
                        data[d, m] = np.empty(data_f.shape[1]) * np.nan
                    else:
                        data[d, m] = np.nanmean(data_f, axis=0)
            elif fhr_stat == 'sum':
                if collapse:
                    if np.all(np.isnan(data_f)):
                        data_m[m] = np.empty(data_f.shape[1]) * np.nan
                    else:
                        data_m[m] = np.nansum(data_f, axis=0)
                else:
                    if np.all(np.isnan(data_f)):
                        data[d, m] = np.empty(data_f.shape[1]) * np.nan
                    else:
                        data[d, m] = np.nansum(data_f, axis=0)
            else:
                raise ValueError('Supported fhr_stat values: mean, sum')
        # ----------------------------------------------------------------------
        # Calculate ensemble mean and spread (if collapse==True)
        #
        # TODO: Add QCing
        # import pdb ; pdb.set_trace()
        if collapse:
            if np.all(np.isnan(data_m)):
                ens_mean[d] = np.empty(data_m.shape[1]) * np.nan
                ens_spread[d] = np.empty(data_m.shape[1]) * np.nan
            else:
                ens_mean[d] = np.nanmean(data_m, axis=0)
                ens_spread[d] = np.nanstd(data_m, axis=0)

    # --------------------------------------------------------------------------
    # Return the data
    #
    if collapse:
        return ens_mean, ens_spread
    else:
        return data


def load_obs(dates, file_template, data_type, grid, record_num=None):
    """
    Load observation data

    Data is loaded over a given range of dates. The data can be either grib1,
    grib2, or binary. If reading from binary files containing more than one
    record (multiple variables), you can specify the record number
    using the `record_num` parameter.

    Parameters
    ----------

    - dates - *list of strings* - list of dates in YYYYMMDD format
    - file_template - *string* - file template containing date formats and
    bracketed variables. Date formatting (eg. %Y%m%d) will be converted into
    the given date.
    - data_type - *string* - input data type (bin, grib1, grib2)
    - grid - *Grid* - Grid associated with the input data
    - record_num - *int* - binary record containing the desired variable

    Returns
    -------

    *NumPy array* - array of observation data (dates x gridpoint)

    Examples
    --------

    Load observations for a given month/day from 1981-2010

        >>> from string_utils.dates import generate_date_list
        >>> from data_utils.gridded.grid import Grid
        >>> from data_utils.gridded.loading import load_obs
        >>> dates = generate_date_list('19810525', '20100525', interval='years')
        >>> file_tmplt = '/path/to/obs/%Y/%m/%d/tmean_05d_%Y%m%d.bin'
        >>> data_type = 'bin'
        >>> grid = Grid('1deg-global')
        >>> obs_data = load_obs(dates, file_tmplt, data_type, grid) # doctest: +SKIP
    """
    # --------------------------------------------------------------------------
    # Initialize a NumPy array to store the data
    #
    data = np.empty((len(dates), grid.num_y * grid.num_x))
    # --------------------------------------------------------------------------
    # Loop over dates
    #
    for d, date in enumerate(dates):
        logger.debug('Date: {}'.format(date))
        # ----------------------------------------------------------------------
        # Convert file template to real file
        #
        date_obj = datetime.strptime(date, '%Y%m%d')
        file = datetime.strftime(date_obj, file_template)
        # ----------------------------------------------------------------------
        # Open file and read the appropriate data
        #
        logger.debug('Loading data from {}'.format(file))
        try:
            data[d] = np.fromfile(file, 'float32')
        except FileNotFoundError:
            data[d] = np.nan
    # --------------------------------------------------------------------------
    # Return data
    #
    return data
