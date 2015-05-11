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

import data_utils.gridded.grid


def plot_to_screen(data, grid, levels=None, colors=None, title=None,
                   lat_range=(-90, 90), lon_range=(0, 360),
                   cbar_ends='triangular', tercile_type='normal',
                   smoothing_factor=0, cbar_type='normal'):
    """
    Plots the given data and displays on-screen.

    Essentially makes calls to :func:`make_plot` and :func:`show_plot` to do
    the work

    Parameters
    ----------

    - data (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data to plot
    - grid (Grid
        - `data_utils.gridded.grid.Grid`
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
    - cbar_type (strin, optional)
        - Type of colorbar ('normal' for a normal colorbar, or 'tercile' for a
        tercile colorbar with 3 color ranges)
    - tercile_type (str, optional)
        - Type of tercile ('normal' or 'median')
    - smoothing_factor (float, optional)
        - Level of smoothing (gaussian filter, this represents the kernel
        width - may need to experiment with value)

    Examples
    --------

        #!python
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> from data_utils.gridded.plotting import plot_to_screen
        >>> from data_utils.gridded.grid import Grid
        >>> grid = Grid('1deg_global')
        >>> A = np.fromfile(resource_filename('data_utils', 'lib/tmax.bin'),
        ... dtype='float32')
        >>> A = np.reshape(A, (grid.num_y, grid.num_x))
        >>> A[A == -999] = np.nan
        >>> plot_to_screen(A, grid)
    """

    # Reshape array if necessary
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')

    make_plot(data, grid, levels=levels, colors=colors, title=title,
              lat_range=lat_range, lon_range=lon_range, cbar_ends=cbar_ends,
              tercile_type=tercile_type, smoothing_factor=smoothing_factor,
              cbar_type=cbar_type)
    show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(data, grid, file, dpi=200, levels=None, colors=None,
                 title=None, lat_range=(-90, 90), lon_range=(0, 360),
                 cbar_ends='triangular', tercile_type='normal',
                 smoothing_factor=0, cbar_type='normal'):
    """
    Plots the given data and saves to a file.

    Essentially makes calls to :func:`make_plot` and :func:`save_plot` to do
    the work

    Parameters
    ----------

    - data (array_like)
        - 1- or 2-dimensional (lat x lon) Numpy array of data to plot
    - grid (Grid)
        - :class:`~data_utils.gridded.grid.Grid`
    - levels (list, optional)
        - List of levels to shade/contour.
    - colors (list of lists)
        - List of colors, each color being a list of RGB values from 0 to 1
    - file (str)
        - File name to save plot to
    - dpi (float, optional)
        - dpi of the image (higher means higher resolution). By default `dpi =
        200`.
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
    - cbar_type (strin, optional)
        - Type of colorbar ('normal' for a normal colorbar, or 'tercile' for a
          tercile colorbar with 3 color ranges)
    - tercile_type (str, optional)
        - Type of tercile ('normal' or 'median')
    - smoothing_factor (float, optional)
        - Level of smoothing (gaussian filter, this represents the kernel width -
          may need to experiment with value)

    Examples
    --------

        #!python
        >>> from pkg_resources import resource_filename
        >>> import numpy as np
        >>> from data_utils.gridded.plotting import plot_to_file
        >>> from data_utils.gridded.grid import Grid
        >>> grid = Grid('1deg_global')
        >>> A = np.fromfile(resource_filename('data_utils', 'lib/tmax.bin'),
        ... dtype='float32')
        >>> A = np.reshape(A, (grid.num_y, grid.num_x))
        >>> A[A == -999] = np.nan
        >>> plot_to_file(A, grid, 'test.png')
    """

    # Set backend to Agg which won't require X11
    matplotlib.pyplot.switch_backend('Agg')

    # Reshape array if necessary
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')

    make_plot(data, grid, levels=levels, colors=colors, title=title,
              lat_range=lat_range, lon_range=lon_range, cbar_ends=cbar_ends,
              tercile_type=tercile_type, smoothing_factor=smoothing_factor,
              cbar_type=cbar_type)
    save_plot(file, dpi)
    matplotlib.pyplot.close("all")


def make_plot(data, grid, levels=None, colors=None, title=None, lat_range=(
        -90, 90), lon_range=(0, 360), cbar_ends='triangular',
              tercile_type='normal', projection='lcc', smoothing_factor=0,
              cbar_type='normal'):
    """
    Creates a plot object using `mpl_toolkits.basemap`

    Nothing is actually plotted. Usually you'd want to call
    `data_utils.gridded.plotting.show_plot` or
    `data_utils.gridded.plotting.save_plot` after this.

    Parameters
    ----------

    - data (2-d array)
        - 2-dimensional (lat x lon) Numpy array of data to plot
    - grid (Grid)
        - `data_utils.gridded.grid.Grid`
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
    - cbar_type (str, optional)
        - Type of colorbar ('normal' for a normal colorbar, or 'tercile' for a
          tercile colorbar with 3 color ranges)
    - tercile_type (str, optional)
        - Type of tercile ('normal' or 'median')
    - smoothing_factor (float, optional)
        - Level of smoothing (gaussian filter, this represents the kernel
        width - may need to experiment with value)
    """

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


def show_plot():
    """
    Shows an existing plot that was created using `mpl_toolkits.basemap`
    """
    # Plot data
    matplotlib.pyplot.show()


def save_plot(file, dpi=200):
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


def plot_tercile_probs_to_screen(below, near, above, grid, levels=None,
                       colors='tmean_colors', title=None, lat_range=(-90, 90),
                       lon_range=(0, 360), cbar_ends='triangular',
                       tercile_type='normal', smoothing_factor=0,
                       cbar_type='tercile'):
    # Get colors
    colors = get_colors(colors)

    # Put terciles into a single array for plotting
    all_probs = put_terciles_in_one_array(below, near, above)

    # Convert all_probs into probabilities from 0-100
    all_probs *= 100
    # Plot
    plot_to_screen(all_probs, grid, levels=levels, colors=colors,
                   title=title, cbar_ends=cbar_ends,
                   tercile_type=tercile_type,
                   smoothing_factor=smoothing_factor, cbar_type=cbar_type)


def plot_tercile_probs_to_file(below, near, above, grid, file, levels=None,
                                 colors='tmean_colors', title=None,
                                 lat_range=(-90, 90), lon_range=(0, 360),
                                 cbar_ends='triangular',
                                 tercile_type='normal', smoothing_factor=0,
                                 cbar_type='tercile'):
    # Get colors
    colors = get_colors(colors)

    # Put terciles into a single array for plotting
    all_probs = put_terciles_in_one_array(below, near, above)

    # Convert all_probs into probabilities from 0-100
    all_probs *= 100
    # Plot
    plot_to_file(all_probs, grid, file, levels=levels, colors=colors,
                 title=title, cbar_ends=cbar_ends, tercile_type=tercile_type,
                 smoothing_factor=smoothing_factor, cbar_type=cbar_type)


def put_terciles_in_one_array(below, near, above):
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


def get_colors(colors):
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
