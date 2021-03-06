"""
Contains methods for plotting gridded data.
"""

from __future__ import print_function
import mpl_toolkits.basemap
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import scipy.ndimage
import math
from pkg_resources import resource_filename
from palettable.colorbrewer.sequential import Greens_7, YlOrBr_7, GnBu_7, BuGn_7
from data_utils.gridded.interpolation import interpolate
from data_utils.gridded.grid import Grid
from data_utils.gridded.interpolation import fill_outside_mask_borders
from data_utils.gridded.interpolation import smooth
import warnings

print(mpl_toolkits.basemap.__file__)
# ------------------------------------------------------------------------------
# Setup reusable docstring
#
_docstring_kwargs = """
    - levels (list, optional)
        - List of levels to shade/contour.
    - fill_colors (list of lists, or string)
        - Specifies the colors to be used to plot the data. It can either be:
            - A list of colors, each color being a list of RGB values from 0
            to 1 (ex. [[0.2, 0.2, 1],[0.4, 0.5, 0.8],[0.2, 0.2, 0.5]])
            - A tuple of matplotlib color args (string, float, rgb, etc), different levels will
            be plotted in different colors in the order specified.
            - A string specifying the variable and plot type. Supported values:
                - tmean-terciles
    - fill_alpha (number between 0 and 1, optional)
        - Alpha of the color fills - 0 is completely transparent, 1 is completly opaque
    - contour_colors (str or mpl_colors)
        - Color of contours
            - If None, then no contours are plotted
            - If string, like 'r' or 'red', contours will be plotted in this color
            - If a tuple of matplotlib color args (string, float, rgb, etc), different levels
            will be plotted in different colors in the order specified.
    - fill_first_field (bool, optional)
        - Whether to fill the first field plotted (default True)
            - If True, then the first field plotted will have filled contours - all subsequent
            fields will be contour-only
            - If False, then all fields plotted will be contour-only
    - contour_labels (bool, optional)
        - Whether contour labels are plotted (default False)
    - smoothing_factor (float, optional)
        - Level of smoothing (gaussian filter, this represents the kernel
        width in standard deviations - may need to experiment with value -
        generally between 0 and 2 should suffice)
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
    - cbar_color_spacing (str, optional)
        - Colorbar color spacing ('natural' will space the color gradient
        based on the gradient in levels [eg. faster change in levels will
        correspond to faster change in color], 'equal' will result in a
        uniform gradient in color [same change in color between 2 levels,
        regardless of the difference in the value of the levels])
    - cbar_label (str, optional)
        - Label for the colorbar - default is no label
    - cbar_tick_labels (list of strings, optional)
        - Specify how the cbar ticks should be labelled
    - tercile_type (str, optional)
        - Type of tercile ('normal' or 'median')
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
    fields = list(args)
    # Get **kwargs
    grid = kwargs['grid']
    levels = np.array(kwargs['levels']) if kwargs['levels'] else None
    projection = kwargs['projection']
    region = kwargs['region']
    fill_colors = kwargs['fill_colors']
    fill_first_field = kwargs['fill_first_field']
    title = kwargs['title']
    lat_range = kwargs['lat_range']
    lon_range = kwargs['lon_range']
    cbar_ends = kwargs['cbar_ends']
    cbar_type = kwargs['cbar_type']
    cbar_color_spacing = kwargs['cbar_color_spacing']
    tercile_type = kwargs['tercile_type']
    smoothing_factor = kwargs['smoothing_factor']
    fill_coastal_vals = kwargs['fill_coastal_vals']
    cbar_label = kwargs['cbar_label']
    cbar_tick_labels = kwargs['cbar_tick_labels']
    contour_colors = kwargs['contour_colors']
    contour_labels = kwargs['contour_labels']
    fill_alpha = kwargs['fill_alpha']

    # --------------------------------------------------------------------------
    # Check args
    #
    # Levels must be set if fill_colors is set
    if fill_colors and levels is None:
        raise ValueError('The "levels" argument must be set if the "fill_colors" '
                         'argument is set')
    # Make sure either region is set, or lat_range and lon_range are set
    if lat_range and lon_range:
        warnings.warn('lat_range and lon_range will override the given region')
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
    # If cbar_type is 'tercile', levels and cbar_tick_labels must both be set
    if cbar_type == 'tercile' and not (levels is not None and cbar_tick_labels):
        raise ValueError('When cbar_type==\'tercile\', levels and cbar_tick_labels '
                         'need to be set')
    # Make sure that certain args match the length of fields. For example, if 2 fields are
    # provided, then levels and contour_colors must have a length of 2 as well, as they apply to
    # each of the fields
    if levels is not None:
        if len(fields) > 1:
            if fill_first_field is False and levels.shape[0] != len(fields):
                raise ValueError('levels must be a list with a length matching the number of '
                                 'fields to plot')
    if contour_colors is not None and type(contour_colors) != list:
        contour_colors = [contour_colors]
    if len(fields) < 1:
        if fill_first_field is False and len(contour_colors) != len(fields):
            raise ValueError('contour_colors must be a list with a length matching the number of '
                             'fields to plot')
        elif fill_first_field is True and len(contour_colors) != (len(fields) - 1):
            raise ValueError('contour_colors must be a list with a length of 1 less than the the '
                             'number of fields to plot')
    # Set a default value for contour_colors
    if contour_colors is None:
        contour_colors = ['black'] * 2

    # --------------------------------------------------------------------------
    # Check colors variables
    #
    # If fill_colors is a string, obtain a colors list
    if isinstance(fill_colors, str):
        fill_colors = _get_colors(fill_colors)
    # Make sure there is 1 more color than levels
    if fill_colors:
        if len(fill_colors) != (len(levels[0]) + 1):
            raise ValueError('The number of fill_colors must be 1 greater than the '
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
            warnings.warn('lat_range and lon_range have no effect for '
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
        # TODO: Remove this once Matplotlib is updated to version 1.5,
        # which fixes this bug (see
        # https://github.com/matplotlib/matplotlib/issues/5209)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
    if smoothing_factor > 0:
        for i in range(len(fields)):
            fields[i] = smooth(fields[i], grid, smoothing_factor=smoothing_factor)

    # --------------------------------------------------------------------------
    # Fill coastal values (if requested)
    #
    if fill_coastal_vals:
        for i in range(len(fields)):
            # Datasets (particularly datasets on a course grid) that are masked out over the
            # water suffer from some missing grid points along the coast. The methodology below
            # remedies this, filling in those values while creating a clean mask along the water.
            # Shift the entire data array 1 grid point in each direction, and for every grid
            # point that becomes "unmissing" after shifting the grid (every grid point that has a
            # non-missing neighbor), set the value of the grid point to the neighbor's value.
            fields[i] = fill_outside_mask_borders(fields[i], passes=2)

            # Place data in a high-res grid so the ocean masking looks decent
            high_res_grid = Grid('1/6th-deg-global')
            fields[i] = interpolate(fields[i], grid, high_res_grid)
            lons, lats = np.meshgrid(high_res_grid.lons, high_res_grid.lats)
            # Mask the ocean values
            fields[i] = mpl_toolkits.basemap.maskoceans((lons - 360), lats, fields[i], inlands=True)

    if cbar_ends == 'triangular':
        extend='both'
    elif cbar_ends == 'square':
        extend='neither'
    else:
        raise ValueError('cbar_ends must be either \'triangular\' or '
                         '\'square\'')

    # ----------------------------------------------------------------------------------------------
    # Plot first field
    #
    if levels is not None:
        if len(fields) == 1:
            new_levels = levels
        else:
            new_levels = levels[0]
        if fill_colors:
            if fill_first_field:
                contours = m.contourf(lons, lats, fields[0], new_levels, latlon=True, extend=extend,
                                      colors=fill_colors, alpha=fill_alpha)
            else:
                contours = m.contour(lons, lats, fields[0], new_levels, latlon=True, extend=extend,
                                     colors=contour_colors[0], alpha=fill_alpha)
        else:
            if cbar_color_spacing == 'equal':
                cmap = matplotlib.cm.get_cmap('jet', len(new_levels))
                norm = matplotlib.colors.BoundaryNorm(new_levels, cmap.N)
                contours = m.contourf(lons, lats, fields[0], new_levels, latlon=True, extend=extend,
                                      cmap=cmap, norm=norm, alpha=fill_alpha)
            elif cbar_color_spacing == 'natural':
                contours = m.contourf(lons, lats, fields[0], new_levels, latlon=True, extend=extend,
                                      alpha=fill_alpha)
            else:
                raise ValueError('Incorrect setting for cbar_color_spacing - must be either '
                                 '\'equal\' or \'natural\'')
    # If levels were not specified
    else:
        if fill_first_field:
            contours = m.contourf(lons, lats, fields[0], latlon=True, extend=extend, alpha=fill_alpha)
        else:
            contours = m.contour(lons, lats, fields[0], latlon=True, extend=extend,
                                 colors=contour_colors[0], clabel=True, alpha=fill_alpha)

    # Plot line contours (only for a single field)
    if contour_colors and len(fields) == 1:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            contours = m.contour(lons, lats, fields[0], new_levels, latlon=True,
                                 colors=contour_colors, linewidths=1)
        # Plot contour labels for the first field
        ax.set_clip_on(True)
        if contour_labels:
            if contours:
                # If all contours all whole numbers, format the labels as such, otherwise they
                # all get 0.000 added to the end
                if np.all(np.mod(contours.levels[0], 1) == 0):
                    fmt = '%d'
                else:
                    fmt = '%s'
                matplotlib.pyplot.clabel(contours, inline=1, fontsize=5, fmt=fmt)

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
        cb = matplotlib.pyplot.colorbar(contours, orientation="horizontal", cax=cax,
                                        label=cbar_label, ticks=cbar_tick_labels)
        cb.ax.set_xticklabels(labels)
        cb.ax.tick_params(labelsize=8)
        # Add colorbar labels
        fontsize = 8
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
        # If cbar_label is set
        if cbar_label and cbar_tick_labels:
            cb = matplotlib.pyplot.colorbar(contours, orientation="horizontal", cax=cax,
                                            label=cbar_label, ticks=cbar_tick_labels)
            cb.set_label(cbar_label, fontsize=8)
            cb.ax.tick_params(labelsize=8)
        elif cbar_label:
            cb = matplotlib.pyplot.colorbar(contours, orientation="horizontal", cax=cax,
                                            label=cbar_label)
            cb.set_label(cbar_label, fontsize=8)
        elif cbar_tick_labels:
            cb = matplotlib.pyplot.colorbar(contours, orientation="horizontal", cax=cax,
                                            ticks=cbar_tick_labels)
            cb.ax.tick_params(labelsize=8)
        else:
            cb = matplotlib.pyplot.colorbar(contours, orientation="horizontal", cax=cax)

    # ----------------------------------------------------------------------------------------------
    # Plot second field (and any additional fields)
    #
    for i in range(1, len(fields)):
        # Plot contours for fields[i]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            if levels is not None:
                contours = m.contour(lons, lats, fields[i], levels[i], latlon=True,
                                     colors=contour_colors[i], linewidths=1)
            else:
                contours = m.contour(lons, lats, fields[i], latlon=True,
                                     colors=contour_colors[i], linewidths=1)
        # Plot contour labels for the first field
        ax.set_clip_on(True)
        if contour_labels:
            if contours:
                # If all contours all whole numbers, format the labels as such, otherwise they
                # all get 0.000 added to the end
                if np.all(np.mod(contours.levels[i], 1) == 0):
                    fmt = '%d'
                else:
                    fmt = '%s'
                matplotlib.pyplot.clabel(contours, inline=1, fontsize=5, fmt=fmt)


def plot_to_screen(*fields, grid=None, levels=None, colors=None, fill_colors=None, fill_alpha=1,
                   projection='equal-area', region='US', title='',
                   lat_range=None, lon_range=None,
                   cbar_ends='triangular', tercile_type='normal',
                   smoothing_factor=0, cbar_type='normal',
                   cbar_color_spacing='natural',
                   fill_coastal_vals=False, cbar_label='', cbar_tick_labels=None, contour_colors=None,
                   fill_first_field=True, contour_labels=False):
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
        >>> plot_to_screen(A, grid=grid)  # doctest: +SKIP
    """

    # --------------------------------------------------------------------------
    # Get dictionary of kwargs for child function
    #
    # Use locals() function to get all defined vars
    kwargs = locals()
    # Remove positional args
    del kwargs['fields']
    # --------------------------------------------------------------------------
    # Reshape field array(s) if necessary
    #
    # Create empty array to store reshaped fields
    reshaped_fields = np.nan * np.empty((len(fields), grid.num_y, grid.num_x))
    # Loop over fields
    for i in range(len(fields)):
        # If the current field is 1 dimensional, make it 2 dimensions (x, y)
        if fields[i].ndim == 1:
            reshaped_fields[i] = np.reshape(fields[i], (grid.num_y, grid.num_x))
        # If the current field is 2 dimensional, leave it alone
        elif fields[i].ndim == 2:
            reshaped_fields[i] = fields[i]
        # If the current field is not 1 or 2 dimensional, we can't know what to do with it
        else:
            raise ValueError('fields must have 1 or 2 dimensions')
    # Save reshaped fields back to tuple of fields
    fields = tuple([np.squeeze(A) for A in np.split(reshaped_fields, len(reshaped_fields), axis=0)])
    # --------------------------------------------------------------------------
    # Call _make_plot()
    #
    _make_plot(*fields, **kwargs)
    _show_plot()
    matplotlib.pyplot.close("all")


