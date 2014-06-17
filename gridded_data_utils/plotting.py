"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib.pyplot
import numpy


def plot_to_screen(grid, lats, lons, title=None):
    """Plots the given grid and displays on-screen.

    Essentially makes calls to :func:`make_plot` and :func:`show_plot` to do
    the work

    Parameters
    ----------
    grid : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    lats : 1-d array
        1-d array of latitudes corresponding to the grid
    lons : 1-d array
        1-d array of longitudes corresponding to the grid
    title : str, optional
        Title of the resulting plot
    """
    make_plot(grid, lats, lons, title)
    show_plot()


def plot_to_file(grid, lats, lons, file, dpi=200, title=None):
    """Plots the given grid and saves to a file.

    Essentially makes calls to :func:`make_plot` and :func:`save_plot` to do
    the work

    Parameters
    ----------
    grid : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    lats : 1-d array
        1-d array of latitudes corresponding to the grid
    lons : 1-d array
        1-d array of longitudes corresponding to the grid
    file : str
        File name to save plot to
    dpi : float, optional
        dpi of the image (higher means higher resolution). By default `dpi =
        200`.
    title : str, optional
        Title of the resulting plot
    """
    make_plot(grid, lats, lons, title)
    save_plot(file, dpi)


def make_plot(grid, lats, lons, title=None):
    """Creates a plot object using
    `mpl_toolkits.basemap <http://matplotlib.org/basemap/users/examples.html>`_.
    Nothing is actually plotted. Usually you'd want to call :func:`show_plot`
    or :func:`save_plot` after this.

    Parameters
    ----------
    grid : 2-d array
        2-dimensional (lat x lon) Numpy array of data to plot
    lats : 1-d array
        1-d array of latitudes corresponding to the grid
    lons : 1-d array
        1-d array of longitudes corresponding to the grid
    title : str, optional
        Title of the resulting plot
    """
    # Convert 1-d arrays of lats and lons into a 2-d mesh grid for pyplot
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
