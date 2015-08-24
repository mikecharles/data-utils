import pytest
from data_utils.gridded import grid


supported_grids = [
    '1/6th-deg-global',
    '0.5deg-global',
    '1deg-global',
    '2deg-global',
    '2.5deg-global',
    '2deg-conus',
]

def test_create_Grid_object():
    """Ensure the Grid object can be created"""
    for supported_grid in supported_grids:
        grid.Grid(supported_grid)


def test_print_info_returns_something(capfd):
    """Ensure the print_info() functions returns a non-empty string"""
    for supported_grid in supported_grids:
        grid.Grid(supported_grid).print_info()
        out, err = capfd.readouterr()
        assert(out)
