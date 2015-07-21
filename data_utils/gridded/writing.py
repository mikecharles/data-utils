"""
Contains methods for writing gridded data.
"""


import numpy as np
from data_utils.gridded.grid import Grid
from data_utils.gridded.interpolation import interpolate


def terciles_to_txt(below, near, above, grid, output_file):
    # Reshape data from one to two dimensions
    if below.ndim == near.ndim == above.ndim == 1:
        below = np.reshape(below, (grid.num_y, grid.num_x))
        near = np.reshape(near, (grid.num_y, grid.num_x))
        above = np.reshape(above, (grid.num_y, grid.num_x))
    # Open output file
    f = open(output_file, 'w')
    # Loop over all grid points
    f.write('XXYY   below    near   above\n'.format())
    for x in range(grid.num_x):
        for y in range(grid.num_y):
            # TODO: Make the num X and Y sizes dynamic - ex. XXYY vs XXXYYY
            f.write('{:02.0f}{:02.0f}   {:4.3f}   {:4.3f}   {:4.3f}\n'.format(
                x+1, y+1,
                below[y, x],
                near[y, x],
                above[y, x])
            )
    # Close output file
    f.close()
