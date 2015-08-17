from unittest import TestCase
from data_utils import units
from nose.tools import assert_raises, assert_equal, assert_true
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np


class TestUnitConverter(TestCase):

    def test_create_UnitConverter_object(self):
        """Ensure the UnitConvert object can be created"""
        units.UnitConverter()

    def test_get_supported_units_returns_something(self):
        """Ensure get_supported_units() returns a non-empty string"""
        assert_true(units.UnitConverter().get_supported_units())

    def test_exception_raised_for_unsupported_units(self):
        """Ensure an exception is raised for an unsupported units"""
        unit_converter = units.UnitConverter()
        test_val = 1
        test_units = 'unsupported_units'
        assert_raises(ValueError, unit_converter.convert, test_val, test_units)

    def test_convert_0pt1mm_to_mm(self):
        """Test converting from 0.1mm to mm"""
        unit_converter = units.UnitConverter()
        # Single value
        before = 100
        after = 10
        assert_equal(unit_converter.convert(before, '0.1mm-to-mm'), after)
        # 1-d List
        before = [100, 200, 300, 400, 500]
        after = [10, 20, 30, 40, 50]
        assert_array_equal(unit_converter.convert(before, '0.1mm-to-mm'), after)
        # NumPy array
        before = np.array([[300., 305., 310.],
                           [305., 310., 315.]], dtype='float64')
        after = np.array([[26.85, 31.85, 36.85],
                          [31.85, 36.85, 41.85]], dtype='float64')
        assert_allclose(unit_converter.convert(before, 'degK-to-degC'), after)