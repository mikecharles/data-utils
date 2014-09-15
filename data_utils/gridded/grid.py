class Grid:
    """
    Grid definition storing attributes of a grid.

    A Grid object can either be created by providing the name of the grid, in
    which case the name must match one of the following:

        1. 1deg_global
        2. 2deg_global
        3. 2deg_conus
        4. 1/6th_deg_global

    or by providing the other attributes listed below

    Attributes
    ----------
    name : String
        Name of the grid
    ll_corner : tuple of floats
        Lower-left corner of the grid, formatted as (lat, lon)
    ur_corner : tuple of floats
        Upper-right corner of the grid, formatted as (lat, lon)
    res : float
        Resolution of the grid (in km if ``type="even"``, in degrees if
        ``type="latlon"``)
    type : str
        Grid type. Possible values are:
            - latlon : Latlon grid
            - equal : Equally-spaced square grid

    """
    def __init__(self, name=None, ll_corner=None, ur_corner=None, res=None,
                 type='latlon'):
        # Create built-in grid definitions based on name
        if name == '1deg_global':
            self.name = name
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 359)
            self.res = 1
            self.type = 'latlon'
        elif name == '2deg_global':
            self.name = name
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 358)
            self.res = 2
            self.type = 'latlon'
        elif name == '2deg_conus':
            self.name = name
            self.ll_corner = (20, 230)
            self.ur_corner = (56, 300)
            self.res = 2
            self.type = 'latlon'
        elif name == '1/6th_deg_global':
            self.name = name
            self.ll_corner = (-89.9167, 0.0833)
            self.ur_corner = (89.9167, 359.9167)
            self.res = 1/6
            self.type = 'latlon'
        # Otherwise create a custom grid definition
        else:
            if ll_corner or ur_corner or res == None:
                raise ValueError('You must either supply the name of a '
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
        self.num_x = int(((self.ur_corner[1] - self.ll_corner[1]) / self.res) + 1)
