"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib.pyplot
import matplotlib.colors
import matplotlib.cm
import matplotlib.colorbar
import numpy as np

import data_utils.gridded.grid


def plot_to_screen(data, grid, levels=None, colors=None, title=None,
                   lat_range=(-90, 90), lon_range=(0, 360)):
    """Plots the given data and displays on-screen.

    Essentially makes calls to :func:`make_plot` and :func:`show_plot` to do
    the work

    Parameters
    ----------
    data : array_like
        1- or 2-dimensional (lat x lon) Numpy array of data to plot
    grid : Grid
        :class:`~data_utils.gridded.grid.Grid`
    levels : list (optional)
        List of levels to shade/contour.
    colors : list of lists
        List of colors, each color being a list of RGB values from 0 to 1
    title : str, optional
        Title of the resulting plot
    lat_range : tuple, optional
        Range of latitude values to plot
    lon_range : tuple, optional
        Range of longitude values to plot

    Examples
    --------

    >>> import numpy as np
    >>> from data_utils.gridded.plotting import plot_to_screen
    >>> grid = data_utils.gridded.grid.Grid('1deg_global')
    >>> A = np.fromfile('tmax_01d_20130101.bin','float32')
    >>> A = np.reshape(A, (grid.num_y, grid.num_x))
    >>> A[A == -999] = np.nan
    >>> plot_to_screen(A, grid, lat_range=(20, 75), lon_range=(180, 310))
    """

    # Reshape array if necessary
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')

    make_plot(data, grid, levels=levels, colors=colors, title=title,
              lat_range=lat_range, lon_range=lon_range)
    show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(data, grid, file, dpi=200, levels=None, colors=None,
                 title=None, lat_range=(-90, 90), lon_range=(0, 360)):
    """Plots the given data and saves to a file.

    Essentially makes calls to :func:`make_plot` and :func:`save_plot` to do
    the work

    Parameters
    ----------
    data : array_like
        1- or 2-dimensional (lat x lon) Numpy array of data to plot
    grid : Grid
        :class:`~data_utils.gridded.grid.Grid`
    levels : list (optional)
        List of levels to shade/contour.
    colors : list of lists
        List of colors, each color being a list of RGB values from 0 to 1
    file : str
        File name to save plot to
    dpi : float, optional
        dpi of the image (higher means higher resolution). By default `dpi =
        200`.
    title : str, optional
        Title of the resulting plot
    lat_range : tuple, optional
        Range of latitude values to plot
    lon_range : tuple, optional
        Range of longitude values to plot

    Examples
    --------
    >>> import numpy as np
    >>> from data_utils.gridded.plotting import plot_to_file
    >>> grid = data_utils.gridded.grid.Grid('1deg_global')
    >>> A = np.fromfile('tmax_01d_20130101.bin','float32')
    >>> A = np.reshape(A, (grid.num_y, grid.num_x))
    >>> A[A == -999] = np.nan
    >>> plot_to_file(A, grid, 'test.png', lat_range=(20, 75), lon_range=(180, 310))
    """

    # Reshape array if necessary
    if data.ndim == 1:
        data = np.reshape(data, (grid.num_y, grid.num_x))
    elif data.ndim != 2:
        raise ValueError('data array must have 1 or 2 dimensions')

    make_plot(data, grid, levels=levels, colors=colors, title=title, lat_range=lat_range, lon_range=lon_range)
    save_plot(file, dpi)
    matplotlib.pyplot.close("all")


