from pytest import raises
from data_utils.gridded import grid
import numpy as np



def test_create_Grid_object():
    """Ensure the Grid object can be created"""
    for supported_grid in grid.get_supported_grids():
        grid.Grid(supported_grid)


def test_exception_raised_for_unsupported_grid():
    """Ensure an exception is raised for an unsupported units"""
    with raises(ValueError):
        grid.Grid('unsupported')


def test_exception_raised_for_no_grid_name():
    """Ensure an exception is raised for an unsupported units"""
    with raises(ValueError):
        grid.Grid()


def test_create_custom_Grid():
    """Ensure a custom Grid object can be created"""
    grid.Grid(ll_corner=(0, 0), ur_corner=(90, 90), res=1)


def test_print_info_returns_something(capfd):
    """Ensure the print_info() functions returns a non-empty string"""
    for supported_grid in grid.get_supported_grids():
        grid.Grid(supported_grid).print_info()
        out, err = capfd.readouterr()
        assert(out)


def test_assert_correct_grid():
    """Tests the is_correct_grid() function"""
    # Should raise a GridError if the number of points is incorrect
    test_grid = grid.Grid('1deg-global')
    bad_y = test_grid.num_y - 1
    bad_x = test_grid.num_x - 1
    test_array = np.random.rand(bad_y, bad_x)
    with raises(grid.GridError):
        test_grid.assert_correct_grid(test_array)
    # Should raise a GridError if the data isn't a NumPy array
    test_grid = grid.Grid('1deg-global')
    with raises(grid.GridError):
        test_grid.assert_correct_grid(1)


if __name__ == '__main__':
    test_assert_correct_grid()
