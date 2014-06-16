import numpy

import gridded_data_utils.plotting
import gridded_data_utils.interpolation
import gridded_data_utils.merging
import gridded_data_utils.qc


# Read in one of Wei Shi's obs files
file = '/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/CPC_GLOBAL_T_V0.x_10min.lnx.20131220'
data = numpy.fromfile(file, 'float32')

# Set missing values to NaNs
data[data <= -999] = numpy.nan

# Reshape to 3 dimensions (vars x lats x lons)
data = numpy.reshape(data, (6, 1080, 2160))

# Extract one variable
data = data[4]

# Interpolate to a new grid
new_res = 4
orig_ll_corner = ((-90 + 1 / 12), (1 / 12))
new_ll_corner = (-90, 0)
new_ur_corner = (90, 360-new_res)
new_grid = gridded_data_utils.interpolation.interpolate(data,
                                                        orig_ll_corner,
                                                        (1/6),
                                                        new_ll_corner,
                                                        new_ur_corner,
                                                        new_res,
                                                        grid_type="latlon")

# Plot grid
gridded_data_utils.plotting.plot_to_screen(new_grid,
                                         numpy.arange(-90, 90 + new_res,
                                                      new_res),
                                         numpy.arange(0, 360, new_res))

gridded_data_utils.plotting.plot_to_file(new_grid,
                                         numpy.arange(-90, 90 + new_res, new_res),
                                         numpy.arange(0, 360, new_res),
                                         'new_res.png',
                                         title="New Resolution")

gridded_data_utils.plotting.plot_to_file(data,
                                         numpy.arange(1/12-90, 90-1/12 + 1/6, 1/6),
                                         numpy.arange(0, 360, 1/6),
                                         'old_res.png',
                                         title="Old Resolution")