def plot_to_file(*fields, grid=None, file=None, dpi=200, levels=None, projection='equal-area',
                 region='US', fill_colors=None, fill_alpha=1, fill_first_field=True, title='',
                 lat_range=None, lon_range=None, cbar_ends='triangular', tercile_type='normal',
                 smoothing_factor=0, cbar_type='normal', cbar_color_spacing='natural',
                 fill_coastal_vals=False, cbar_label='', cbar_tick_labels=None,
                 contour_colors=None, contour_labels=False):
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
        >>> plot_to_file(A, grid=grid, file='out.png')  # doctest: +SKIP
    """

    # --------------------------------------------------------------------------
    # Get dictionary of kwargs for child function
    #
    # Use locals() function to get all defined vars
    kwargs = locals()
    # Remove positional args
    del kwargs['fields']
    # del kwargs['grid']
    # del kwargs['file']
    # --------------------------------------------------------------------------
    # Set backend to Agg which won't require X11
    #
    matplotlib.pyplot.switch_backend('Agg')
    # --------------------------------------------------------------------------
    # Reshape field array(s) if necessary
    #
    # Create empty array to store reshaped fields
    reshaped_fields = np.nan * np.empty((len(fields), grid.num_y, grid.num_x))
    # Loop over fields
    for i in range(len(fields)):
        # If the current field is 1 dimensional, make it 2 dimensions (x, y)
        if fields[i].ndim == 1:
            reshaped_fields[i] = np.reshape(fields[i], (grid.num_y, grid.num_x))
        # If the current field is 2 dimensional, leave it alone
        elif fields[i].ndim == 2:
            reshaped_fields[i] = fields[i]
        # If the current field is not 1 or 2 dimensional, we can't know what to do with it
        else:
            raise ValueError('fields must have 1 or 2 dimensions')
    # Save reshaped fields back to tuple of fields
    fields = tuple([np.squeeze(A) for A in np.split(reshaped_fields, len(reshaped_fields), axis=0)])
    # --------------------------------------------------------------------------
    # Call _make_plot()
    #
    _make_plot(*fields, **kwargs)
    _save_plot(file, dpi)
    matplotlib.pyplot.close("all")


def plot_tercile_probs_to_screen(below, near, above, grid,
                                 levels=[-90, -80, -70, -60, -50, -40, -33, 33,
                                         40, 50, 60, 70, 80, 90],
                                 projection='equal-area', region='US',
                                 fill_colors='tmean-terciles',
                                 fill_alpha=1, title='',
                                 lat_range=None, lon_range=None,
                                 cbar_ends='triangular',
                                 tercile_type='normal', smoothing_factor=0,
                                 cbar_type='tercile',
                                 cbar_color_spacing='natural',
                                 fill_coastal_vals=False, cbar_label='',
                                 cbar_tick_labels=[-90, -80, -70, -60, -50, -40, -33,
                                             33, 40, 50, 60, 70, 80, 90], contour_colors=None,
                                 contour_labels=False):
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
    # Define **kwargs for child function
    #
    kwargs['grid'] = grid
    # --------------------------------------------------------------------------
    # Plot
    #
    plot_to_screen(all_probs, **kwargs)


def plot_tercile_probs_to_file(below, near, above, grid, file,
                               levels=[-90, -80, -70, -60, -50, -40, -33, 33,
                                       40, 50, 60, 70, 80, 90],
                               projection='equal-area', region='US',
                               fill_colors='tmean-terciles',
                               fill_alpha=1, title='',
                               lat_range=None, lon_range=None,
                               cbar_ends='triangular', tercile_type='normal',
                               smoothing_factor=0, cbar_type='tercile',
                               cbar_color_spacing='natural',
                               fill_coastal_vals=False, cbar_label='',
                               cbar_tick_labels=[-90, -80, -70, -60, -50, -40, -33,
                                           33, 40, 50, 60, 70, 80, 90], contour_colors=None,
                               contour_labels=False):
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
    # Define **kwargs for child function
    #
    kwargs['grid'] = grid
    kwargs['file'] = file
    # --------------------------------------------------------------------------
    # Plot
    #
    plot_to_file(all_probs, **kwargs)


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
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        matplotlib.pyplot.savefig(file, dpi=dpi, bbox_inches='tight')


def _put_terciles_in_one_array(below, near, above):
    # Make an empty array to store above, near, and below
    all_probs = np.empty(below.shape)
    all_probs[:] = np.nan
    with np.errstate(invalid='ignore'):
        # Insert belows where they are the winning category and above 33%
        all_probs = np.where((below > 0.333) & (below > above), -1*below,
                             all_probs)
        # Insert aboves where they are the winning category and above 33%
        all_probs = np.where((above > 0.333) & (above > below), above, all_probs)
        # Insert nears where neither above or below are above 33%
        all_probs = np.where((below <= 0.333) & (above <= 0.333), 0, all_probs)
    # Return all_probs
    return all_probs


def _get_colors(colors):
    # Colors should be set to '[var]-[plot-type]'
    if colors in ['tmean-terciles', '500hgt-terciles']:
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
    elif colors == 'precip-terciles':
        # Below normal (browns)
        below = [
            [0.26,  0.13,  0.01],
            [0.36,  0.19,  0.02],
            [0.45,  0.25,  0.02],
            [0.63,  0.39,  0.12],
            [0.74,  0.56,  0.33],
            [0.85,  0.73,  0.55],
            [0.96,  0.9 ,  0.76],
        ]
        # Near normal (grey)
        near = [[0.75, 0.75, 0.75],]
        # Above normal (greens)
        above = (np.array(BuGn_7.colors) / 255).tolist()
        return below + near + above
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
