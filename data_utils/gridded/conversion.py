import numpy
from bisect import bisect

import stats_utils.stats


"""
Contains methods for converting gridded data from one format to another
"""


def fcst_bin_to_txt(bin_file, num_x, num_y, fcst_ptiles,
                    desired_output_thresholds, txt_file,
                    output_threshold_type='ptile', terciles=False):
    """Converts a forecast binary file to a text file

    The forecast binary file must contain probabilities of exceeding certain
    percentiles (AKA a POE file), where the percentiles are ascending in the
    file. The dimensions of the file should be (P x L)

      where

      - P is the percentile
      - L is the location

    If output_threshold_type is set to 'ptile' ('raw'), then the probability of
    exceeding the given ptiles (raw values) will be written to the output file
    under the headers ptileXX, ptileYY (rawvalXX, rawvalYY), etc.

    If terciles=True, then headers will be different (see the Parameters section
    below)

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
        1-dimensional list of ptiles found in the forecast file
    desired_output_thresholds : list
        1-dimensional list of ptiles or raw values to include in the output file
    txt_file : string
        Text file to write data to (will be overwritten)
    output_threshold_type : string (optional)
        Type of thresholds to write out ('ptile' or 'raw')
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

    >>> import data_utils.gridded.conversion
    >>> bin_file = 'gefs_temp_2m_20140611_00z_d08_d14_poe_ER.bin'
    >>> num_x = 360
    >>> num_y = 181
    >>> fcst_ptiles = [ 1,  2,  5, 10, 15,
    ...                20, 25, 33, 40, 50,
    ...                60, 67, 75, 80, 85,
    ...                90, 95, 98, 99]
    >>> desired_output_thresholds = [33, 67]
    >>> data_utils.gridded.conversion.fcst_bin_to_txt(
    ...    bin_file, num_x, num_y, fcst_ptiles, desired_output_thresholds,
    ...    'out.txt', terciles=True)
    """

    # If terciles=True, make sure there are only 2 percentiles
    if terciles:
        if len(desired_output_thresholds) != 2:
            raise ValueError('To output terciles, you must pass exactly 2 '
                             'desired thresholds')

    # Open binary file
    data = numpy.fromfile(bin_file, dtype='float32')

    # Reshape data
    data = numpy.reshape(data, (len(fcst_ptiles), num_y, num_x))

    # Make sure desired percentiles are part of the forecast percentiles
    if set(fcst_ptiles).issuperset(set(desired_output_thresholds)):

        # Find the indexes of the desired_output_thresholds within fcst_ptiles
        ptile_indexes = [fcst_ptiles.index(i) for i in desired_output_thresholds]

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

def obs_bin_to_txt(bin_file, num_x, num_y, category_thresholds, txt_file,
                   category_threshold_type='ptile', climo_file=None,
                   climo_ptiles=None):
    """Converts an observation binary file to a text file

    The observation binary file must contain raw values of the given variable.
    The file should be a single dimension (locations).

    A climatology file is necessary if category_threshold_type='ptile', in which
    case the raw values in the observation file needs to first be converted to
    ptiles. The climatology file must have probabilities of exceeding a given
    set of percentiles, and be of dimensions (P x L)

      where

      - P is the percentile
      - L is the location

    climo_ptiles must also be provided specifying the percentiles in the file.

    Parameters
    ----------
    bin_file : string
        Binary file containing the observation, with the dimensions (Y x X)
    num_x : int
        Number of points in the X-direction
    num_y : int
        Number of points in the Y-direction
    category_thresholds : list
        1-dimensional list of thresholds (either ptiles or raw values) to
        include in the output file
    txt_file : string
        Text file to write data to (will be overwritten)
    category_threshold_type : string (optional)
        Type of thresholds to write out ('ptile' or 'raw')
    climo_file : string (optional)
        Binary file containing the observation, with the dimensions (Y x X)
    climo_ptiles : list (optional)
        List of percentiles found in the climatology file

    Raises
    ------
    ValueError
        If arguments are incorrect

    Examples
    --------

    >>> import numpy
    >>> import data_utils.gridded.conversion
    >>> num_x = 360
    >>> num_y = 181
    >>> climo_file = '/cpc/data/climatologies/land_air/short_range/global/merged_tmean_poe/1deg/07d/tmean_clim_poe_07d_0625.bin'
    >>> climo_ptiles = numpy.array([ 1,  2,  5, 10, 15,
    ...                             20, 25, 33, 40, 50,
    ...                             60, 67, 75, 80, 85,
    ...                             90, 95, 98, 99])
    >>> bin_file = '/cpc/efsr_realtime/merged_tmean/1deg/07d/2014/06/25/tmean_07d_20140625.bin'
    >>> category_thresholds = [33, 67]
    >>> data_utils.gridded.conversion.obs_bin_to_txt(bin_file, num_x, num_y, category_thresholds, 'out3.txt', climo_file=climo_file, climo_ptiles=climo_ptiles)
    """

    # Currently only supports 3 categories
    if len(category_thresholds) != 2:
        raise ValueError('Currently only supports 3 categories')

    # Open obs binary file
    obs_data = numpy.fromfile(bin_file, dtype='float32')

    # Open climo binary file
    climo_data = numpy.fromfile(climo_file, dtype='float32')

    # Make sure desired percentiles are part of the forecast percentiles
    if set(climo_ptiles).issuperset(set(category_thresholds)):

        # Reshape climo data
        climo_data = numpy.reshape(climo_data, (len(climo_ptiles), num_y*num_x))  # Reshape data

        # Convert observations to percentiles
        k = 1.343
        obs_ptile_data = stats_utils.stats.values_to_ptiles(obs_data, climo_data, climo_ptiles, k)

        # Reshape obs data
        obs_ptile_data = numpy.reshape(obs_ptile_data, (num_y, num_x))  # Reshape data

        # Open the output file
        file = open(txt_file, 'w')

        # Establish the format for the grid point column and the data column(s)
        gridpoint_col_fmt = '{:03d}{:03d}'
        data_col_fmt = {'category': '{:>12.0f}', 'percentile': '{:>12.2f}'}

        # ----------------------------------------------------------------------
        # Create a header string
        #
        # The word 'id' is used for the first column (which contains
        # gridpoints). This is the typical header used in the other VWT text
        # files.
        header_string = ('{:<' + str(len(gridpoint_col_fmt.format(0, 0))) + 's}  ').format('id')
        for temp_str in ['category', 'percentile']:
            header_string += ('{:>' + str(len(data_col_fmt[temp_str].format(0))) + 's}  ').format(temp_str)

        # Write header to file
        file.write(header_string + '\n')

        # Loop over grid
        for x in range(numpy.shape(obs_ptile_data)[1]):
            for y in range(numpy.shape(obs_ptile_data)[0]):
                # Create a data string consisting of the desired data columns
                data_string = ''
                data_string += (data_col_fmt['category'] + '  ').format(
                    bisect(category_thresholds,obs_ptile_data[y, x])+1)
                data_string += (data_col_fmt['percentile'] + '  ').format(
                    obs_ptile_data[y, x])
                # Write the grid point and data to the file
                file.write((gridpoint_col_fmt + '  {}\n').format(x + 1, y + 1,
                                                                 data_string))
        # Close the output file
        file.close()
    else:
        raise ValueError('Desired percentiles must all be found in fcst '
                         'percentiles')