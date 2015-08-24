from pytest import raises
from data_utils.gridded import grid
from data_utils.gridded.grid import get_supported_grids



def test_create_Grid_object():
    """Ensure the Grid object can be created"""
    for supported_grid in get_supported_grids():
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
    for supported_grid in get_supported_grids():
        grid.Grid(supported_grid).print_info()
        out, err = capfd.readouterr()
        assert(out)
