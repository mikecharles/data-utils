"""
Contains methods for writing gridded data.
"""


import numpy as np
from data_utils.gridded.grid import Grid
from data_utils.gridded.interpolation import interpolate


def terciles_to_txt(below, near, above, grid, output_file, missing_val=None):
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
            # If below, near, and above are equal to the missing value
            # specified, do not format them (leave them as is)
            if missing_val is not None and \
                    all([x == missing_val for x in[below[y, x],
                                                   near[y, x],
                                                   above[y, x]]]):
                f.write(
                    '{:02.0f}{:02.0f}    {:4s}    {:4s}    {:4s}\n'.format(
                        x + 1,
                        y + 1,
                        str(missing_val), str(missing_val), str(missing_val)
                    )
                )
            # If below, near, and above are not equal to the missing value
            # specified, proceed with formatting them as floats
            else:
                f.write(
                    '{:02.0f}{:02.0f}   {:4.3f}   {:4.3f}   {:4.3f}\n'.format(
                        x+1, y+1,
                        below[y, x],
                        near[y, x],
                        above[y, x])
                )
    # Close output file
    f.close()
