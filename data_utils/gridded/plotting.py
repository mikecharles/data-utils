"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import scipy.ndimage
import math


# ------------------------------------------------------------------------------
# Setup reusable docstring
#
_docstring_kwargs = """
    - levels (list, optional)
        - List of levels to shade/contour.
    - colors (list of lists)
        - List of colors, each color being a list of RGB values from 0 to 1
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


def plot_to_screen(data, grid, levels=None, colors=None, title=None,
                   lat_range=(-90, 90), lon_range=(0, 360),
                   cbar_ends='triangular', tercile_type='normal',
                   smoothing_factor=0, cbar_type='normal'):
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
    # Define *args to pass to child function
    #
    args = [data, grid]
    # --------------------------------------------------------------------------
    # Reshape array if necessary
    #
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')
    # --------------------------------------------------------------------------
    # Call _make_plot()
    #
    _make_plot(*args, **kwargs)
    _show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(data, grid, file, dpi=200, levels=None, colors=None,
                 title=None, lat_range=(-90, 90), lon_range=(0, 360),
                 cbar_ends='triangular', tercile_type='normal',
                 smoothing_factor=0, cbar_type='normal'):
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
    colors = kwargs['colors']
    title = kwargs['title']
    lat_range = kwargs['lat_range']
    lon_range = kwargs['lon_range']
    cbar_ends = kwargs['cbar_ends']
    cbar_type = kwargs['cbar_type']
    tercile_type = kwargs['tercile_type']
    smoothing_factor = kwargs['smoothing_factor']

    # Check args
    if colors and not levels:
        raise ValueError('The "levels" argument must be set if the "colors" '
                         'argument is set')

    # Convert the ll_corner and res to arrays of lons and lats
    start_lat, start_lon = grid.ll_corner
    end_lat, end_lon = grid.ur_corner
    lats = np.arange(start_lat, end_lat + grid.res, grid.res)
    lons = np.arange(start_lon, end_lon + grid.res, grid.res)

    # Create a 2-d mesh array of lons and lats for pyplot
    lons, lats = np.meshgrid(lons, lats)

    # Create Basemap
    fig, ax = matplotlib.pyplot.subplots()
    projection = 'lcc'
    if projection == 'mercator':
        m = mpl_toolkits.basemap.Basemap(llcrnrlon=lon_range[0],
                                         llcrnrlat=lat_range[0],
                                         urcrnrlon=lon_range[1],
                                         urcrnrlat=lat_range[1],
                                         projection='mill',
                                         ax=ax,
                                         resolution='l')
        m.drawcoastlines(linewidth=1)
        m.drawparallels(np.arange(lat_range[0], lat_range[1]+1, 10),
                        labels=[1, 1, 0, 0], fontsize=9)
        m.drawmeridians(np.arange(lon_range[0], lon_range[1]+1, 10),
                        labels=[0, 0, 0, 1], fontsize=9)
        m.drawmapboundary(fill_color='#DDDDDD')
        m.drawstates()
        m.drawcountries()
    elif projection == 'lcc':
        m = mpl_toolkits.basemap.Basemap(width=8000000, height=6600000,
                                         lat_0=53., lon_0=-100.,
                                         projection='lcc', ax=ax,
                                         resolution='l')
        m.drawcoastlines(linewidth=1)
        # m.drawparallels(np.arange(lat_range[0], lat_range[1] + 1, 10),
        #                 labels=[1, 1, 0, 0], fontsize=9)
        # m.drawmeridians(np.arange(lon_range[0], lon_range[1] + 1, 10),
        #                 labels=[0, 0, 0, 1], fontsize=9)
        m.drawmapboundary(fill_color='#DDDDDD')
        m.drawstates()
        m.drawcountries()

    else:
        raise ValueError('Supported projections: \'mercator\', \'stereo\'')

    # Smooth data
    data = scipy.ndimage.filters.gaussian_filter(data, smoothing_factor)

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


def plot_tercile_probs_to_screen(below, near, above, grid,
                                 levels=[-90, -80, -70, -60, -50, -40, -33, 33,
                                         40, 50, 60, 70, 80, 90],
                                 colors='tmean_colors', title=None,
                                 lat_range=(-90, 90), lon_range=(0, 360),
                                 cbar_ends='triangular', tercile_type='normal',
                                 smoothing_factor=0, cbar_type='tercile'):
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
    # Get colors
    #
    colors = _get_colors(colors)
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
                               colors='tmean_colors', title=None,
                               lat_range=(-90, 90), lon_range=(0, 360),
                               cbar_ends='triangular',
                               tercile_type='normal', smoothing_factor=0,
                               cbar_type='tercile'):
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
    # Get colors
    #
    colors = _get_colors(colors)
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
    # Colors should be set to '[var]_colors'
    if colors == 'tmean_colors':
        return [
            # Below normal (blues)
            [0.03, 0.27, 0.58],
            [0.13, 0.44, 0.71],
            [0.26, 0.57, 0.78],
            [0.42, 0.68, 0.84],
            [0.62, 0.79, 0.88],
            [0.78, 0.86, 0.94],
            [0.94, 0.95, 1.00],
            # Near normal (grey)
            [0.75, 0.75, 0.75],
            # Above normal (reds)
            [1.00, 0.9, 0.85],
            [0.99, 0.73, 0.63],
            [0.99, 0.57, 0.45],
            [0.98, 0.42, 0.29],
            [0.94, 0.23, 0.17],
            [0.80, 0.09, 0.11],
            [0.60, 0.00, 0.05]
        ]
    else:
        raise ValueError('Supported vars for default color scales (colors=['
                         'var]_colors): tmean, precip')


_make_plot.__doc__ = _make_plot.__doc__.format(_docstring_kwargs)
plot_to_screen.__doc__ = plot_to_screen.__doc__.format(_docstring_kwargs)
plot_to_file.__doc__ = plot_to_file.__doc__.format(_docstring_kwargs)
plot_tercile_probs_to_file.__doc__ = \
    plot_tercile_probs_to_file.__doc__.format(_docstring_kwargs)
plot_tercile_probs_to_screen.__doc__ = \
    plot_tercile_probs_to_screen.__doc__.format(_docstring_kwargs)
