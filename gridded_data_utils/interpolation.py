"""
Contains methods for interpolating gridded data.
"""

def interpolate(data, start_lat, start_lon, resolution, grid_spacing="latlon"):
    """Interpolates a grid from one resolution to another.

    Parameters
    ----------
    data : array_like
        2-dimensional (y-by-x) Numpy array of data to interpolate
    start_lat : float
        Start latitude (bottom-left corner of grid)
    start_lon : float
        Start longitude (bottom-left corner of grid)
    resolution : float
        Grid resolution (in km if `grid_spacing`="even", in degrees if `grid_spacing`="latlon")

    Returns
    -------
    grid : array_like
        A grid at the desired resolution.
    """

    # Generate an array of longitude values for the old grid

    # Generate an array of latitude values for the old grid

    # Generate an