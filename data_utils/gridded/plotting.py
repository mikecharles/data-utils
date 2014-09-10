"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib.pyplot
import numpy

import data_utils.gridded.grid


def plot_to_screen(data, grid, levels=None, title=None):
    """Plots the given data and displays on-screen.

    Essentially makes calls to :func:`make_plot` and :func:`show_plot` to do
    the work

    Parameters
    ----------
    data : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    grid : Grid
        :class:`~data_utils.gridded.grid.Grid`
    title : str, optional
        Title of the resulting plot
    """
    make_plot(data, grid, levels=levels, title=title)
    show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(data, grid, file, dpi=200, levels=None, title=None):
    """Plots the given data and saves to a file.

    Essentially makes calls to :func:`make_plot` and :func:`save_plot` to do
    the work

    Parameters
    ----------
    data : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    grid : Grid
        :class:`~data_utils.gridded.grid.Grid`
    file : str
        File name to save plot to
    dpi : float, optional
        dpi of the image (higher means higher resolution). By default `dpi =
        200`.
    title : str, optional
        Title of the resulting plot
    """
    make_plot(data, grid, levels=levels, title=title)
    save_plot(file, dpi)
    matplotlib.pyplot.close("all")


def make_plot(data, grid, levels=None, title=None):
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
    title : str (optional)
        Title of the resulting plot
    """
    # Convert the ll_corner and res to arrays of lons and lats
    start_lat, start_lon = grid.ll_corner
    end_lat, end_lon = grid.ur_corner
    lats = numpy.arange(start_lat, end_lat + grid.res, grid.res)
    lons = numpy.arange(start_lon, end_lon + grid.res, grid.res)

    # Create a 2-d mesh array of lons and lats for pyplot
    lons, lats = numpy.meshgrid(lons, lats)

    # Create Basemap
    fig, ax = matplotlib.pyplot.subplots()
    m = mpl_toolkits.basemap.Basemap(llcrnrlon=0, llcrnrlat=-80, urcrnrlon=360,
                                     urcrnrlat=80, projection='mill', ax=ax)
    m.drawcoastlines(linewidth=1.25)
    m.drawparallels(numpy.arange(-80, 81, 20), labels=[1, 1, 0, 0])
    m.drawmeridians(numpy.arange(0, 360, 60), labels=[0, 0, 0, 1])
    m.drawmapboundary(fill_color='#DDDDDD')

    # Plot data
    if levels:
        plot = m.contourf(lons, lats, data, levels, latlon=True)
    else:
        plot = m.contourf(lons, lats, data, latlon=True)

    # Add labels
    fontsize = 14
    matplotlib.pyplot.title(title, fontsize=fontsize)

    # Add a colorbar
    matplotlib.pyplot.colorbar(plot, orientation="horizontal")


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
