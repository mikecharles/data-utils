"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib.pyplot
import numpy


def plot_to_screen(grid, ll_corner, ur_corner, res, grid_type="latlon", title=None):
    """Plots the given grid and displays on-screen.

    Essentially makes calls to :func:`make_plot` and :func:`show_plot` to do
    the work

    Parameters
    ----------
    grid : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    ll_corner : tuple of floats
        Lower-left corner of the grid, formatted as (lat, lon)
    ur_corner : tuple of floats
        Upper-right corner of the grid, formatted as (lat, lon)
    res : float
        Grid resolution (in km if ``grid_type="even"``, in degrees if
        ``grid_type="latlon"``)
    grid_type : str
        Grid type. Possible values are:
            - latlon : Latlon grid
            - equal : Equally-spaced square grid
    title : str, optional
        Title of the resulting plot
    """
    make_plot(grid, ll_corner, ur_corner, res, grid_type, title)
    show_plot()


def plot_to_file(grid, ll_corner, ur_corner, res, file, grid_type="latlon", dpi=200, title=None):
    """Plots the given grid and saves to a file.

    Essentially makes calls to :func:`make_plot` and :func:`save_plot` to do
    the work

    Parameters
    ----------
    grid : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    ll_corner : tuple of floats
        Lower-left corner of the grid, formatted as (lat, lon)
    ur_corner : tuple of floats
        Upper-right corner of the grid, formatted as (lat, lon)
    res : float
        Grid resolution (in km if ``grid_type="even"``, in degrees if
        ``grid_type="latlon"``)
    file : str
        File name to save plot to
    grid_type : str
        Grid type. Possible values are:
            - latlon : Latlon grid
            - equal : Equally-spaced square grid
    dpi : float, optional
        dpi of the image (higher means higher resolution). By default `dpi =
        200`.
    title : str, optional
        Title of the resulting plot
    """
    make_plot(grid, ll_corner, ur_corner, res, grid_type, title)
    save_plot(file, dpi)


def make_plot(grid, ll_corner, ur_corner, res, grid_type="latlon", title=None):
    """Creates a plot object using
    `mpl_toolkits.basemap <http://matplotlib.org/basemap/users/examples.html>`_.
    Nothing is actually plotted. Usually you'd want to call :func:`show_plot`
    or :func:`save_plot` after this.

    Parameters
    ----------
    grid : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    ll_corner : tuple of floats
        Lower-left corner of the grid, formatted as (lat, lon)
    ur_corner : tuple of floats
        Upper-right corner of the grid, formatted as (lat, lon)
    res : float
        Grid resolution (in km if ``grid_type="even"``, in degrees if
        ``grid_type="latlon"``)
    grid_type : str
        Grid type. Possible values are:
            - latlon : Latlon grid
            - equal : Equally-spaced square grid
    title : str, optional
        Title of the resulting plot
    """
    # Convert the ll_corner and res to arrays of lons and lats
    start_lat, start_lon = ll_corner
    end_lat, end_lon = ur_corner
    lats = numpy.arange(start_lat, end_lat + res, res)
    lons = numpy.arange(start_lon, end_lon + res, res)

    # Create a 2-d mesh grid of lons and lats for pyplot
    lons, lats = numpy.meshgrid(lons, lats)

    # Create Basemap
    fig, ax = matplotlib.pyplot.subplots()
    m = mpl_toolkits.basemap.Basemap(llcrnrlon=0, llcrnrlat=-80, urcrnrlon=360,
                                     urcrnrlat=80, projection='mill', ax=ax)
    m.drawcoastlines(linewidth=1.25)
    m.drawparallels(numpy.arange(-80, 81, 20), labels=[1, 1, 0, 0])
    m.drawmeridians(numpy.arange(0, 360, 60), labels=[0, 0, 0, 1])
    m.drawmapboundary(fill_color='#DDDDDD')

    # Plot grid
    m.contourf(lons, lats, grid, latlon=True)

    # Add labels
    fontsize = 14
    matplotlib.pyplot.title(title, fontsize=fontsize)


def show_plot():
    """Shows an existing plot that was created using
    `mpl_toolkits.basemap <http://matplotlib.org/basemap/users/examples.html>`_
    """
    # Plot grid
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
