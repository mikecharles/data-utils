#!/usr/bin/env python

import numpy as np
import math
import logging
import sys
import argparse
import re
import yaml
from datetime import datetime, timedelta
from time import time
from data_utils.gridded.reading import read_grib
from data_utils.gridded.grid import Grid
from data_utils.gridded.plotting import plot_tercile_probs_to_file
from stats_utils.stats import poe_to_moments
from string_utils.strings import replace_vars_in_string
from string_utils.dates import generate_date_list
from mpp.poe import make_poe, poe_to_terciles

start_time = time()


# Function to see if all list elements are the same
def all_same(items):
    return all(x == items[0] for x in items)


# Function to validate a date
def date_arg(value):
    if not re.match("\d{8}|\d{8}-\d{8}|yesterday|today", value):
        raise argparse.ArgumentTypeError("must be in the form YYYYMMDD, "
                                         "YYYYMMDD-YYYYMMDD, yesterday, "
                                         "or today".format(value))
    else:
        return value


# Function to validate the model
def model_arg(value):
    model_list = ['gefsbc', 'cmcebc']
    regex = ''
    for model in model_list:
        regex += '({})|'.format(model)
    regex = regex.strip('|')
    if not re.match(regex, value):
        raise argparse.ArgumentTypeError("must be one of the following: "
                                         "{}".format(model_list))
    else:
        return value

# ------------------------------------------------------------------------------
# Command line args
#

# Create an ArgumentParser object
parser = argparse.ArgumentParser(add_help=False, usage='%(prog)s [OPTIONS]')

# Add a required argument group
group = parser.add_argument_group('required arguments')

# Add arguments
group.add_argument(
    '-d',
    '--date',
    dest='date',
    help='date(s) to post-process model data for (YYYYMMDD, YYYYMMDD-YYYYMMDD, '
         '\'yesterday\', or \'today\')',
    metavar='<DATE>',
    required=True,
    type=date_arg
)
group.add_argument(
    '-m',
    '--model',
    dest='model',
    help='model to post-process - to combine mult. models (equal weighting), '
         'separate by commas (no spaces)',
    metavar='<MODEL>',
    required=True,
    type=model_arg
)
group.add_argument(
    '-c',
    '--cycle',
    dest='cycle',
    help='model cycle to post-process',
    metavar='<CYCLE>', choices=['00z'],
    required=True,
)
group.add_argument(
    '-v',
    '--var',
    dest='var',
    help='variable to post-process',
    metavar='<VAR>', choices=['tmean'],
    required=True,
)
group.add_argument(
    '-l',
    '--lead',
    dest='lead',
    help='lead time to post-process',
    metavar='<LEAD>', choices=['d6-10', 'd8-14'],
    required=True,
)
group.add_argument(
    '-p',
    '--processing-type',
    dest='processing_type',
    help='type of post-processing to perform',
    metavar='<TYPE>', choices=['make-poe'],
    required=True,
)

# Add an optional argument group
group = parser.add_argument_group('optional arguments')
group.add_argument(
    '-h',
    '--help',
    dest='help',
    action='help',
    help='show this help message and exit'
)
# group.add_argument(
#     '--transmit',
#     dest='transmit',
#     help='transmit the output to the destination in the config file',
#     action='store_true'
# )
group.add_argument(
    '--log-level',
    dest='log_level',
    help='logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)',
    metavar='<LEVEL>',
    default='INFO',
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "debug",
             "info", "warning", "error", "critical"]
)
group.add_argument(
    '--config-file',
    dest='config_file',
    help='config file to parse',
    metavar='<FILE>',
    default='library/config.yml',
)

# If no options are set, print help and exit, otherwise parse args
if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit()
else:
    args = parser.parse_args()

# Remove 'z' from cycle
cycle_num = args.cycle.strip('z')

# Capitalize logging level
args.log_level = args.log_level.upper()

# Convert date of "today" into YYYYMMDD
if args.date == 'today':
    temp_date = datetime.now()
    args.date = "{:%Y%m%d}".format(temp_date)
