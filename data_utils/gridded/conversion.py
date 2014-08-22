import numpy


"""
Contains methods for converting gridded data from one format to another
"""


def fcst_bin_to_txt(bin_file, num_x, num_y, fcst_ptiles, desired_ptiles,
                    txt_file, terciles=False):
    """Converts a forecast binary file to a text file

    The forecast binary file must contain probabilities of exceeding certain
    percentiles (AKA a POE file), where the percentiles are ascending in the
    file. The dimensions of the file should be (P x L)

    where

    - P is the percentile
    - L is the location

    Parameters
    ----------
    bin_file : string
        Binary file containing the forecast, with the dimensions (ptile x Y x
        X)
    num_x : int
        Number of points in the X-direction
    num_y : int
        Number of points in the Y-direction
    fcst_ptiles : list
        1-dimensional list of percentiles found in the forecast file
    desired_ptiles : list
        1-dimensional list of percentiles to include in the output file
    txt_file : string
        Text file to write data to (will be overwritten)
    terciles : bool, optional
        - If True, will output tercile probabilities (with headers below, normal
          , and above)
        - If False (default), will output probabilities of exceeding percentiles
          (with headers ptileXX, ptileYY, etc.)
        - Can only be set when 2 percentiles are supplied

    Raises
    ------
    ValueError
        If arguments are incorrect

    Examples
    --------

    >>> import numpy
    >>> import data_utils.gridded.conversion
    >>> file = 'gefs_tmax_2m_20140301_00z_d08_poe_ER.bin'
    >>> fcst_ptiles = [ 1,  2,  5, 10, 15,
    ...                20, 25, 33, 40, 50,
    ...                60, 67, 75, 80, 85,
    ...                90, 95, 98, 99]
    >>> desired_ptiles = [10, 90]
    >>> num_x = 360
    >>> num_y = 181
    >>> data = numpy.fromfile(file, dtype='float32')
    >>> data = numpy.reshape(data, (len(fcst_ptiles), num_y, num_x))
    >>> data_utils.gridded.conversion.fcst_bin_to_txt(data,
    ...                                               fcst_ptiles,
    ...                                               desired_ptiles,
    ...                                               'out.txt',
    ...                                               terciles=True)
    """

    # If terciles=True, make sure there are only 2 percentiles
    if terciles:
        if len(desired_ptiles) != 2:
            raise ValueError('To output terciles, you must pass exactly 2 '
                             'desired percentiles')

    # Open binary file
    data = numpy.fromfile(bin_file, dtype='float32')

    # Reshape data
    data = numpy.reshape(data, (len(fcst_ptiles), num_y, num_x))

    # Make sure desired percentiles are part of the forecast percentiles
    if set(fcst_ptiles).issuperset(set(desired_ptiles)):

        # Find the indexes of the desired_ptiles within fcst_ptiles
        ptile_indexes = [fcst_ptiles.index(i) for i in desired_ptiles]

        # Open the output file
        file = open(txt_file, 'w')

        # Establish the format for the grid point column and the data column(s)
        gridpoint_col_fmt = '{:03d}{:03d}'
        data_col_fmt = '{:>12.5f}'

        # ----------------------------------------------------------------------
        # Create a header string
        #
        # The word 'id' is used for the first column (which contains
        # gridpoints). This is the typical header used in the other VWT text
        # files.
        #
        # Also note that the header of each column is designed to match the
        # length of the data in that column, so they are aligned.
        header_string = ('{:<' + str(len(gridpoint_col_fmt.format(0, 0))) +
                         's}  ').format('id')
        if terciles:
            header_string = ('{:<' + str(len(gridpoint_col_fmt.format(0, 0))) +
                             's}  ').format('id')
            for temp_str in ['prob_below', 'prob_normal', 'prob_above']:
                header_string += ('{:>' + str(len(data_col_fmt.format(0))) +
                                  's}  ').format(temp_str)
        else:
            for ptile_index in ptile_indexes:
                header_string += ('{:>' + str(len(data_col_fmt.format(0))) +
                                  's}  ').format('ptile{:02d}'.format(
                    fcst_ptiles[ptile_index]))

        # Write header to file
        file.write(header_string + '\n')

        # Loop over grid
        for x in range(numpy.shape(data)[2]):
            for y in range(numpy.shape(data)[1]):
                # Create a data string consisting of the desired ptiles
                if terciles:
                    probs = []
                    probs.append(1.0 - data[ptile_indexes[0], y, x])
                    probs.append(data[ptile_indexes[0], y, x] -
                                 data[ptile_indexes[1], y, x])
                    probs.append(data[ptile_indexes[1], y, x])
                    data_string = ''
                    for prob in probs:
                        data_string += (data_col_fmt + '  ').format(prob)
                else:
                    data_string = ''
                    for ptile_index in ptile_indexes:
                        data_string += (data_col_fmt + '  ').format(
                            data[ptile_index, y, x])
                # Write the grid point and data to the file
                file.write((gridpoint_col_fmt + '  {}\n').format(
                    x+1, y+1, data_string))

        # Close the output file
        file.close()
    else:
        raise ValueError('Desired percentiles must all be found in fcst '
                         'percentiles')

