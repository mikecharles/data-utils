#!/usr/bin/env python

import numpy as np
import math
import logging
from datetime import datetime, timedelta
from time import time
from data_utils.gridded.reading import read_grib
from data_utils.gridded.grid import Grid
from data_utils.gridded.plotting import plot_tercile_probs_to_file
from stats_utils.stats import poe_to_moments
from string_utils.strings import replace_vars_in_string
from mpp.poe import make_poe, poe_to_terciles

start_time = time()

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
var = 'tmean'
grid_res = '1deg'
log_level = 'DEBUG'
# Set a few vars that depend on lead
if lead == 'd6-10':
    # fhr range
    if cycle == '00':
        fhr1 = 150
        fhr2 = 264
    else:
        raise ValueError('Currently only the 00z cycle is supported')
    # ave window
    ave_window = '05d'
    # lead end
    lead_end = 10
elif lead == 'd8-14':
    # fhr range
    if cycle == '00':
        fhr1 = 198
        fhr2 = 360
    else:
        raise ValueError('Currently only the 00z cycle is supported')
    # ave window
    ave_window = '07d'
    # lead end
    lead_end = 14

fhrs = range(fhr1, fhr2 + 1, fhr_int)

# Get list of members
members = ['{:02d}'.format(m) for m in range(num_members)]

# Setup logging
logging.basicConfig(format='%(levelname)s - %(module)s - %(message)s',
                    level=getattr(logging, log_level))

# Initialize a logging object
logger = logging.getLogger(__name__)

# Set logging level
# logger.setLevel(logging.DEBUG)

# Should eventually be in a loop
date = '20150116'
date_obj = datetime.strptime(date, '%Y%m%d')
climo_mmdd = datetime.strftime(date_obj + timedelta(days=lead_end), '%m%d')

logger.info('LEAD END: '+str(lead_end))

yyyy, mm, dd = date[0:4], date[4:6], date[6:8]

grid = Grid('{}_global'.format(grid_res))

# ------------------------------------------------------------------------------
# Load ensemble forecast data
#
logger.info('Loading ensemble forecast data...')
fcst_file_template = '/cpc/model_realtime/raw/{model}/06h/{yyyy}/{mm}/{dd}/{cycle}/{model}_{yyyy}{mm}{dd}_{cycle}z_f{fhr}_m{member}.grb2'

# Initialize data NumPy arrays
fcst_data = np.empty((num_members, grid.num_x * grid.num_y)) # all
# members/gridpoints
temp_data = np.empty((len(fhrs), grid.num_x * grid.num_y)) # all fhrs/gridpoints

# Loop over members
for m in range(len(members)):
    member = members[m]
    logger.debug('Loading member {}'.format(member))
    # Loop over fhrs
    for f in range(len(fhrs)):
        fhr = fhrs[f]
        # Establish fcst file name
        fcst_file = replace_vars_in_string(fcst_file_template, model=model,
                                           yyyy=yyyy, mm=mm, dd=dd,
                                           cycle=cycle, fhr=fhr, member=member)
        # Load data from fcst file
        logger.debug('Loading data from {}...'.format(fcst_file))
        temp_data[f] = read_grib(fcst_file, 'grib2', 'TMP', '2 m above ground')
    # Create average or accumulation over fhrs
    if var == 'tmean':
        fcst_data[m] = np.nanmean(temp_data, axis=0)
    elif var == 'precip':
        fcst_data[m] = np.nansum(temp_data, axis=0)

    #     fcst_data[m].astype('float32').tofile('test_m{}.bin'.format(member))

# Convert fcst data from Kelvin to Celsius
if var == 'tmean':
    fcst_data -= 273.15

# ------------------------------------------------------------------------------
# Load climo data
#
logger.info('Loading climatology data...')
climo_file_template = '/export/cpc-lw-mcharles/mcharles/data/climatologies/land_air/short_range/global/{climo_var}/{grid_res}/{ave_window}/{var}_clim_poe_{ave_window}_{climo_mmdd}.bin'
if var == 'tmean':
    climo_var = 'merged_tmean_poe'
else:
    climo_var = var
# Establish fcst file name
climo_file = replace_vars_in_string(climo_file_template, climo_var=climo_var,
                                    grid_res=grid_res, ave_window=ave_window,
                                    var=var, climo_mmdd=climo_mmdd)
logger.debug('Climatology file: {}'.format(climo_file))
climo_data = np.reshape(np.fromfile(climo_file, 'float32'), (len(ptiles),
                                                  grid.num_y*grid.num_x))

# ------------------------------------------------------------------------------
# Obtain the climatological mean and standard deviation at each gridpoint
#
# Use stats_utils.stats.poe_to_moments()
logger.info('Converting climatologies from percentile to mean/standard '
            'deviation...')
climo_mean, climo_std = poe_to_moments(climo_data, ptiles, axis=0)

# ------------------------------------------------------------------------------
# Anomalize all ensemble members
#
logger.info('Converting forecast data to standardized anomaly space...')
fcst_data_z = (fcst_data - climo_mean) / climo_std

# ------------------------------------------------------------------------------
# Use R_best to calculate the standard deviation of the kernels
#
logger.info('Creating POEs from standardized anomaly forecasts...')

# Define R_best and the kernel standard deviation (currently arbitrary)
R_best = 0.7  # correlation of best member
kernel_std = math.sqrt(1 - R_best ** 2)
# Loop over all gridpoints
poe = np.empty((len(ptiles), fcst_data_z.shape[1]))
for i in range(fcst_data_z.shape[1]):
    poe[:, i] = make_poe(fcst_data_z[:, i], ptiles, kernel_std)

# ------------------------------------------------------------------------------
# Convert the final POE to terciles for plotting
#
below, near, above = poe_to_terciles(poe, ptiles)

levels = [-100, -90, -80, -70, -60, -50, -40, -33,
          33, 40, 50, 60, 70, 80, 90, 100]

plot_file = 'test.png'

plot_tercile_probs_to_file(below, near, above, grid, plot_file, levels=levels,
                           colors='tmean_colors')

end_time = time()

logger.info('Process took {:.0f} seconds to complete'.format(end_time -
                                                             start_time))
