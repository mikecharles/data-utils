"""
Contains methods for merging gridded data.
"""

from __future__ import print_function
import numpy


def stack_grids(bottom, top, mask=None):
    # Set the final grid equal to the bottom grid
    final_grid = bottom

    # Wherever the mask is 1, replace the final_grid with the top grid
    final_grid = numpy.where(mask == 1, top, bottom)

    return final_grid
