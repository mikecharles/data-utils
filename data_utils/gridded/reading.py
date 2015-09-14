"""
Contains methods for reading gridded data.
"""

import subprocess
import shlex
import uuid
import os
import logging

import numpy


# Initialize a logging object specific to this module
logger = logging.getLogger('root')


def read_grib(file, grib_type, variable, level, yrev=False):
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
    - yrev (optional)
        - Option to flip the data in the y-direction

    Returns
    -------
    - (array_like)
        - A data array

    Raises
    ------
    - IOError
        - If wgrib has a problem reading the grib and/or writing the temp file
    - Exception
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
    # Set the name of the wgrib program to call
    if grib_type == 'grib1':
        wgrib_call = 'wgrib "{}" | grep "{}" | grep "{}" | wgrib -i "{}" -nh ' \
                     '-bin -o "{}"'.format(file, variable, level, file,
                                           temp_file)
    elif grib_type == 'grib2':
        # Note that the binary data is written to stdout
        wgrib_call = 'wgrib2 "{}" -match "{}" -match "{}" -end -order we:sn ' \
                     '-no_header -inv /dev/null -bin -'.format(file,
                                                               variable, level)
    else:
        raise IOError(__name__ + ' requires grib_type to be grib1 or grib2')
    # Generate a wgrib call
    try:
        logger.debug('Command to extract grib data: ' + wgrib_call)
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
        raise Exception('No grib record found')
    # Delete the temporary file
    if grib_type == 'grib1':
        os.remove(temp_file)
    # Flip the data in the y-dimension (if necessary)
    if yrev:
        # Reshape into 2 dimensions
        data = numpy.reshape(data, ())
    # Return data
    return data

