#!/usr/bin/env python

import numpy as np
# import math
# import mpp.poe
import logging
from data_utils.gridded.reading import read_grib
import sys
from data_utils.gridded.grid import Grid
# from data_utils.gridded.plotting import plot_to_file
# from stats_utils import stats

from string_utils.strings import replace_vars_in_string

# ------------------------------------------------------------------------------
# Config file options
#
# Define ptiles
ptiles = [ 1,  2,  5, 10, 15,
          20, 25, 33, 40, 50,
          60, 67, 75, 80, 85,
          90, 95, 98, 99]
num_members = 21
fhr_int = 6

# ------------------------------------------------------------------------------
# Command line args
#
model = 'gefsbc'
cycle = '00'
lead = 'd6-10'

if lead == 'd6-10' and cycle == '00':
    fhr1 = 150
    fhr2 = 264
elif lead == 'd8-14' and cycle == '00':
    fhr1 = 198
    fhr2 = 360
else:
    raise ValueError()

# Setup logging
logging.basicConfig(format='%(levelname)s - %(module)s - %(message)s',
                    level=logging.DEBUG)

# Initialize a logging object
logger = logging.getLogger(__name__)

# Set logging level
# logger.setLevel(logging.DEBUG)

# Should eventually be in a loop
date = '20150101'
yyyy, mm, dd = date[0:4], date[4:6], date[6:8]

grid = Grid('1deg_global')
grid.print_info()

# ------------------------------------------------------------------------------
# Load ensemble forecast data
#
fcst_file_template = '/cpc/model_realtime/raw/{model}/06h/{yyyy}/{mm}/{dd}/{cycle}/{model}_{yyyy}{mm}{dd}_{cycle}z_f{fhr}_m{member}.grb2'

# Initialize a data NumPy array
# data = np.empty(())

for member in ['{:02d}'.format(m) for m in range(num_members)]:
    for fhr in range(fhr1, fhr2 + 1, fhr_int):
        fcst_file = replace_vars_in_string(fcst_file_template, model=model,
                                           yyyy=yyyy, mm=mm, dd=dd,
                                           cycle=cycle, fhr=fhr, member=member)
        logger.info('Loading data from {}...'.format(fcst_file))
        print(read_grib(fcst_file, 'grib2', 'TMP', '2 m above ground').shape())
        sys.exit()

# replace_vars_in_string

# ------------------------------------------------------------------------------
# Load climo data
#

#-------------------------------------------------------------------------------
# Obtain the climatological mean and standard deviation at each gridpoint
#
# Load the climo file
# climo_file = '/export/cpc-lw-mcharles/mcharles/data/climatologies/land_air' \
#              '/short_range/global/merged_tmean_poe_missing_vals/1deg/05d' \
#              '/tmean_clim_poe_05d_1213.bin'
# climo_data = np.reshape(np.fromfile(climo_file, 'float32'), (len(ptiles),
#                                                   grid.num_y*grid.num_x))
#
# # Loop over climo gridpoints and calculate the mean and standard deviation
# # for i in range(grid.num_y*grid.num_x):
# for i in [0]:
#     [mean, std] = stats.poe_to_moments(ptiles, climo_data[:, i])
#     print(mean, std)








# --------------------------------------------------------------------------
# Make a set of fake, standardized ensemble members
# num_members = 21  # Number of ensemble members
# discrete_members = numpy.random.randn(num_members)
# grid = Grid('1deg_global')
# model_data = np.empty([num_members, grid.num_y*grid.num_x])
# model_file = '/cpc/model_realtime/raw/gefs/06h/2014/12/03/00' \
#              '/gefs_20141203_00z_f180_m{:02d}.grb2'
# for m in range(model_data.shape[0]):
#     print('Loading ' + model_file.format(m))
#     model_data[m, :] = read_grib(model_file.format(m),
#                                  'grib2', 'TMP',  '2 m above ground')



# Use R_best to calculate the standard deviation of the kernels
# R_best = 0.7  # Correlation of best member
# kernel_std = math.sqrt(1 - R_best ** 2)
#
# print(model_data[:, 0])
#
# mpp.poe.make_poe(model_data[:, 0], ptiles, kernel_std, make_plot=True)

# for i in range(data.shape[1]):
#     print('Calculating POE at point {}'.format(i))
#     poe = mpp.poe.make_poe(data[:,i], ptiles, kernel_std)
