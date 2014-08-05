"""
Contains methods for merging gridded data.
"""

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

    Examples
    --------

    Stack Wei Shi's data on top of a d0 GEFS field

    >>> grib = pygrib.open('/cpc/efsr_realtime/raw/gefs/06h/2013/01/01/00/\
gefs_tmp_2m_20130101_00z_f006_m00.grb2')
    >>> rec = grib.select(name='2 metre temperature', \
typeOfLevel='heightAboveGround', \
level=2)[0]
    >>> bottom = numpy.flipud(rec.values) - 273.15 # Kelvin
    >>> bottom -= 273.15
    >>> top = numpy.fromfile('/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/\
CPC_GLOBAL_T_V0.x_10min.lnx.20131220','float32')
    >>> top[top <= -999] = numpy.nan # Set missing values to NaN
    >>> top = numpy.reshape(top, (6, 1080, 2160))
    >>> top = top[4] # Extract one variable
    >>> orig_ll_corner = ((-90 + 1 / 12.0), (1 / 12.0)) # Interpolate to 1 deg
    >>> top = data_utils.gridded.interpolation.interpolate(top, \
orig_ll_corner, \
1/6.0, \
(-90, 0), \
(90, 359), \
1)
    >>> merged_grid = data_utils.gridded.merging.stack_grids(bottom, top)
    """
    if mask:
        # Wherever the mask is 1, set final_grid to the top grid, bottom elsewhere
        final_grid = numpy.where(mask == 1, top, bottom)
    else:
        # Wherever the top grid is not NAN, set final_grid to the top grid, bottom elsewhere
        final_grid = numpy.where(~numpy.isnan(top), top, bottom)

    return final_grid
