

"""
Contains methods for converting gridded data from one format to another
"""


def fcst_bin_to_ascii():
    """Converts a forecast binary file to an ASCII file

    The forecast binary file must contain probabilities of exceeding certain
    percentiles (AKA a POE file), where the percentiles are ascending in the
    file. The dimensions of the file should be (P x L)

    where

    - P is the percentile
    - L is the location

    Parameters
    ----------
    orig_grid : array_like
        2-dimensional (lat x lon) Numpy array of data to interpolate
    orig_ll_corner : tuple of floats
        Lower-left corner of the original grid, formatted as (lat, lon)
    orig_res : float
        Original grid resolution (in km if ``grid_type="even"``, in degrees if
        ``grid_type="latlon"``)
    new_ll_corner : tuple of floats
        Lower-left corner of the new grid, formatted as (lat, lon)
    new_ur_corner : tuple of floats
        Upper-right corner of the new grid, formatted as (lat, lon)
    new_res : float
        New grid resolution (in km if ``grid_type="even"``, in degrees if
        ``grid_type="latlon"``)
    grid_type : str
        Original grid type. Possible values are:
            - latlon : Latlon grid
            - equal : Equally-spaced square grid

    Returns
    -------
    grid : array_like
        A grid at the desired resolution.

    Examples
    --------

    Interpolate Wei Shi's gridded temperature obs from 1/6th deg to 1 deg

    >>> file = '/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/CPC_GLOBAL_T_V0.x_10min.lnx.20131220'
    >>> data = numpy.fromfile(file, 'float32')
    >>> data[data <= -999] = numpy.nan
    >>> data = numpy.reshape(data, (6, 1080, 2160))
    >>> data = data[4]
    >>> orig_ll_corner = (-89.9167, 0.0833)
    >>> orig_res = 1/6.0
    >>> new_res = 4
    >>> new_ll_corner = (-90, 0)
    >>> new_ur_corner = (90, 360-new_res)
    >>> new_grid = data_utils.gridded.interpolation.interpolate(data, \
orig_ll_corner, \
orig_res, \
new_ll_corner, \
new_ur_corner, \
new_res, \
grid_type="latlon")
    """

    # --------------------------------------------------------------------------
    # Read in forecast binary file
    #

    # --------------------------------------------------------------------------
    # Make sure desired percentiles are part of the forecast percentiles
    #

        # ----------------------------------------------------------------------
        # If not, then interpolate
        #

    # --------------------------------------------------------------------------
    # Read in forecast binary file
    #
