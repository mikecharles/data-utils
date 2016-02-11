"""
Defines a Grid object. Grid objects store certain properties of a gridded
dataset (lat/lon grid corners, resolution, etc.), and can simplify defining a
grid when calling utilities such as interpolation routines, plotting, etc.
"""


import numpy as np
import warnings


def get_supported_grids():
    return [
        '1/6th-deg-global',
        '0.5deg-global',
        '1deg-global',
        '2deg-global',
        '2.5deg-global',
        '2deg-conus',
    ]


class GridError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Grid:
    """
    Grid definition storing attributes of a grid.

    A Grid object can either be created by providing the name of the grid, in
    which case the name must match one of the following:

    1. 1/6th-deg-global
    2. 0.5deg-global-edge-aligned - note that this grid has the grid box edge
       aligned with even intervals
    3. 0.5-deg-global (or 0.5-deg-global-center-aligned) - note that this grid
       has the grid box center aligned with even intervals 
    4. 1deg-global
    5. 2deg-global
    6. 2.5deg-global
    7. 2deg-conus

    or by providing the other attributes listed below

    Attributes
    ----------

    - name (String)
        - Name of the grid
    - ll_corner (tuple of floats)
        - Lower-left corner of the grid, formatted as (lat, lon)
    - ur_corner (tuple of floats)
        - Upper-right corner of the grid, formatted as (lat, lon)
    - res (float)
        - Resolution of the grid (in km if `type="even"`, in degrees if
        `type="latlon"`)
    - type (str)
        - Grid type. Possible values are:
            - latlon (Latlon grid)
            - equal (Equally-spaced square grid)

    """
    def __init__(self, name=None, ll_corner=None, ur_corner=None, res=None,
                 type='latlon'):

        # Document all instance variables
        self.name = None
        '''Grid name'''

        self.ll_corner = ll_corner
        '''Lower-left corner of grid (lon, lat)'''

        self.ur_corner = ur_corner
        '''Upper-right corner of grid (lon, lat)'''

        self.res = res
        '''Grid resolution'''

        self.type = type
        '''Grid type (currently only latlon is supported)'''

        # Create built-in grid definitions based on name
        if name == '1deg_global' or name == '1deg-global':
            self.name = name
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 359)
            self.res = 1
            self.type = 'latlon'
        elif name == '2deg_global' or name == '2deg-global':
            self.name = name
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 358)
            self.res = 2
            self.type = 'latlon'
        elif name == '2.5deg_global' or name == '2.5deg-global':
            self.name = name
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 357.5)
            self.res = 2.5
            self.type = 'latlon'
        elif name == '2deg_conus' or name == '2deg-conus':
            self.name = name
            self.ll_corner = (20, 230)
            self.ur_corner = (56, 300)
            self.res = 2
            self.type = 'latlon'
        elif name == '1/6th_deg_global' or name == '1/6th-deg-global':
            self.name = name
            self.ll_corner = (-89.9167, 0.0833)
            self.ur_corner = (89.9167, 359.9167)
            self.res = 1/6
            self.type = 'latlon'
        elif name == '0.5deg-global' or name == '0.5-deg-global-center-aligned':
            self.name = name
            self.ll_corner = (-89.75, 0.25)
            self.ur_corner = (89.75, 359.75)
            self.res = 0.5
            self.type = 'latlon'
        elif name == '0.5deg-global-edge-aligned':
            self.name = name
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 359.5)
            self.res = 0.5
            self.type = 'latlon'
        # Otherwise create a custom grid definition
        else:
            if not all([self.ll_corner, self.ur_corner, self.res]):
                raise GridError('You must either supply the name of a '
                                 'built-in Grid, or an ll_corner, '
                                 'ur_corner, and res to create a custom '
                                 'Grid')
            self.name = 'custom'
            self.ll_corner = ll_corner
            self.ur_corner = ur_corner
            self.res = res
            self.type = type

        # Calculate additional attributes
        self.num_y = int(((self.ur_corner[0] - self.ll_corner[0]) / self.res) + 1)
        '''Number of points in the y-direction'''
        self.num_x = int(((self.ur_corner[1] - self.ll_corner[1]) / self.res) + 1)
        '''Number of points in the x-direction'''
        self.lats = np.arange(self.ll_corner[0], self.ur_corner[0] + 0.00000001,
                              self.res).tolist()
        '''List of latitude values at which grid points are found'''
        self.lons = np.arange(self.ll_corner[1], self.ur_corner[1] + 0.00000001,
                              self.res).tolist()
        '''List of longitude values at which grid points are found'''


    def print_info(self):
        """
        Prints all attributes of a given Grid.
        """
        print('Grid info:')
        for key, val in vars(self).items():
            print('\t{}: {}'.format(key, val))


    def assert_correct_grid(self, data):
        """
        Verifies that this is the correct Grid for the given data. If it isn't,

        Parameters
        ----------

        - data - array_like - data to verify

        Exceptions
        ----------

        GridError - if the grid is not correct
        """
        # Make sure there are num_y x num_x points
        try:
            if self.num_y * self.num_x != data.size:
                raise GridError('Total number of points in array is incorrect')
        except AttributeError:
            raise GridError('Data not a valid NumPy array')

    def latlon_to_gridpoint(self, latlons):
        """
        Returns the index of the 1-dimensional array corresponding to this
        grid, given the lat and lon values. The lat/lon value pair must match
        the location of a grid point in this grid, otherwise None will be
        returned.

        Parameters
        ----------

        - latlons - tuple of *float* or *list of tuple of floats* - lat/lon of grid point(s)

        Returns
        -------

        *int* or *None* - array index containing the given grid point(s) index(es), or -1 if no
        grid point matches the given lat/lon value
        """
        if type(latlons) is not list:
            latlons = [latlons]
        matches = []
        for latlon in latlons:
            lat, lon = latlon
            lon = 360 + lon if lon < 0 else lon
            lats, lons = np.meshgrid(self.lats, self.lons)
            lats = lats.reshape((self.num_y * self.num_x))
            lons = lons.reshape((self.num_y * self.num_x))
            try:
                match = np.argwhere((lats == lat) & (lons == lon))[0][0]
                if match.size == 0:
                    matches.append(-1)
                else:
                    matches.append(match)
            except IndexError:
                matches.append(-1)
        return matches

if __name__ == '__main__':
    grid = Grid('1deg-global')
    latlons = [(-93, 31), (-88, 38), (-115, 36)]
    print(grid.latlon_to_gridpoint(latlons))