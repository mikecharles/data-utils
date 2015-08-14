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
        - units (*string*) - Units to convert from and to (formatted as
          XXX-to-YYY). For example:
            - '0.1mm-to-mm'
            - 'degK-to-degC'

        Returns
        -------

        - *array_like* - NumPy array or list containing the converted data

        Examples
        --------

        Here's an example:

            #!/usr/bin/env python
            >>> from pkg_resources import resource_filename
            >>> import numpy as np
            >>> from data_utils.gridded.plotting import plot_to_file
            >>> from data_utils.gridded.grid import Grid
            >>> from data_utils.gridded.interpolation import interpolate
            >>> old_grid = Grid('2deg-conus')
            >>> new_grid = Grid('1deg-global')
            >>> file = resource_filename('data_utils', 'lib/example-tmean-obs.bin')
            >>> data = np.fromfile(file, 'float32')
            >>> new_data = interpolate(data, old_grid, new_grid)
        """
        # Throw a ValueError if the given units aren't supported
        if units not in self.supported_units:
            raise ValueError('Unsupported units, must be one of {}'.format(
                self.supported_units))

        # Convert given data to a NumPy array
        data = np.array(data)

        # 0.1mm-to-mm
        if units == '0.1mm-to-mm':
            data = data / 10
        elif units == 'degK-to-degC':
            data = data - 273.15

        # Return data
        return data
