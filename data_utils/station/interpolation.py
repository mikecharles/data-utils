import numpy as np
from stats_utils.stats import find_nearest_index


"""
Contains methods for interpolating gridded data.
"""


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



if __name__ == '__main__':
    import numpy as np
    from data_utils.gridded.grid import Grid
    from pkg_resources import resource_filename

    grid = Grid('1deg_global')

    below = np.fromfile('../../below.bin', dtype='float32')
    near = np.fromfile('../../near.bin', dtype='float32')
    above = np.fromfile('../../above.bin', dtype='float32')

    stn_ids = []
    stn_lats = []
    stn_lons = []
    with open(resource_filename('data_utils', 'library/station-list-tmean.csv'),
              'r') as file:
        next(file)  # Skip header
        # Loop over lines
        for line in file:
            columns = line.replace('\n', '').split(',')
            stn_ids.append(columns[0])
            stn_lats.append(float(columns[6]))
            if float(columns[7]) < 0:
                stn_lons.append(float(columns[7]) + 360)
            else:
                stn_lons.append(float(columns[7]))

    below_stn = grid_to_stn(below, grid, stn_ids, stn_lats, stn_lons)
    near_stn = grid_to_stn(near, grid, stn_ids, stn_lats, stn_lons)
    above_stn = grid_to_stn(above, grid, stn_ids, stn_lats, stn_lons)

    print('DONE')