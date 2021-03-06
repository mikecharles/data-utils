"""
Contains methods for reading gridded data.
"""

import subprocess
import shlex
import uuid
import os

import numpy

from data_utils.gridded.grid import Grid


def read_grib(file, grib_type, variable, level, grid=None, yrev=False,
              grep_fhr=None, debug=False):
    """
    Reads a record from a grib file

    Uses wgrib to convert a record to a temporary binary file, then reads that
    file in, and removes the temporary file.

    A grib record string will be constructed using the arguments provide. For
    example:

    Parameters
    ----------

    - file (string)
        - Name of the grib file to read from
    - grib_type (string)
        - Type of grib file ('grib1', 'grib2')
    - variable (string)
        - Name of the variable in the grib record (ex. TMP, UGRD, etc.)
    - level (string)
        - Name of the level (ex. '2 m above ground', '850 mb', etc.)
    - grid (Grid)
        - Grid object the data is defined on
    - yrev (optional)
        - Option to flip the data in the y-direction
    - grep_fhr (optional)
        - fhr to grep grib file for - this is useful for gribs that may for
        some reason have duplicate records for a given variable but with
        different fhrs. This way you can get the record for the correct fhr.

    Returns
    -------
    - (array_like)
        - A data array

    Raises
    ------
    - IOError
        - If wgrib has a problem reading the grib and/or writing the temp file
    - IOError
        - If no grib record is found

    Examples
    --------

        #!/usr/bin/env python
        >>> from data_utils.gridded.reading import read_grib
        >>> from pkg_resources import resource_filename
        >>> file = resource_filename('data_utils',
        ... 'lib/example-tmean-fcst.grb2')
        >>> grib_type = 'grib2'
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> data = read_grib(file, grib_type, variable, level)
        >>> data.shape
        (65160,)
        >>> data
        array([ 248.77000427,  248.77000427,  248.77000427, ...,  241.86000061,
                241.86000061,  241.86000061], dtype=float32)
    """
    # Make sure grib file exists first
    if not os.path.isfile(file):
        raise IOError('Grib file not found')
    # Generate a temporary file name
    temp_file = str(uuid.uuid4()) + '.bin'
    # Set the grep_fhr string
    if grep_fhr:
        grep_fhr_str = grep_fhr
    else:
        grep_fhr_str = '.*'
    # Set the name of the wgrib program to call
    if grib_type == 'grib1':
        wgrib_call = 'wgrib "{}" | grep ":{}:" | grep ":{}:" | grep -P "{}" | wgrib ' \
                     '-i "{}" -nh -bin -o "{}"'.format(file, variable, level,
                                           grep_fhr_str, file, temp_file)
    elif grib_type == 'grib2':
        # Note that the binary data is written to stdout
        wgrib_call = 'wgrib2 "{}" -match "{}" -match "{}" -match "{}" -end ' \
                     '-order we:sn -no_header -inv /dev/null -bin -'.format(
            file, variable, level, grep_fhr_str)
    else:
        raise IOError(__name__ + ' requires grib_type to be grib1 or grib2')
    if debug:
        print('wgrib command: {}'.format(wgrib_call))
    # Generate a wgrib call
    try:
        if grib_type == 'grib1':
            output = subprocess.call(wgrib_call, shell=True,
                                     stderr=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL)
        else:
            proc = subprocess.Popen(wgrib_call, shell=True,
                                      stderr=subprocess.DEVNULL,
                                      stdout=subprocess.PIPE)
    except Exception as e:
        if grib_type == 'grib1':
            os.remove(temp_file)
        raise IOError('Couldn\'t read {} file: {}'.format(grib_type, str(e)))
    # Read in the binary data
    if grib_type == 'grib1':
        data = numpy.fromfile(temp_file, dtype=numpy.float32)
    else:
        data = numpy.frombuffer(bytearray(proc.stdout.read()), dtype='float32')
    if data.size == 0:
        raise IOError('No grib record found')
    # Delete the temporary file
    if grib_type == 'grib1':
        os.remove(temp_file)
    # Flip the data in the y-dimension (if necessary)
    if yrev:
        # Reshape into 2 dimensions
        try:
            data = numpy.reshape(data, (grid.num_y, grid.num_x))
        except AttributeError:
            raise ValueError('The \'yrev\' parameter requires that the '
                             '\'grid\' parameter be defined')
        # Flip
        data = numpy.flipud(data)
        # Reshape back into 1 dimension
        data = numpy.reshape(data, data.size)
    # Return data
    return data

