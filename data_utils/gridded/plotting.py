"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib.pyplot
import numpy

import data_utils.gridded.grid


def plot_to_screen(data, grid, levels=None, title=None, lat_range=(-90, 90), lon_range=(0, 360)):
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
    lat_range : tuple, optional
        Range of latitude values to plot
    lon_range : tuple, optional
        Range of longitude values to plot

    Examples
    --------

    >>> import numpy
    >>> import data_utils.gridded.plotting
    >>> grid = data_utils.gridded.grid.Grid('1deg_global')
    >>> A = numpy.fromfile('/export/cpc-lw-mcharles/mcharles/data/observations/land_air/short_range/global/merged_tmax/1deg/01d/2013/01/01/tmax_01d_20130101.bin','float32')
    >>> A = numpy.reshape(A, (grid.num_y, grid.num_x))
    >>> A[A == -999] = numpy.nan
    >>> data_utils.gridded.plotting.plot_to_screen(A, grid, lat_range=(20, 75), lon_range=(180, 310))
    """

    make_plot(data, grid, levels=levels, title=title, lat_range=lat_range, lon_range=lon_range)
    show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(data, grid, file, dpi=200, levels=None, title=None, lat_range=(-90, 90), lon_range=(0, 360)):
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
    lat_range : tuple, optional
        Range of latitude values to plot
    lon_range : tuple, optional
        Range of longitude values to plot

    Examples
    --------
    >>> import numpy
    >>> import data_utils.gridded.plotting
    >>> grid = data_utils.gridded.grid.Grid('1deg_global')
    >>> A = numpy.fromfile('/export/cpc-lw-mcharles/mcharles/data/observations/land_air/short_range/global/merged_tmax/1deg/01d/2013/01/01/tmax_01d_20130101.bin','float32')
    >>> A = numpy.reshape(A, (grid.num_y, grid.num_x))
    >>> A[A == -999] = numpy.nan
    >>> data_utils.gridded.plotting.plot_to_file(A, grid, 'test.png', lat_range=(20, 75), lon_range=(180, 310))

    """
    make_plot(data, grid, levels=levels, title=title, lat_range=lat_range, lon_range=lon_range)
    save_plot(file, dpi)
    matplotlib.pyplot.close("all")


def make_plot(data, grid, levels=None, title=None, lat_range=(-90, 90), lon_range=(0, 360)):
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
    lat_range : tuple, optional
        Range of latitude values to plot
    lon_range : tuple, optional
        Range of longitude values to plot
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
    m = mpl_toolkits.basemap.Basemap(llcrnrlon=lon_range[0],
                                     llcrnrlat=lat_range[0],
                                     urcrnrlon=lon_range[1],
                                     urcrnrlat=lat_range[1],
                                     projection='mill',
                                     ax=ax,
                                     resolution='l')
    m.drawcoastlines(linewidth=1)
    m.drawparallels(numpy.arange(lat_range[0], lat_range[1]+1, 10), labels=[1, 1, 0, 0])
    m.drawmeridians(numpy.arange(lon_range[0], lon_range[1]+1, 10), labels=[0, 0, 0, 1])
    m.drawmapboundary(fill_color='#DDDDDD')
    m.drawstates()
    m.drawcountries()

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
