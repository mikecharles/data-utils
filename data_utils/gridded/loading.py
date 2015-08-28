"""
Containg methods for loading larger amounts of data

For example, let's say you want to load all of the forecasts valid today from
all years between 1985 and 2010. This module is intended to make that much
simpler.
"""

import numpy as np
from datetime import datetime


def load_fcsts(dates, file_template, data_type, grid, variable=None,
               level=None, record_num=None):
    pass


def load_obs(dates, file_template, data_type, grid, record_num=None):
    # Initialize a NumPy array to store the data
    data = np.empty((len(dates), grid.num_y * grid.num_x))
    # Loop over dates
    for d, date in enumerate(dates):
        # Convert file template to real file
        date_obj = datetime.strptime(date, '%Y%m%d')
        file = datetime.strftime(date_obj, file_template)
        # Open file and read the appropriate data
        try:
            data[d] = np.fromfile(file, 'float32')
        except FileNotFoundError:
            data[d] = np.nan
    # Return data
    return data


if __name__ == '__main__':
    from string_utils.dates import generate_date_list
    from data_utils.gridded.grid import Grid
    dates = generate_date_list('19850515', '20100515', interval='years')
    file_template = '/cpc/data/observations/land_air/short_range/global' \
                    '/merged_tmean/1deg/05d/%Y/%m/%d/tmean_05d_%Y%m%d.bin'
    data_type = 'bin'
    grid = Grid('1deg-global')
    data = load_obs(dates, file_template, data_type, grid)
    print('Done')