def make_plot(data, grid, levels=None, colors=None, title=None, lat_range=(-90, 90), lon_range=(0, 360)):
    """Creates a plot object using
    `mpl_toolkits.basemap <http://matplotlib.org/basemap/users/examples.html>`_.
    Nothing is actually plotted. Usually you'd want to call :func:`show_plot`
    or :func:`save_plot` after this.

    Parameters
    ----------
    data : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    grid : Grid
        :class:`~data_utils.gridded.grid.Grid`
    levels : list (optional)
        List of levels to shade/contour.
    colors : list of lists
        List of colors, each color being a list of RGB values from 0 to 1
    title : str (optional)
        Title of the resulting plot
    lat_range : tuple, optional
        Range of latitude values to plot
    lon_range : tuple, optional
        Range of longitude values to plot
    """
    # Check args
    if (colors and not levels) or (levels and not colors):
        raise ValueError('The "levels" and "colors" parameters must both be '
                         'defined together or not at all')
    # Convert the ll_corner and res to arrays of lons and lats
    start_lat, start_lon = grid.ll_corner
    end_lat, end_lon = grid.ur_corner
    lats = np.arange(start_lat, end_lat + grid.res, grid.res)
    lons = np.arange(start_lon, end_lon + grid.res, grid.res)

    # Create a 2-d mesh array of lons and lats for pyplot
    lons, lats = np.meshgrid(lons, lats)

    # Create Basemap
    fig, ax = matplotlib.pyplot.subplots()
    m = mpl_toolkits.basemap.Basemap(llcrnrlon=lon_range[0],
                                     llcrnrlat=lat_range[0],
                                     urcrnrlon=lon_range[1],
                                     urcrnrlat=lat_range[1],
                                     projection='mill',
                                     ax=ax,
                                     resolution='l')
    m.drawcoastlines(linewidth=1)
    m.drawparallels(np.arange(lat_range[0], lat_range[1]+1, 10), labels=[1, 1, 0, 0])
    m.drawmeridians(np.arange(lon_range[0], lon_range[1]+1, 10), labels=[0, 0, 0, 1])
    m.drawmapboundary(fill_color='#DDDDDD')
    m.drawstates()
    m.drawcountries()

    # Plot data
    if levels:
        plot = m.contourf(lons, lats, data, levels, latlon=True, colors=colors)
    else:
        plot = m.contourf(lons, lats, data, latlon=True)

    # Add labels
    fontsize = 14
    matplotlib.pyplot.title(title, fontsize=fontsize)

    # Add a colorbar
    matplotlib.pyplot.colorbar(plot, orientation="horizontal")
    # cb = matplotlib.colorbar.ColorbarBase(plot, norm=norm, boundaries=[-10]+bounds+[10], extend='both', extendfrac='auto', ticks=bounds, spacing='uniform', orientation='horizontal')
    # cb.set_label('TEST')


def show_plot():
    """Shows an existing plot that was created using
    `mpl_toolkits.basemap <http://matplotlib.org/basemap/users/examples.html>`_
    """
    # Plot data
    matplotlib.pyplot.show()


def save_plot(file, dpi=200):
    """Saves an existing plot that was created using
    `mpl_toolkits.basemap <http://matplotlib.org/basemap/users/examples.html>`_
    to a file.

    Parameters
    ----------
    file : str
        File name to save plot to
    dpi : float, optional
        dpi of the image (higher means higher resolution). By default `dpi =
        200`.
    """
    matplotlib.pyplot.savefig(file, dpi=dpi, bbox_inches='tight')


def plot_tercile_probs(below, near, above, grid, levels=None, colors=None,
                       title=None, lat_range=(-90, 90), lon_range=(0, 360)):
    # Make an empty array to store above, near, and below
    all_probs = np.empty(below.shape)
    all_probs[:] = np.nan
    # Insert belows where they are the winning category and above 33%
    all_probs = np.where((below > 0.333) & (below > above), -1*below, all_probs)
    # Insert aboves where they are the winning category and above 33%
    all_probs = np.where((above > 0.333) & (above > below), above, all_probs)
    # Insert nears where neither above or below are above 33%
    all_probs = np.where((below <= 0.333) & (above <= 0.333), 0, all_probs)
    # Convert all_probs into probabilities from 0-100
    all_probs *= 100
    # Plot
    plot_to_screen(all_probs, grid, levels=levels, colors=colors,
                   title=title, lat_range=(20, 70), lon_range=(200, 300))
