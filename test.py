import numpy

import gridded_data_utils.interpolation
import gridded_data_utils.merging
import gridded_data_utils.qc

# Read in one of Wei Shi's obs files
data = numpy.fromfile('/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/CPC_GLOBAL_T_V0.x_10min.lnx.20131220','float32')
data[data <= -999] = numpy.nan
data = numpy.reshape(data, (6, 2160, 1080))
data = data[4]

gridded_data_utils.interpolation.interpolate(data, 20, 200, 0.5, grid_spacing="latlon")