# Convert date of "today" into YYYYMMDD
elif args.date == 'yesterday':
    temp_date = datetime.now() - timedelta(days=1)
    args.date = "{:%Y%m%d}".format(temp_date)

# Convert date of YYYYMMDD-YYYYMMDD into start and end dates
if re.match('\d{8}-\d{8}', args.date):
    args.start_date, args.end_date = args.date.split('-')
else:
    args.start_date = args.end_date = args.date

# Set a few vars that depend on lead
if args.lead == 'd6-10':
    # fhr range
    if args.cycle == '00z':
        fhr1 = 150
        fhr2 = 264
    # ave window
    ave_window = '05d'
    # lead end
    lead_end = 10
elif args.lead == 'd8-14':
    # fhr range
    if args.cycle == '00z':
        fhr1 = 198
        fhr2 = 360
    # ave window
    ave_window = '07d'
    # lead end
    lead_end = 14

# Get a list of models
models = args.model.split(',')

# ------------------------------------------------------------------------------
# Config file options
#
# Read some options from config file
try:
    with open(args.config_file) as f:
        config = yaml.load(f)
except Exception as e:
    raise Exception('Could not parse config file {}: {} Make sure you\'ve '
                    'copied config.yml.example to config.yml'.format(
        args.config_file, e))
try:
    ptiles = config['ptiles']
    climo_file_template = config['climo-data']['file-template']
    out_file_prefix_template = config['output']['file-prefix-template']
except KeyError as e:
    raise KeyError('One of the config keys is missing or invalid...')

