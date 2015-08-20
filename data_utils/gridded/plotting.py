"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import scipy.ndimage
import math
import logging
from pkg_resources import resource_filename
from palettable.colorbrewer.sequential import Greens_7, YlOrBr_7
from data_utils.gridded.interpolation import interpolate
from data_utils.gridded.grid import Grid
from data_utils.gridded.interpolation import fill_outside_borders
from data_utils.gridded.interpolation import smooth

# ------------------------------------------------------------------------------
# Setup logging
#
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Setup reusable docstring
#
_docstring_kwargs = """
    - levels (list, optional)
        - List of levels to shade/contour.
    - colors (list of lists, or string)
        - Specifies the colors to be used to plot the data. It can either be:
            - A list of colors, each color being a list of RGB values from 0
            to 1 (ex. [[0.2, 0.2, 1],[0.4, 0.5, 0.8],[0.2, 0.2, 0.5]])
            - A string specifying the variable and plot type. Supported values:
                - tmean-terciles
    - projection (str, optional)
        - Set the map projection ('lcc' or 'mercator')
    - region (str, optional)
        - Set the plotting region ('US', 'CONUS', 'global')
    - title (str, optional)
        - Title of the resulting plot
    - lat_range (tuple, optional)
        - Range of latitude values to plot
    - lon_range (tuple, optional)
        - Range of longitude values to plot
    - cbar_ends (str, optional)
        - Shape of the ends of the colorbar ('square' or 'triangular'). If
        'square', levels should contain the endpoints. If 'triangular',
        the levels should not contain the endpoints.
    - cbar_type (string, optional)
        - Type of colorbar ('normal' for a normal colorbar, or 'tercile' for a
        tercile colorbar with 3 color ranges)
    - tercile_type (str, optional)
        - Type of tercile ('normal' or 'median')
    - smoothing_factor (float, optional)
        - Level of smoothing (gaussian filter, this represents the kernel
        width in standard deviations - may need to experiment with value -
        generally between 0 and 2 should suffice)
    """


