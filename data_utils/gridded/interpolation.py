"""
Contains methods for interpolating gridded data.
"""

import numpy
import mpl_toolkits.basemap
from scipy import ndimage
from scipy.ndimage.filters import gaussian_filter

def interpolate(orig_data, orig_grid, new_grid):
    """
    Interpolates a grid from one resolution to another.

    Parameters
    ----------

    - orig_data (array_like)
        - Array of original data
    - orig_grid (Grid)
        - Original `data_utils.gridded.grid.Grid`
    - new_grid : Grid
        - New `data_utils.gridded.grid.Grid`

    Returns
    -------

    - new_data (array_like)
        - A data array on the desired grid.

    Examples
    --------

    Interpolate gridded temperature obs from 2 degrees (CONUS) to 1 degree
    global

        #!/usr/bin/env python
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> from data_utils.gridded.plotting import plot_to_file
        >>> from data_utils.gridded.grid import Grid
        >>> old_grid = Grid('2deg-conus')
        >>> new_grid = Grid('1deg-global')
        >>> file = resource_filename('data_utils', 'lib/example-tmean-obs.bin')
        >>> data = numpy.fromfile(file, 'float32')
        >>> new_data = interpolate(data, old_grid, new_grid)
    """

    # If orig and new grids are the same, we're done
    if orig_grid.name == new_grid.name:
        return orig_data

    # If data is 1-dimensional, reshape to 2 dimensions
    reshape_back_to_1 = False
    if orig_data.ndim == 1:
        reshape_back_to_1 = True
        orig_data = numpy.reshape(orig_data, (orig_grid.num_y, orig_grid.num_x))

    # Generate arrays of longitude and latitude values for the original grid
    num_lats, num_lons = (orig_grid.num_y, orig_grid.num_x)
    orig_start_lat, orig_start_lon = orig_grid.ll_corner
    orig_lons = numpy.arange(orig_start_lon,
                             orig_start_lon + (num_lons * orig_grid.res),
                             orig_grid.res,
                             numpy.float32)
    orig_lats = numpy.arange(orig_start_lat,
                             orig_start_lat + (num_lats * orig_grid.res),
                             orig_grid.res,
                             numpy.float32)

    # Generate mesh of longitude and latitude values for the new grid
    new_start_lat, new_start_lon = new_grid.ll_corner
    new_end_lat, new_end_lon = new_grid.ur_corner
    new_lons, new_lats = numpy.meshgrid(new_grid.lons, new_grid.lats)

    # Use the interp() function from mpl_toolkits.basemap to interpolate the
    # grid to the new lat/lon values.
    new_data = mpl_toolkits.basemap.interp(orig_data, orig_lons, orig_lats,
                                           new_lons, new_lats, order=1,
                                           masked=True)
    # Extract the data portion of the MaskedArray
    new_data = new_data.filled(numpy.nan)

    # If the original data was 1-dimensional, return to 1 dimension
    if reshape_back_to_1:
        new_data = numpy.reshape(new_data, (new_grid.num_y * new_grid.num_x))

    # May be faster, but so far doesn't work with missing data (ex. oceans)
    # f = interpolate.RectBivariateSpline(lats[:,1], lons[1,:], numpy.ma.masked_invalid(data), kx=1, ky=1)
    # data_new = f(lats_new[:,1], lons_new[1,:])

    return new_data


def fill_outside_mask_borders(data, passes=1):
    """
    Fill the grid points outside of the mask borders of a dataset (eg. over the
    ocean for land-only datasets) with the value from the nearest non-missing
    neighbor

    Parameters
    ----------

        - data - *numpy array( - data to fill missing
        - passes - *int* - number of passes (for each pass, 1 extra layer of
        grid points will be filled)
        points

    Returns
    -------

        - A filled array.

    Examples
    --------

    Create a 5x5 array of data, mask out the outer values, and fill

    >>> # Import packages
    >>> from data_utils.gridded.interpolation import fill_outside_mask_borders
    >>> import numpy as np
    >>> # Generate random data with missing values along the border
    >>> A = np.random.randint(1, 9, (5, 5)).astype('float16')
    >>> A[0] = A[-1] = A[:,0] = A[:,-1] = np.nan
    >>> A  # doctest: +SKIP
    array([[ nan,  nan,  nan,  nan,  nan],
           [ nan,   4.,   4.,   3.,  nan],
           [ nan,   6.,   7.,   3.,  nan],
           [ nan,   3.,   8.,   8.,  nan],
           [ nan,  nan,  nan,  nan,  nan]], dtype=float16)
    >>> # Fill the missing outside values with the nearest neighbor values
    >>> A = fill_outside_mask_borders(A)
    >>> A  # doctest: +SKIP
    array([[ 4.,  4.,  4.,  3.,  3.],
           [ 4.,  4.,  4.,  3.,  3.],
           [ 6.,  6.,  7.,  3.,  3.],
           [ 3.,  3.,  8.,  8.,  8.],
           [ 3.,  3.,  8.,  8.,  8.]], dtype=float16)
    """
    # If data is already a masked array, then make sure to return a masked
    # array. If not, return just the data portion
    try:
        data.mask
        is_masked = True
    except AttributeError as e:
        data = numpy.ma.masked_invalid(data)
        is_masked = False
    for _ in range(passes):
        for shift in (-1, 1):
            for axis in (0, 1):
                data_shifted = numpy.roll(data, shift=shift, axis=axis)
                idx = ~data_shifted.mask * data.mask
                data[idx] = data_shifted[idx]
    if is_masked:
        return data
    else:
        return data.data


def smooth(data, grid, smoothing_factor=0.5):
    """
    Smooth an array of spatial data using a gaussian filter

    Parameters
    ----------

    - data - array_like - array of spatial data
    - grid - Grid object corresponding to data
    - smoothing_factor - float, optional - sigma value for the gaussian filter

    Returns
    -------

    - array_like - array of smoothed spatial data

    Examples
    --------

    >>> from pkg_resources import resource_filename
    >>> import numpy as np
    >>> from data_utils.gridded.plotting import plot_to_screen
    >>> from data_utils.gridded.grid import Grid
    >>> from data_utils.gridded.interpolation import smooth
    >>> grid = Grid('2deg-conus')
    >>> A = np.fromfile(resource_filename('data_utils',
    ... 'lib/example-tmean-obs.bin'), dtype='float32')
    >>> A = np.reshape(A, (grid.num_y, grid.num_x))
    >>> plot_to_screen(A, grid, levels=range(-20, 20, 2))  # doctest: +SKIP
    >>> B = smooth(A, grid, smoothing_factor=1)
    >>> plot_to_screen(B, grid, levels=range(-20, 20, 2))  # doctest: +SKIP
    """
    # ----------------------------------------------------------------------
    # Smooth the data
    #
    # Get the mask of the current data array
    mask = numpy.ma.masked_invalid(data).mask
    # Fill all missing values with their nearest neighbor's value so that
    # the following Gaussian filter does not eat away the data set at the
    # borders.
    data = fill_outside_mask_borders(data, passes=max([grid.num_y, grid.num_x]))
    # Apply a Gaussian filter to smooth the data
    data = gaussian_filter(data, smoothing_factor,
                                                 order=0, mode='nearest')
    # Reapply the mask from the initial data array
    return numpy.where(mask, numpy.NaN, data)
