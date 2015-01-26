#!/usr/bin/env python

import numpy as np
from data_utils.gridded.grid import Grid
from data_utils.gridded.interpolation import interpolate


"""
Contains methods for writing gridded data.
"""

def terciles_to_txt(below, near, above, grid, output_file):
    # Reshape data from one to two dimensions
    if below.ndim == near.ndim == above.ndim == 1:
        below = np.reshape(below, (grid.num_y, grid.num_x))
        near = np.reshape(below, (grid.num_y, grid.num_x))
        above = np.reshape(below, (grid.num_y, grid.num_x))
    # Open output file
    f = open(output_file, 'w')
    # Loop over all grid points
    f.write('XXYY   below   near   above\n'.format())
    for x in range(grid.num_x):
        for y in range(grid.num_y):
            # TODO: Make the num X and Y sizes dynamic - ex. XXYY vs XXXYYY
            f.write('{:02.0f}{:02.0f}   {:4.3f}  {:4.3f}   {:4.3f}\n'.format(
                x+1, y+1,
                below[y, x],
                near[y, x],
                above[y, x])
            )
    # Close output file
    f.close()

if __name__ == '__main__':
    below_old = np.fromfile('../../below.bin', dtype='float32')
    near_old = np.fromfile('../../near.bin', dtype='float32')
    above_old = np.fromfile('../../above.bin', dtype='float32')
    old_grid = Grid('1deg_global')
    new_grid = Grid('2deg_conus')

    below = interpolate(below_old, old_grid, new_grid)
    near = interpolate(near_old, old_grid, new_grid)
    above = interpolate(above_old, old_grid, new_grid)

    terciles_to_txt(below, near, above, new_grid, 'test.txt')