def _make_plot(*args, **kwargs):
    """
    Creates a plot object using `mpl_toolkits.basemap`

    Nothing is actually plotted. Usually you'd want to call
    `data_utils.gridded.plotting._show_plot` or
    `data_utils.gridded.plotting._save_plot` after this.

    Parameters
    ----------

    - data (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data to plot
    - grid (Grid object)
        - See [data_utils.gridded.grid.Grid](
        ../gridded/grid.m.html#data_utils.gridded.grid.Grid)
    {}
    """

    # Get *args
    data = args[0]
    grid = args[1]
    # Get **kwargs
    levels = kwargs['levels']
    projection = kwargs['projection']
    region = kwargs['region']
    colors = kwargs['colors']
    title = kwargs['title']
    lat_range = kwargs['lat_range']
    lon_range = kwargs['lon_range']
    cbar_ends = kwargs['cbar_ends']
    cbar_type = kwargs['cbar_type']
    tercile_type = kwargs['tercile_type']
    smoothing_factor = kwargs['smoothing_factor']
    fill_coastal_vals = kwargs['fill_coastal_vals']

    # --------------------------------------------------------------------------
    # Check args
    #
    # Levels must be set if colors is set
    if colors and not levels:
        raise ValueError('The "levels" argument must be set if the "colors" '
                         'argument is set')
    # Make sure either region is set, or lat_range and lon_range are set
    if lat_range and lon_range:
        logger.warning('lat_range and lon_range will override the given region')
    elif lat_range is None and lon_range is None:
        # Make sure region is supported
        supported_regions = ['US', 'CONUS', 'global']
        if region not in supported_regions:
            raise ValueError('Unsupported region, must be one of {}'.format(
                supported_regions))
    else:
        raise ValueError('lat_range on lon_range must either both be defined, '
                         'or both be not defined')
    # Make sure region and projection make sense together
    if region == 'global' and projection != 'mercator':
        raise ValueError('Only the \'mercator\' projection can be used when '
                         'region is set to \'global\'')

    # --------------------------------------------------------------------------
    # Check colors variable
    #
    # If colors is a string, obtain a colors list
    if isinstance(colors, str):
        colors = _get_colors(colors)
    # Make sure there is 1 more color than levels
    if colors:
        if len(colors) != (len(levels) + 1):
            raise ValueError('The number of colors must be 1 greater than the '
                             'number of levels')

    # Convert the ll_corner and res to arrays of lons and lats
    start_lat, start_lon = grid.ll_corner
    end_lat, end_lon = grid.ur_corner
    lats = np.arange(start_lat, end_lat + grid.res, grid.res)
    lons = np.arange(start_lon, end_lon + grid.res, grid.res)

    # Create a 2-d mesh array of lons and lats for pyplot
    lons, lats = np.meshgrid(lons, lats)

    # Create Basemap
    fig, ax = matplotlib.pyplot.subplots()
    if projection == 'mercator':
        # Get lat_range and lon_range from region if they aren't already defined
        if not (lat_range and lon_range):
            if region == 'US':
                lat_range = (25, 72)
                lon_range = (190, 300)
                latlon_line_interval = 10
            elif region == 'CONUS':
                lat_range = (24, 50)
                lon_range = (230, 295)
                latlon_line_interval = 5
            elif region == 'global':
                lat_range = (-90, 90)
                lon_range = (0, 360)
                latlon_line_interval = 30
            else:
                lat_range = (-90, 90)
                lon_range = (0, 360)
                latlon_line_interval = 30
        else:
            latlon_line_interval = 30
        m = mpl_toolkits.basemap.Basemap(llcrnrlon=lon_range[0],
                                         llcrnrlat=lat_range[0],
                                         urcrnrlon=lon_range[1],
                                         urcrnrlat=lat_range[1],
                                         projection='mill',
                                         ax=ax,
                                         resolution='l')
        m.drawcoastlines(linewidth=1)
        m.drawparallels(np.arange(lat_range[0], lat_range[1]+1, latlon_line_interval),
                        labels=[1, 1, 0, 0], fontsize=9)
        m.drawmeridians(np.arange(lon_range[0], lon_range[1]+1, latlon_line_interval),
                        labels=[0, 0, 0, 1], fontsize=9)
        m.drawmapboundary(fill_color='#DDDDDD')
        m.drawcountries()
    elif projection in ['lcc', 'equal-area']:
        # Set the name of the projection for Basemap
        if projection == 'lcc':
            basemap_projection = 'lcc'
        elif projection == 'equal-area':
            basemap_projection = 'laea'
        # Warn if user provides lat_range and lon_range, which will have no
        # effect for these projections
        if lat_range or lon_range:
            logger.warning('lat_range and lon_range have no effect for '
                           'projection {}'.format(projection))
        # Set width, height, lat_0, and lon_0 based on region
        if not (lat_range and lon_range):
            if region == 'US':
                m = mpl_toolkits.basemap.Basemap(width=8000000, height=6600000,
                                                 lat_0=53., lon_0=260.,
                                                 projection=basemap_projection,
                                                 ax=ax, resolution='l')
            elif region == 'CONUS':
                m = mpl_toolkits.basemap.Basemap(width=5000000, height=3200000,
                                                 lat_0=39., lon_0=262.,
                                                 projection=basemap_projection,
                                                 ax=ax, resolution='l')
        else:
            m = mpl_toolkits.basemap.Basemap(llcrnrlon=lon_range[0],
                                             llcrnrlat=lat_range[0],
                                             urcrnrlon=lon_range[1],
                                             urcrnrlat=lat_range[1],
                                             projection=basemap_projection,
                                             ax=ax, resolution='l')
        # Draw political boundaries
        m.drawcountries(linewidth=0.5)
        m.drawcoastlines(0.5)
        if region in ['US', 'CONUS']:
            m.readshapefile(resource_filename('data_utils', 'lib/states'),
                            name='states', drawbounds=True)
            ax = matplotlib.pyplot.gca()
            for state in m.states:
                x, y = zip(*state)
                m.plot(x, y, marker=None, color='black', linewidth=0.75)
    else:
        raise ValueError('Supported projections: \'mercator\', \'lcc\'')

    # Smooth the data
    data = smooth(data, grid, smoothing_factor=smoothing_factor)

    # --------------------------------------------------------------------------
    # Fill coastal values (if requested)
    #
    if fill_coastal_vals:
        # Datasets (particularly datasets on a course grid) that are masked
        # out over the water suffer from some missing grid points along the
        # coast. The methodology below remedies this, filling in those values
        #  while creating a clean mask along the water.
        #
        # Shift the entire data array 1 grid point in each direction,
        # and for every grid point that becomes "unmissing" after shifting
        # the grid (every grid point that has a non-missing neighbor),
        # set the value of the grid point to the neighbor's value.
        data = fill_outside_borders(data, passes=2)

        # Place data in a high-res grid so the ocean masking looks decent
        high_res_grid = Grid('1/6th-deg-global')
        data = interpolate(data, grid, high_res_grid)
        lons, lats = np.meshgrid(high_res_grid.lons, high_res_grid.lats)
        # Mask the ocean values
        data = mpl_toolkits.basemap.maskoceans((lons - 360), lats, data,
                                               inlands=True)

    # Plot data
    if cbar_ends == 'triangular':
        extend='both'
    elif cbar_ends == 'square':
        extend='neither'
    else:
        raise ValueError('cbar_ends must be either \'triangular\' or '
                         '\'square\'')
    if levels:
        if colors:
            plot = m.contourf(lons, lats, data, levels, latlon=True,
                              extend=extend, colors=colors)
        else:
            plot = m.contourf(lons, lats, data, levels, latlon=True,
                              extend=extend)
    else:
        plot = m.contourf(lons, lats, data, latlon=True, extend=extend)
        levels = plot._levels

    # Add labels
    matplotlib.pyplot.title(title, fontsize=10)

    # --------------------------------------------------------------------------
    # Add a colorbar
    #
    if cbar_type == 'tercile':
        # Generate probability tick labels
        labels = ['{:.0f}%'.format(math.fabs(level)) for level in levels]
        # Add the colorbar (attached to figure above)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="4%", pad=0.3)
        cb = matplotlib.pyplot.colorbar(plot, orientation="horizontal",
                                        ticks=levels, cax=cax)
        cb.ax.set_xticklabels(labels)
        cb.ax.tick_params(labelsize=8)
        # Add colorbar labels
        fontsize=8
        tercile_type = tercile_type.capitalize()
        cb.ax.text(0.24, 1.2, 'Probability of Below {}'.format(tercile_type),
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
        cb.ax.text(0.5, 1.2, '{}'.format(tercile_type),
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
        cb.ax.text(0.76, 1.2, 'Probability of Above {}'.format(tercile_type),
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
    else:
        # Add the colorbar (attached to figure above)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="4%", pad=0.3)
        cb = matplotlib.pyplot.colorbar(plot, orientation="horizontal", cax=cax)


def plot_to_screen(data, grid, levels=None, colors=None,
                   projection='equal-area', region='US', title='',
                   lat_range=None, lon_range=None,
                   cbar_ends='triangular', tercile_type='normal',
                   smoothing_factor=0, cbar_type='normal',
                   fill_coastal_vals=False):
    """
    Plots the given data and displays on-screen.

    Essentially makes calls to `_make_plot` and `_show_plot` to do the work

    Parameters
    ----------

    - data (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data to plot
    - grid (Grid object)
        - See [data_utils.gridded.grid.Grid](
        ../gridded/grid.m.html#data_utils.gridded.grid.Grid)
    {}

    Examples
    --------

        #!/usr/bin/env python
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> from data_utils.gridded.plotting import plot_to_screen
        >>> from data_utils.gridded.grid import Grid
        >>> grid = Grid('2deg-conus')
        >>> A = np.fromfile(resource_filename('data_utils',
        ... 'lib/example-tmean-obs.bin'), dtype='float32')
        >>> A = np.reshape(A, (grid.num_y, grid.num_x))
        >>> A[A == -999] = np.nan
        >>> plot_to_screen(A, grid)  # doctest: +SKIP
    """

    # --------------------------------------------------------------------------
    # Get dictionary of kwargs for child function
    #
    # Use locals() function to get all defined vars
    kwargs = locals()
    # Remove positional args
    del kwargs['data']
    del kwargs['grid']
    # --------------------------------------------------------------------------
    # Reshape array if necessary
    #
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    # --------------------------------------------------------------------------
    # Define *args to pass to child function
    #
    args = [data, grid]
    # --------------------------------------------------------------------------
    # Call _make_plot()
    #
    _make_plot(*args, **kwargs)
    _show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(data, grid, file, dpi=200, levels=None,
                 projection='equal-area', region='US', colors=None,
                 title='', lat_range=None, lon_range=None,
                 cbar_ends='triangular', tercile_type='normal',
                 smoothing_factor=0, cbar_type='normal',
                 fill_coastal_vals=False):
    """
    Plots the given data and saves to a file.

    Essentially makes calls to `_make_plot` and `_save_plot` to do the work

    Parameters
    ----------

    - data (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data to plot
    - grid (Grid object)
        - See [data_utils.gridded.grid.Grid](
        ../gridded/grid.m.html#data_utils.gridded.grid.Grid)
    - file (str)
        - File name to save plot to
    {}

    Examples
    --------

        #!/usr/bin/env python
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> from data_utils.gridded.plotting import plot_to_file
        >>> from data_utils.gridded.grid import Grid
        >>> grid = Grid('2deg-conus')
        >>> A = np.fromfile(resource_filename('data_utils',
        ... 'lib/example-tmean-obs.bin'), dtype='float32')
        >>> A = np.reshape(A, (grid.num_y, grid.num_x))
        >>> A[A == -999] = np.nan
        >>> plot_to_file(A, grid, 'out.png')  # doctest: +SKIP
    """

    # --------------------------------------------------------------------------
    # Get dictionary of kwargs for child function
    #
    # Use locals() function to get all defined vars
    kwargs = locals()
    # Remove positional args
    del kwargs['data']
    del kwargs['grid']
    del kwargs['file']
    # --------------------------------------------------------------------------
    # Set backend to Agg which won't require X11
    #
    matplotlib.pyplot.switch_backend('Agg')
    # --------------------------------------------------------------------------
    # Reshape array if necessary
    #
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    # --------------------------------------------------------------------------
    # Define *args to pass to child function
    #
    args = [data, grid]
    # --------------------------------------------------------------------------
    # Call _make_plot()
    #
    _make_plot(*args, **kwargs)
    _save_plot(file, dpi)
    matplotlib.pyplot.close("all")


def plot_tercile_probs_to_screen(below, near, above, grid,
                                 levels=[-90, -80, -70, -60, -50, -40, -33, 33,
                                         40, 50, 60, 70, 80, 90],
                                 projection='equal-area', region='US',
                                 colors='tmean-terciles', title='',
                                 lat_range=None, lon_range=None,
                                 cbar_ends='triangular',
                                 tercile_type='normal', smoothing_factor=0,
                                 cbar_type='tercile', fill_coastal_vals=False):
    """
    Plots below, near, and above normal (median) terciles to the screen.

    Parameters
    ----------

    - below (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data
    - near (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data
    - above (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data
    - grid (Grid object)
        - See [data_utils.gridded.grid.Grid](
        ../gridded/grid.m.html#data_utils.gridded.grid.Grid)
    {}

    Examples
    --------

        >>> from data_utils.gridded.plotting import plot_tercile_probs_to_screen
        >>> from data_utils.gridded.grid import Grid
        >>> from mpp.poe import poe_to_terciles
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> ptiles = [
        ...  1,  2,  5, 10, 15,
        ... 20, 25, 33, 40, 50,
        ... 60, 67, 75, 80, 85,
        ... 90, 95, 98, 99]
        >>> grid = Grid('2deg-conus')
        >>> data = np.fromfile(resource_filename('data_utils',
        ... 'lib/example-tmean-fcst.bin'), dtype='float32')
        >>> data = np.reshape(data, (len(ptiles), grid.num_y * grid.num_x))
        >>> below, near, above = poe_to_terciles(data, ptiles)
        >>> plot_tercile_probs_to_screen(below, near, above, grid)  # doctest: +SKIP
    """
    # --------------------------------------------------------------------------
    # Get dictionary of kwargs for child function
    #
    # Use locals() function to get all defined vars
    kwargs = locals()
    # Remove positional args
    del kwargs['below']
    del kwargs['near']
    del kwargs['above']
    del kwargs['grid']
    # --------------------------------------------------------------------------
    # Reshape arrays if necessary
    #
    if below.ndim == 1:
        below = np.reshape(below, (grid.num_y, grid.num_x))
    elif below.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    if near.ndim == 1:
        near = np.reshape(near, (grid.num_y, grid.num_x))
    elif near.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    if above.ndim == 1:
        above = np.reshape(above, (grid.num_y, grid.num_x))
    elif above.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    # --------------------------------------------------------------------------
    # Put terciles into a single array for plotting
    #
    all_probs = _put_terciles_in_one_array(below, near, above)
    # --------------------------------------------------------------------------
    # Convert all_probs into probabilities from 0-100
    #
    all_probs *= 100
    # --------------------------------------------------------------------------
    # Define *args for child function
    #
    args = [all_probs, grid]
    # --------------------------------------------------------------------------
    # Plot
    #
    plot_to_screen(*args, **kwargs)


def plot_tercile_probs_to_file(below, near, above, grid, file,
                               levels=[-90, -80, -70, -60, -50, -40, -33, 33,
                                       40, 50, 60, 70, 80, 90],
                               projection='equal-area', region='US',
                               colors=None, title='',
                               lat_range=None, lon_range=None,
                               cbar_ends='triangular', tercile_type='normal',
                               smoothing_factor=0, cbar_type='tercile',
                               fill_coastal_vals=False):
    """
    Plots below, near, and above normal (median) terciles to a file.

    Parameters
    ----------

    - below (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data
    - near (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data
    - above (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data
    - grid (Grid object)
        - See [data_utils.gridded.grid.Grid](
        ../gridded/grid.m.html#data_utils.gridded.grid.Grid)
    - file (str)
        - File name to save plot to
    {}

    Examples
    --------

        >>> from data_utils.gridded.plotting import plot_tercile_probs_to_file
        >>> from data_utils.gridded.grid import Grid
        >>> from mpp.poe import poe_to_terciles
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> ptiles = [
        ...  1,  2,  5, 10, 15,
        ... 20, 25, 33, 40, 50,
        ... 60, 67, 75, 80, 85,
        ... 90, 95, 98, 99]
        >>> grid = Grid('2deg-conus')
        >>> data = np.fromfile(resource_filename('data_utils',
        ... 'lib/example-tmean-fcst.bin'), dtype='float32')
        >>> data = np.reshape(data, (len(ptiles), grid.num_y * grid.num_x))
        >>> below, near, above = poe_to_terciles(data, ptiles)
        >>> plot_tercile_probs_to_file(below, near, above, grid, 'out.png')  # doctest: +SKIP
    """
    # --------------------------------------------------------------------------
    # Get dictionary of kwargs for child function
    #
    # Use locals() function to get all defined vars
    kwargs = locals()
    # Remove positional args
    del kwargs['below']
    del kwargs['near']
    del kwargs['above']
    del kwargs['grid']
    del kwargs['file']
    # --------------------------------------------------------------------------
    # Reshape arrays if necessary
    #
    if below.ndim == 1:
        below = np.reshape(below, (grid.num_y, grid.num_x))
    elif below.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    if near.ndim == 1:
        near = np.reshape(near, (grid.num_y, grid.num_x))
    elif near.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    if above.ndim == 1:
        above = np.reshape(above, (grid.num_y, grid.num_x))
    elif above.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    # --------------------------------------------------------------------------
    # Put terciles into a single array for plotting
    #
    all_probs = _put_terciles_in_one_array(below, near, above)
    # --------------------------------------------------------------------------
    # Convert all_probs into probabilities from 0-100
    #
    all_probs *= 100
    # --------------------------------------------------------------------------
    # Define *args for child function
    #
    args = [all_probs, grid, file]
    # --------------------------------------------------------------------------
    # Plot
    #
    plot_to_file(*args, **kwargs)


def _show_plot():
    """
    Shows an existing plot that was created using `mpl_toolkits.basemap`
    """
    # Plot data
    matplotlib.pyplot.show()


def _save_plot(file, dpi=200):
    """Saves an existing plot that was created using `mpl_toolkits.basemap`
    to a file.

    Parameters
    ----------

    - file (str)
        - File name to save plot to
    - dpi (float, optional)
        - dpi of the image (higher means higher resolution). By default `dpi =
          200`.
    """
    matplotlib.pyplot.savefig(file, dpi=dpi, bbox_inches='tight')


def _put_terciles_in_one_array(below, near, above):
    # Make an empty array to store above, near, and below
    all_probs = np.empty(below.shape)
    all_probs[:] = np.nan
    # Insert belows where they are the winning category and above 33%
    all_probs = np.where((below > 0.333) & (below > above), -1*below, all_probs)
    # Insert aboves where they are the winning category and above 33%
    all_probs = np.where((above > 0.333) & (above > below), above, all_probs)
    # Insert nears where neither above or below are above 33%
    all_probs = np.where((below <= 0.333) & (above <= 0.333), 0, all_probs)
    # Return all_probs
    return all_probs


def _get_colors(colors):
    # Colors should be set to '[var]-[plot-type]'
    if colors == 'tmean-terciles':
        return [
            # Below normal (blues)
            [0.01, 0.31, 0.48],
            [0.02, 0.44, 0.69],
            [0.21, 0.56, 0.75],
            [0.45, 0.66, 0.81],
            [0.65, 0.74, 0.86],
            [0.82, 0.82, 0.9],
            [0.95, 0.93, 0.96],
            # Near normal (grey)
            [0.75, 0.75, 0.75],
            # Above normal (reds)
            [1., 0.94, 0.85],
            [0.99, 0.83, 0.62],
            [0.99, 0.73, 0.52],
            [0.99, 0.55, 0.35],
            [0.94, 0.4, 0.28],
            [0.84, 0.19, 0.12],
            [0.6, 0., 0.]
        ]
    else:
        raise ValueError('supplied colors parameter not supported, see API '
                         'docs')


_make_plot.__doc__ = _make_plot.__doc__.format(_docstring_kwargs)
plot_to_screen.__doc__ = plot_to_screen.__doc__.format(_docstring_kwargs)
plot_to_file.__doc__ = plot_to_file.__doc__.format(_docstring_kwargs)
plot_tercile_probs_to_file.__doc__ = \
    plot_tercile_probs_to_file.__doc__.format(_docstring_kwargs)
plot_tercile_probs_to_screen.__doc__ = \
    plot_tercile_probs_to_screen.__doc__.format(_docstring_kwargs)
