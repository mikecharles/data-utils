import numpy
import mpl_toolkits.basemap
import matplotlib.pyplot

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

new_grid = gridded_data_utils.interpolation.interpolate(data, (-90 + 1 / 12), (1 / 12), (1 / 6), -90, 0, 90, 355, 5, grid_type="latlon")

num_x = 2160
num_y = 1080
num_vars = 6
start_x = 1.0 / 12.0
start_y = -90.0 + 1.0 / 12.0
resolution = 1 / 6.0
lons, lats = numpy.meshgrid(
    numpy.arange(start_x, start_x + (num_x * resolution), resolution,
                 numpy.float32),
    numpy.arange(start_y, start_y + (num_y * resolution), resolution,
                 numpy.float32))

lons_new = numpy.arange(0, 360, 5)
lats_new = numpy.arange(-90, 91, 5)
lons_new, lats_new = numpy.meshgrid(lons_new, lats_new)

# Create Basemap
matplotlib.pyplot.figure()
m = mpl_toolkits.basemap.Basemap(llcrnrlon=0, llcrnrlat=-80, urcrnrlon=360,
                                 urcrnrlat=80, projection='mill')
m.drawcoastlines(linewidth=1.25)
m.drawparallels(numpy.arange(-80, 81, 20), labels=[1, 1, 0, 0])
m.drawmeridians(numpy.arange(0, 360, 60), labels=[0, 0, 0, 1])
m.drawmapboundary(fill_color='#DDDDDD')
m.contourf(lons, lats, data, latlon=True)

matplotlib.pyplot.figure()
m2 = mpl_toolkits.basemap.Basemap(llcrnrlon=0, llcrnrlat=-80,
                                  urcrnrlon=360, urcrnrlat=80,
                                  projection='mill')
m2.drawcoastlines(linewidth=1.25)
m2.drawparallels(numpy.arange(-80, 81, 20), labels=[1, 1, 0, 0])
m2.drawmeridians(numpy.arange(0, 360, 60), labels=[0, 0, 0, 1])
m2.drawmapboundary(fill_color='#DDDDDD')
m2.contourf(lons_new, lats_new, new_grid, latlon=True)
matplotlib.pyplot.show()

print('something')

