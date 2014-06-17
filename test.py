import numpy

import pygrib

import gridded_data_utils.plotting
import gridded_data_utils.interpolation
import gridded_data_utils.merging
import gridded_data_utils.qc

# =============================================================================
# Test interpolation
# =============================================================================

# # Read in one of Wei Shi's obs files
# file = '/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/CPC_GLOBAL_T_V0.x_10min.lnx.20131220'
# data = numpy.fromfile(file, 'float32')
#
# # Set missing values to NaNs
# data[data <= -999] = numpy.nan
#
# # Reshape to 3 dimensions (vars x lats x lons)
# data = numpy.reshape(data, (6, 1080, 2160))
#
# # Extract one variable
# data = data[4]
#
# # Interpolate to a new grid
# new_res = 4
# orig_ll_corner = ((-90 + 1 / 12.0), (1 / 12.0))
# new_ll_corner = (-90, 0)
# new_ur_corner = (90, 360-new_res)
# new_grid = gridded_data_utils.interpolation.interpolate(data,
#                                                         orig_ll_corner,
#                                                         (1/6.0),
#                                                         new_ll_corner,
#                                                         new_ur_corner,
#                                                         new_res,
#                                                         grid_type="latlon")
#
# # Plot grid
# gridded_data_utils.plotting.plot_to_screen(new_grid, new_ll_corner, new_ur_corner, new_res)

# gridded_data_utils.plotting.plot_to_file(new_grid,
#                                          numpy.arange(-90, 90 + new_res, new_res),
#                                          numpy.arange(0, 360, new_res),
#                                          'new_res.png',
#                                          title="New Resolution")
#
# gridded_data_utils.plotting.plot_to_file(data,
#                                          numpy.arange(1/12.0-90, 90-1/12.0 + 1/6.0, 1/6.0),
#                                          numpy.arange(0, 360, 1/6.0),
#                                          'old_res.png',
#                                          title="Old Resolution")

# =============================================================================
# Test Merging
# =============================================================================


#--------------------------------------------------------------------------
# Read in d0 data (bottom grid)
#
grib = pygrib.open('/cpc/efsr_realtime/raw/gefs/06h/2013/01/01/00/gefs_tmp_2m_20130101_00z_f006_m00.grb2')
rec = grib.select(name='2 metre temperature',
                  typeOfLevel='heightAboveGround',
                  level=2)[0]
bottom = numpy.flipud(rec.values)
# Convert from Kelvin to Celsius
bottom -= 273.15
# Plot the data
gridded_data_utils.plotting.plot_to_file(bottom, (-90, 0), (90, 359), 1,
                        title="d0 field (bottom grid)",
                        file="d0_bottom.png")

#--------------------------------------------------------------------------
# Read in Wei Shi's data (top grid)
#
top = numpy.fromfile('/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/CPC_GLOBAL_T_V0.x_10min.lnx.20131220','float32')
# Set missing values to NaNs
top[top <= -999] = numpy.nan
# Reshape to 3 dimensions (vars x lats x lons)
top = numpy.reshape(top, (6, 1080, 2160))
# Extract one variable
top = top[4]
# Interpolate to 1 degree
orig_ll_corner = ((-90 + 1 / 12.0), (1 / 12.0))
top = gridded_data_utils.interpolation.interpolate(top, orig_ll_corner, 1/6.0, (-90, 0), (90, 359), 1)
# Plot the data
gridded_data_utils.plotting.plot_to_file(top, (-90, 0), (90, 359), 1,
                        title="obs field (top grid)",
                        file="obs_top.png")

# -------------------------------------------------------------------------
# Read in the mask file
#
mask = numpy.zeros_like(top)
mask[~numpy.isnan(top)] = 1
# mask = numpy.fromfile('/export/cpc-lw-mcharles/mcharles/data/land_mask_1deg.bin', 'float32')
# Reshape to 2 dimensions (lats x lons)
# top = numpy.reshape(mask, (181, 360))

# Plot the mask
gridded_data_utils.plotting.plot_to_file(mask, (-90, 0), (90, 359), 1,
                      title="mask",
                      file="mask.png")

#--------------------------------------------------------------------------
# Call the stack_grids() function
#
merged_grid = gridded_data_utils.merging.stack_grids(bottom, top, mask=mask)
# Plot the merged grid
gridded_data_utils.plotting.plot_to_file(merged_grid, (-90, 0), (90, 359), 1,
                      title="Merged d0 and obs",
                      file="merged.png")