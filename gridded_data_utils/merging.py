"""
Contains methods for merging gridded data.
"""

from __future__ import print_function
import numpy


def stack_grids(bottom, top, mask=None):
    """Stacks one grid on top of another.

    If a mask argument is provided, then the final grid will be equal to the
    top grid wherever mask=1, and the bottom grid everywhere else.

    If a mask argument is not provided, then the final grid will be equal to
    the top grid wherever the top grid is not missing, and the bottom grid
    everywhere else.

    Parameters
    ----------
    bottom : 2-d array
        2-dimensional (lat x lon) Numpy array of data to serve as the bottom
        grid
    top : 2-d array
        2-dimensional (lat x lon) Numpy array of data to serve as the top grid
    mask : 2-day array, optional
        2-dimensional (lat x lon) Numpy array, set to 1 wherever you would
        like the top grid to be selected

    Example
    -------
    # Read in d0 data (bottom grid)
    >>> grib = pygrib.open('/cpc/efsr_realtime/raw/gefs/06h/2013/01/01/00/ \
                           gefs_tmp_2m_20130101_00z_f006_m00.grb2')
    >>> rec = grib.select(name='2 metre temperature',
                          typeOfLevel='heightAboveGround',
                          level=2)[0]
    >>> bottom = numpy.flipud(rec.values)
    # Convert from Kelvin to Celsius
    >>> bottom -= 273.15
    # Read in Wei Shi's data (top grid)
    >>> top = numpy.fromfile('/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/ \
                             CPC_GLOBAL_T_V0.x_10min.lnx.20131220','float32')
    # Set missing values to NaNs
    >>> top[top <= -999] = numpy.nan
    # Reshape to 3 dimensions (vars x lats x lons)
    >>> top = numpy.reshape(top, (6, 1080, 2160))
    # Extract one variable
    >>> top = top[4]
    # Interpolate to 1 degree
    >>> orig_ll_corner = ((-90 + 1 / 12.0), (1 / 12.0))
    >>> top = gridded_data_utils.interpolation.interpolate(top,
                                                           orig_ll_corner,
                                                           1/6.0,
                                                           (-90, 0),
                                                           (90, 359),
                                                           1)
    # Stack the two grids
    >>> merged_grid = gridded_data_utils.merging.stack_grids(bottom, top)
    """
    # Wherever the mask is 1, set final_grid to the top grid, bottom elsewhere
    final_grid = numpy.where(mask == 1, top, bottom)

    return final_grid
