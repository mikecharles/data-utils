from data_utils.gridded import interpolation
from data_utils.gridded.grid import get_supported_grids, Grid
import numpy as np
from pytest import raises


def test_interpolation():
    """Test that interpolation can be done between all grids"""
    # Create fake data for every grid
    fake_data = {}
    for gridname in get_supported_grids():
        grid = Grid(gridname)
        fake_data[gridname] = np.random.rand(grid.num_y, grid.num_x).astype(
            'float16')
    # Loop over every possible combination of grids
    for gridname1 in get_supported_grids():
        for gridname2 in get_supported_grids():
            # Create 2 Grid objects
            grid1 = Grid(gridname1)
            grid2 = Grid(gridname2)
            interpolation.interpolate(fake_data[gridname1], grid1, grid2)


def test_fill_outside_borders():
    """Test the function that fills data outside the borders"""
    # Make sure when passing in a MaskedArray, a MaskedArray is returned
    test_array = np.ma.masked_array(np.random.rand(2, 2))
    returned_array = interpolation.fill_outside_mask_borders(test_array)
    mask = returned_array.mask
    # Make sure when passing in a non-MaskedArray, a non-MaskedArray is returned
    test_array = np.random.rand(2, 2)
    returned_array = interpolation.fill_outside_mask_borders(test_array)
    with raises(AttributeError):
        returned_array.mask


if __name__ == '__main__':
    test_fill_outside_borders()
