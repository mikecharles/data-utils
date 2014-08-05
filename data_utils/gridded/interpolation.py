import numpy
import mpl_toolkits.basemap

"""
Contains methods for interpolating gridded data.
"""


def interpolate(orig_grid,
                  orig_ll_corner, orig_res,
                  new_ll_corner, new_ur_corner, new_res,
                  grid_type="latlon"):
    """Interpolates a grid from one resolution to another.

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

    # Generate arrays of longitude and latitude values for the original grid
    num_lats, num_lons = orig_grid.shape
    orig_start_lat, orig_start_lon = orig_ll_corner
    orig_lons = numpy.arange(orig_start_lon,
                             orig_start_lon + (num_lons * orig_res),
                             orig_res,
                             numpy.float32)
    orig_lats = numpy.arange(orig_start_lat,
                             orig_start_lat + (num_lats * orig_res),
                             orig_res,
                             numpy.float32)

    # Generate mesh of longitude and latitude values for the new grid
    new_start_lat, new_start_lon = new_ll_corner
    new_end_lat, new_end_lon = new_ur_corner
    new_lons = numpy.arange(new_start_lon,
                            new_end_lon + new_res,
                            new_res,
                            numpy.float32)
    new_lats = numpy.arange(new_start_lat,
                            new_end_lat + new_res,
                            new_res,
                            numpy.float32)
    new_lons, new_lats = numpy.meshgrid(new_lons, new_lats)

    # Use the interp() function from mpl_toolkits.basemap to interpolate the
    # grid to the new lat/lon values. Note that this requires 2 calls because
    # with bilinear, if 1 neighbor point is missing, the interpolated gridpoint
    # becomes missing, so the first call does a nearest neighbor interpolation,
    # the 2nd call does a bilinar interpolation, and we take all points from
    # the 2nd call that are non-nan, and points from the 1st call for all
    # others.
    new_grid_temp1 = mpl_toolkits.basemap.interp(orig_grid, orig_lons, orig_lats,
                                                 new_lons, new_lats, order=0)
    new_grid_temp2 = mpl_toolkits.basemap.interp(orig_grid, orig_lons, orig_lats,
                                                 new_lons, new_lats, order=1)
    new_grid = numpy.where(new_grid_temp2 == numpy.nan, new_grid_temp1, new_grid_temp2)

    # May be faster, but so far doesn't work with missing data (ex. oceans)
    # f = interpolate.RectBivariateSpline(lats[:,1], lons[1,:], numpy.ma.masked_invalid(data), kx=1, ky=1)
    # data_new = f(lats_new[:,1], lons_new[1,:])

    return new_grid
