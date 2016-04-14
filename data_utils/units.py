"""
Contains utilities for converting between different scientific units
"""

import numpy as np


class UnitConverter:
    """Class to support conversion of data between different units"""

    def __init__(self):
        """Class constructor"""
        self.supported_units = [
            '0.1mm-to-mm',
            'degK-to-degC',
            'degC-to-degF',
            'degF-to-degC',
            'm-to-mm',
            'mm-to-inches',
            'inches-to-mm',
        ]

    def get_supported_units(self):
        """Returns a list of supported units"""
        return '\n'.join(self.supported_units)

    def convert(self, data, units):
        """
        Converts data from one unit to another

        Parameters
        ----------

        - data (*array_like*) - NumPy array or list containing data to convert
        - units (*string*) - Units to convert from and to (formatted as XXX-to-YYY). For a list
        of all supported units, call `data_utils.units.UnitConverter.get_supported_units`

        Returns
        -------

        - *array_like* or *float* - NumPy array, list, or float containing the converted data

        Examples
        --------

        Convert degrees Kelvin to Celsius

            #!/usr/bin/env python
            >>> import numpy as np
            >>> from data_utils.units import UnitConverter
            >>> uc = UnitConverter()
            >>> A = np.array([[300, 295, 305], [297, 309, 288]])
            >>> uc.convert(A, 'degK-to-degC')
            array([[ 26.85,  21.85,  31.85],
                   [ 23.85,  35.85,  14.85]])
        """
        # Throw a ValueError if the given units aren't supported
        if units not in self.supported_units:
            raise ValueError('Unsupported units, must be one of {}'.format(
                self.supported_units))

        # Convert given data to a NumPy array if necessary
        if type(data) is not np.ma.core.MaskedArray and type(data) is not np.ndarray:
            data = np.array(data)

        # 0.1mm-to-mm
        if units == '0.1mm-to-mm':
            data = data / 10
        elif units == 'degK-to-degC':
            data = data - 273.15
        elif units == 'm-to-mm':
            data = data * 1000
        elif units == 'mm-to-inches':
            data = data / 25.4
        elif units == 'inches-to-mm':
            data = data * 25.4
        elif units == 'degC-to-degF':
            data = data * 9/5 + 32
        elif units == 'degF-to-degC':
            data = (data - 32) * 5/9
        else:
            raise ValueError('Unsupported units, must be one of {}'.format(
                self.supported_units))

        # Return data
        return data
