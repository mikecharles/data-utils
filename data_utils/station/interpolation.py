

"""
Contains methods for interpolating gridded data.
"""


def grid_to_stn(gridded_data, grid, stn_ids, stn_lats, stn_lons):
    """Interpolates values from a grid to stations in a station list.

    Parameters
    ----------
    gridded_data : array_like
        Array of gridded data
    grid : Grid
        :class:`~data_utils.gridded.grid.Grid` that the gridded data is on
    stn_ids : list
        List of station ids
    stn_lats : list
        List of station lats
    stn_lons : list
        List of station lons

    Returns
    -------
    array_like
        Array of values representing the value of the gridded data
        interpolated to the station locations

    Examples
    --------

    """
    for i in len(stn_ids):



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