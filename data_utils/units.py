"""
Contains utilities for converting between different scientific units
"""

def convert(data, units):
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
    pass