# ------------------------------------------------------------------------------
# Setup logging
#
logging.basicConfig(format='%(levelname)s - %(module)s - %(message)s',
                    level=getattr(logging, args.log_level))
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Loop over dates
#
for date in generate_date_list(args.start_date, args.end_date):
    logger.info('Processing {}...'.format(date))
    # Get some date-related vars
    date_obj = datetime.strptime(date, '%Y%m%d')
    climo_mmdd = datetime.strftime(date_obj + timedelta(days=lead_end), '%m%d')
    yyyy, mm, dd = date[0:4], date[4:6], date[6:8]

    # --------------------------------------------------------------------------
    # Load ensemble forecast data
    #
    logger.info('Loading ensemble forecast data...')

    # Make sure the models have matching grids and fhrs
    if not all_same(
            [config['fcst-data'][m]['grid-name'] for m in models]
    ) or not all_same(
            [config['fcst-data'][m]['fhr-int'] for m in models]
    ):
        logger.fatal('All models must have the same fhr-int and grid-name')
        sys.exit(1)

    # Get a list of fhrs
    fhrs = range(fhr1, fhr2 + 1, config['fcst-data'][models[0]]['fhr-int'])

    # Create a new grid definition
    grid = Grid(config['fcst-data'][models[0]]['grid-name'])

    # Calculate total_num_members
    total_num_members = 0
    for model in models:
        total_num_members += config['fcst-data'][model]['num-members']
    # Initialize data NumPy arrays
    fcst_data = np.empty((total_num_members, grid.num_x * grid.num_y))  # all
    # members/grid points
    temp_data = np.empty((len(fhrs), grid.num_x * grid.num_y))  # all fhrs/grid
    # points

    # --------------------------------------------------------------------------
    # Loop over models
    #
    # Keep a count of the member across all models
    m_total = 0
    for model in models:
        # Read model-related options from config file
        try:
            R_best = config['fcst-data'][model]['r-best']
            grid_name = config['fcst-data'][model]['grid-name']
            num_members = config['fcst-data'][model]['num-members']
            data_type = config['fcst-data'][model]['data-type']
            fcst_file_template = config['fcst-data'][model]['file-template']
            var_name = config['fcst-data'][model]['vars'][args.var]['name']
            var_level = config['fcst-data'][model]['vars'][args.var]['level']
        except KeyError as e:
            raise KeyError('One of the config keys is missing or invalid...')

        # Get list of members
        members = ['{:02d}'.format(m) for m in range(num_members)]

        # Loop over members
        for m_single in range(len(members)):
            member = members[m_single]
            logger.debug('Loading member {}'.format(member))
            # Loop over fhrs
            for f in range(len(fhrs)):
                fhr = fhrs[f]
                # Establish fcst file name
                fcst_file = replace_vars_in_string(fcst_file_template,
                                                   model=model, yyyy=yyyy,
                                                   mm=mm, dd=dd,
                                                   cycle_num=cycle_num,
                                                   cycle=args.cycle, fhr=fhr,
                                                   member=member)
                # Load data from fcst file
                logger.debug('Loading data from {}...'.format(fcst_file))
                temp_data[f] = read_grib(fcst_file, data_type, var_name,
                                         var_level)

            # Create average or accumulation over fhrs
            if args.var == 'tmean':
                fcst_data[m_total] = np.nanmean(temp_data, axis=0)
            elif args.var == 'precip':
                fcst_data[m_total] = np.nansum(temp_data, axis=0)

            # Increment total member count
            m_total += 1

            # fcst_data[m].astype('float32').tofile('test_m{}.bin'.format(member))

    # Convert fcst data from Kelvin to Celsius
    if args.var == 'tmean':
        fcst_data -= 273.15

    # --------------------------------------------------------------------------
    # Perform post-processing
    #
    if args.processing_type == 'make-poe':

        # --------------------------------------------------------------------------
        # Load climo data
        #
        logger.info('Loading climatology data...')
        if args.var == 'tmean':
            climo_var = 'merged_tmean_poe'
        else:
            climo_var = args.var
        # Establish fcst file name
        climo_file = replace_vars_in_string(climo_file_template,
                                            climo_var=climo_var,
                                            grid_name=grid_name,
                                            ave_window=ave_window,
                                            var=args.var, climo_mmdd=climo_mmdd)
        logger.debug('Climatology file: {}'.format(climo_file))
        climo_data = np.reshape(
            np.fromfile(climo_file, 'float32'), (len(ptiles), grid.num_y*grid.num_x)
        )

        # --------------------------------------------------------------------------
        # Obtain the climatological mean and standard deviation at each gridpoint
        #
        # Use stats_utils.stats.poe_to_moments()
        logger.info('Converting climatologies from percentile to mean/standard '
                    'deviation...')
        climo_mean, climo_std = poe_to_moments(climo_data, ptiles, axis=0)

        # --------------------------------------------------------------------------
        # Anomalize all ensemble members
        #
        logger.info('Converting forecast data to standardized anomaly space...')
        fcst_data_z = (fcst_data - climo_mean) / climo_std

        # fcst_data_z = np.reshape(np.fromfile('fcst_data_z.bin', dtype='float32'),
        #                          (num_members, grid.num_x*grid.num_y))

        # --------------------------------------------------------------------------
        # Use R_best to calculate the standard deviation of the kernels
        #
        logger.info('Creating POEs from standardized anomaly forecasts...')

        kernel_std = math.sqrt(1 - R_best ** 2)
        # Loop over all grid points
        poe = make_poe(fcst_data_z, ptiles, kernel_std, member_axis=0)

        # --------------------------------------------------------------------------
        # Convert the final POE to terciles for plotting
        #
        below, near, above = poe_to_terciles(poe, ptiles)

        levels = [-100, -90, -80, -70, -60, -50, -40, -33,
                  33, 40, 50, 60, 70, 80, 90, 100]

        # Establish output file name prefix
        model_file_str = '-'.join(sorted(args.model.split(',')))
        out_file_prefix = replace_vars_in_string(out_file_prefix_template,
                                                 model=model_file_str,
                                                 var=args.var, date=date,
                                                 cycle=args.cycle,
                                                 lead=args.lead)

        # Plot terciles to a file
        plot_tercile_probs_to_file(below, near, above, grid,
                                   out_file_prefix+'.png', levels=levels,
                                   colors='tmean_colors')

# Print time taken to finish
end_time = time()
logger.info('Process took {:.0f} seconds to complete'.format(end_time -
                                                             start_time))
