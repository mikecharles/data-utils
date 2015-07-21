"""
Contains methods for interpolating station data.
"""


import numpy as np
from stats_utils.stats import find_nearest_index


def grid_to_stn(gridded_data, grid, stn_ids, stn_lats, stn_lons):
    """Interpolates values from a grid to stations in a station list.

    Parameters
    ----------

    - gridded_data (array_like)
        - Array of gridded data
    - grid (Grid)
        - `data_utils.gridded.grid.Grid` that the gridded data is on
    - stn_ids (list)
        - List of station ids
    - stn_lats (list)
        - List of station lats
    - stn_lons (list)
        - List of station lons

    Returns
    -------

    - array_like
        - Array of values representing the value of the gridded data
          interpolated to the station locations

    Examples
    --------

    """
    # Reshape gridded data to 2 dimensions if necessary
    if gridded_data.ndim == 1:
        gridded_data = np.reshape(gridded_data, (grid.num_y, grid.num_x))
    # Create empty list to store station vals
    stn_val = []
    # Loop over all stations
    for i in range(len(stn_ids)):
        # Find closest grid point to station
        x_index = find_nearest_index(grid.lons, stn_lons[i])
        y_index = find_nearest_index(grid.lats, stn_lats[i])
        # Assign station val
        stn_val.append(gridded_data[y_index, x_index])

    return stn_val
