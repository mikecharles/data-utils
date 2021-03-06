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


def test_convert_mm_to_inches():
    """Test converting from mm to inches"""
    unit_converter = units.UnitConverter()
    # Single value
    before = 25.4
    after = 1.0
    assert(unit_converter.convert(before, 'mm-to-inches') == after)
    # 1-d List
    before = [25.4, 50.8, 76.2, 101.6, 127.0]
    after = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert_allclose(unit_converter.convert(before, 'mm-to-inches'), after)
    # NumPy array
    before = np.array([[25.4, 50.8, 76.2],
                       [50.8, 76.2, 101.6]], dtype='float64')
    after = np.array([[1.0, 2.0, 3.0],
                      [2.0, 3.0, 4.0]], dtype='float64')
    assert_allclose(unit_converter.convert(before, 'mm-to-inches'), after)


def test_convert_inches_to_mm():
    """Test converting from inches to mm"""
    unit_converter = units.UnitConverter()
    # Single value
    before = 1.0
    after = 25.4
    assert(unit_converter.convert(before, 'inches-to-mm') == after)
    # 1-d List
    before = [1.0, 2.0, 3.0, 4.0, 5.0]
    after = [25.4, 50.8, 76.2, 101.6, 127.0]
    assert_allclose(unit_converter.convert(before, 'inches-to-mm'), after)
    # NumPy array
    before = np.array([[1.0, 2.0, 3.0],
                      [2.0, 3.0, 4.0]], dtype='float64')
    after = np.array([[25.4, 50.8, 76.2],
                       [50.8, 76.2, 101.6]], dtype='float64')
    assert_allclose(unit_converter.convert(before, 'inches-to-mm'), after)


def test_convert_degC_to_degF():
    """Test converting from degC to degF"""
    unit_converter = units.UnitConverter()
    # Single value
    before = 0.
    after = 32.
    assert(unit_converter.convert(before, 'degC-to-degF') == after)
    # 1-d List
    before = [-40., 0., 100.]
    after = [-40., 32., 212.]
    assert_allclose(unit_converter.convert(before, 'degC-to-degF'), after)
    # NumPy array
    before = np.array([[-40., 0.],
                      [0., 100.]], dtype='float64')
    after = np.array([[-40., 32.],
                      [32., 212.]], dtype='float64')
    assert_allclose(unit_converter.convert(before, 'degC-to-degF'), after)


def test_convert_degF_to_degC():
    """Test converting from degC to degF"""
    unit_converter = units.UnitConverter()
    # Single value
    before = 32.
    after = 0.
    assert(unit_converter.convert(before, 'degF-to-degC') == after)
    # 1-d List
    before = [-40., 32., 212.]
    after = [-40., 0., 100.]
    assert_allclose(unit_converter.convert(before, 'degF-to-degC'), after)
    # NumPy array
    before = np.array([[-40., 32.],
                       [32., 212.]], dtype='float64')
    after = np.array([[-40., 0.],
                      [0., 100.]], dtype='float64')
    assert_allclose(unit_converter.convert(before, 'degF-to-degC'), after)
