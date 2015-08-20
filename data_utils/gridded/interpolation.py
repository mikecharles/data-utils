"""
Contains methods for interpolating gridded data.
"""


import numpy
import mpl_toolkits.basemap


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
