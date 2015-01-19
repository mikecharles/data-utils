#!/usr/bin/env python

import numpy as np
import math
import logging
import sys
from configobj import *
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
# Command line args
#
model = 'gefsbc'
cycle = '00'
lead = 'd6-10'
var = 'tmean'
log_level = 'INFO'
config_file = 'config.ini'
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

# ------------------------------------------------------------------------------
# Config file options
#
# Read options from config file
try:
    config = ConfigObj(config_file, file_error=True, unrepr=True)
except Exception as e:
    raise Exception('Could not parse config file {}: {} Make sure you\'ve '
                    'copied config.ini.example to config.ini'.format(
        config_file, e))
try:
    ptiles = config['ptiles']
    fcst_file_template = config['fcst-data']['file-template']
    climo_file_template = config['climo-data']['file-template']
    out_file_prefix_template = config['output']['file-prefix-template']
    num_members = config['fcst-data']['gefsbc']['num-members']
    fhr_int = config['fcst-data']['gefsbc']['fhr-int']
    R_best = config['fcst-data']['gefsbc']['r-best']
    grid_name = config['fcst-data']['gefsbc']['grid-name']
except KeyError as e:
    raise KeyError('One of the config keys is missing or invalid...')

# ------------------------------------------------------------------------------
# Setup a few more things that depend on config and command-line settings
#
# Create a new grid definition
grid = Grid(grid_name)
# Get a list of fhrs
fhrs = range(fhr1, fhr2 + 1, fhr_int)
# Get list of members
members = ['{:02d}'.format(m) for m in range(num_members)]
# Setup logging
logging.basicConfig(format='%(levelname)s - %(module)s - %(message)s',
                    level=getattr(logging, log_level))
logger = logging.getLogger(__name__)


# Should eventually be in a loop
date = '20150119'
date_obj = datetime.strptime(date, '%Y%m%d')
climo_mmdd = datetime.strftime(date_obj + timedelta(days=lead_end), '%m%d')

yyyy, mm, dd = date[0:4], date[4:6], date[6:8]

# ------------------------------------------------------------------------------
# Load ensemble forecast data
#
logger.info('Loading ensemble forecast data...')

# Initialize data NumPy arrays
fcst_data = np.empty((num_members, grid.num_x * grid.num_y))  # all
# members/grid points
temp_data = np.empty((len(fhrs), grid.num_x * grid.num_y))  # all fhrs/grid
# points

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
if var == 'tmean':
    climo_var = 'merged_tmean_poe'
else:
    climo_var = var
# Establish fcst file name
climo_file = replace_vars_in_string(climo_file_template, climo_var=climo_var,
                                    grid_name=grid_name, ave_window=ave_window,
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

# fcst_data_z = np.reshape(np.fromfile('fcst_data_z.bin', dtype='float32'),
#                          (num_members, grid.num_x*grid.num_y))

# ------------------------------------------------------------------------------
# Use R_best to calculate the standard deviation of the kernels
#
logger.info('Creating POEs from standardized anomaly forecasts...')

kernel_std = math.sqrt(1 - R_best ** 2)
# Loop over all grid points
poe = make_poe(fcst_data_z, ptiles, kernel_std, member_axis=0)

# ------------------------------------------------------------------------------
# Convert the final POE to terciles for plotting
#
below, near, above = poe_to_terciles(poe, ptiles)

levels = [-100, -90, -80, -70, -60, -50, -40, -33,
          33, 40, 50, 60, 70, 80, 90, 100]

# Establish output file name prefix
out_file_prefix = replace_vars_in_string(out_file_prefix_template, model=model,
                                   var=var, date=date, cycle=cycle, lead=lead)

plot_tercile_probs_to_file(below, near, above, grid,
                           out_file_prefix+'.png', levels=levels,
                           colors='tmean_colors')

end_time = time()

logger.info('Process took {:.0f} seconds to complete'.format(end_time -
                                                             start_time))
