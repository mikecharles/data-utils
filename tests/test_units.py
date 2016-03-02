from data_utils import units
from pytest import raises
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np


def test_create_UnitConverter_object():
    """Ensure the UnitConvert object can be created"""
    units.UnitConverter()


def test_get_supported_units_returns_something():
    """Ensure get_supported_units() returns a non-empty string"""
    assert(units.UnitConverter().get_supported_units())


def test_exception_raised_for_unsupported_units():
    """Ensure an exception is raised for an unsupported units"""
    with raises(ValueError):
        unit_converter = units.UnitConverter()
        test_val = 1
        test_units = 'unsupported_units'
        unit_converter.convert(test_val, test_units)


def test_convert_0pt1mm_to_mm():
    """Test converting from 0.1mm to mm"""
    unit_converter = units.UnitConverter()
    # Single value
    before = 100
    after = 10
    assert(unit_converter.convert(before, '0.1mm-to-mm') == after)
    # 1-d List
    before = [100, 200, 300, 400, 500]
    after = [10, 20, 30, 40, 50]
    assert_allclose(unit_converter.convert(before, '0.1mm-to-mm'), after)
    # NumPy array
    before = np.array([[100, 200, 300],
                       [200, 300, 400]], dtype='float64')
    after = np.array([[10, 20, 30],
                      [20, 30, 40]], dtype='float64')
    assert_allclose(unit_converter.convert(before, '0.1mm-to-mm'), after)
