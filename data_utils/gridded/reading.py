"""
Contains methods for reading gridded data.
"""

import subprocess
import shlex
import uuid
import os

import numpy


def read_grib(file, grib_type, variable, level):
    """Reads a record from a grib file

    Uses wgrib to convert a record to a temporary binary file, then reads that
    file in, and removes the temporary file.

    A grib record string will be constructed using the arguments provide. For
    example:



    Parameters
    ----------
    file : string
        Name of the grib file to read from
    grib_type : string
        Type of grib file ('grib1', 'grib2')
    variable : string
        Name of the variable in the grib record (ex. TMP, UGRD, etc.)
    level : string
        Name of the level (ex. '2 m above ground', '850 mb', etc.)

    Returns
    -------
    data : array_like
        A data array

    Raises
    ------
    IOError
        If wgrib has a problem reading the grib and/or writing the temp file
    Exception
        If no grib record is found

    Examples
    --------

    >>> import data_utils.gridded.reading
    >>>
    >>> file = 'gefs_20140101_00z_f036_m05.grb2'
    >>> grib_type = 'grib2'
    >>> variable = 'TMP'
    >>> level = '2 m above ground'
    >>> data = data_utils.gridded.reading.read_grib(file, grib_type, variable, level)
    >>> data.shape
    (65160,)
    >>> data
    array([ 246.3999939 ,  246.3999939 ,  246.3999939 , ...,  242.74000549,
            242.74000549,  242.74000549], dtype=float32)
    """
    # Generate a temporary file name
    temp_file = str(uuid.uuid4()) + '.bin'
    # Set the name of the wgrib program to call
    if grib_type == 'grib1':
        wgrib_call = 'wgrib "{}" | grep "{}" | grep "{}" | wgrib -i "{}" -nh ' \
                     '-bin -o "{}"'.format(file, variable, level, temp_file)
    elif grib_type == 'grib2':
        wgrib_call = 'wgrib2 "{}" -match "{}" -match "{}" -order we:sn ' \
                     '-no_header -bin "{}"'.format(file, variable, level,
                                                   temp_file)
    else:
        raise IOError(__name__ + ' requires grib_type to be grib1 or grib2')
    # Generate a wgrib call
    try:
        output = subprocess.check_output(shlex.split(wgrib_call))
    except Exception as e:
        raise IOError('Couldn\'t read {} file: {}'.format(grib_type, str(e)))
    # Read in the binary data
    data = numpy.fromfile(temp_file, dtype=numpy.float32)
    if data.size == 0:
        raise Exception('No grib record found')
    # Delete the temporary file
    os.remove(temp_file)
    # Return data
    return data