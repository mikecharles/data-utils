class Grid:
    """
    Grid definition storing attributes of a grid.


    """
    def __init__(self, name=None, ll_corner=None, ur_corner=None, res=None,
                 type='latlon'):
        # Create built-in grid definitions based on name
        if name == '1deg_global':
            self.ll_corner = (-90, 0)
            self.ur_corner = (90, 359)
            self.res = 1
            self.type = 'latlon'
        elif name == '2deg_conus':
            self.ll_corner = (20, 230)
            self.ur_corner = (56, 300)
            self.res = 2
            self.type = 'latlon'
        # Otherwise create a custom grid definition
        else:
            if ll_corner or ur_corner or res == None:
                raise ValueError('You must either supply the name of a '
                                 'built-in GridDef, or an ll_corner, '
                                 'ur_corner, and res to create a custom '
                                 'GridDef')
            self.ll_corner = ll_corner
            self.ur_corner = ur_corner
            self.res = res
            self.type = type
        # Calculate additional attributes
        self.num_y = int(((self.ur_corner[0] - self.ll_corner[0]) / self.res) + 1)
        self.num_x = int(((self.ur_corner[1] - self.ll_corner[1]) / self.res) + 1)
