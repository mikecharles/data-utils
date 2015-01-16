#!/usr/bin/env python

from __future__ import division

import numpy as np
import scipy.stats
from stats_utils.stats import find_nearest_index
import matplotlib.pyplot as plt
import math
import logging


# Initialize a logging object specific to this module
logger = logging.getLogger(__name__)


def make_poe(ensemble_array, ptiles, kernel_std=math.sqrt(1 - 0.7 ** 2),
             make_plot=False, member_axis=0):
    """ Converts a set of discrete ensemble members into a continuous
    Probability of Exceedance (POE) distribution. The members are each "dressed"
    with a "kernel" (small Gaussian PDF), and then the kernels are all averaged
    to obtain a single PDF that is essentially a continuous representation of
    the distribution described by the discrete members.

    Parameters
    ----------
    data : array_like
        N-dimensional Numpy array of discrete member values
    ptiles : list
        List of percentiles at which to return the POE
    kernel_std : real, optional
        Standard deviation of the kernels. Defaults to a PDF in which the best
        member has a 0.7 correlation with observations.
    make_plot : boolean
        Whether to make a plot of the PDFs and POE. Defaults to False
    member_axis : int, optional
        Axis containing the varying members, over which the POE is calculated.
        Defaults to 0

    Returns
    -------
    array_like
        NumPy array of POE values at the given percentiles

    Examples
    --------


    2
    """

    # --------------------------------------------------------------------------
    # Options
    #
    num_xvals = 1000  # Number of discrete X values for generating PDFs

    # --------------------------------------------------------------------------
    # Create kernels for all members
    #
    num_members = ensemble_array.shape[member_axis]
    # Create list of x values in standardized space
    x = np.linspace(-4, 4, num_xvals)
    # Create an array to store all kernels
    kernels = np.empty((ensemble_array.shape[0], x.shape[0],
                        ensemble_array.shape[1]))
    # Loop over each grid point and create a kernel
    for g in range(ensemble_array.shape[1]):
        print(g)
        kernels[:, :, g] = scipy.stats.norm.pdf(x, ensemble_array[:, g,
                                                np.newaxis],
                                          kernel_std) / num_members

    # --------------------------------------------------------------------------
    # Sum all member kernels into a final PDF
    #
    final_pdf = np.sum(kernels, axis=0)

    # --------------------------------------------------------------------------
    # Convert into a POE (1 - CDF)
    #
    final_poe = 1 - np.cumsum(final_pdf, axis=0) / np.max(np.cumsum(
        final_pdf, axis=0), axis=0)

    # --------------------------------------------------------------------------
    # Return the POE at the given percentiles
    #
    output = np.empty((len(ptiles), ensemble_array.shape[1]))
    ptile_indexes = []
    for ptile in scipy.stats.norm.ppf(np.array(ptiles)/100):
        ptile_indexes.append(find_nearest_index(x, ptile))
    for g in range(ensemble_array.shape[1]):
        output[:, g] = final_poe[ptile_indexes, g]

    # --------------------------------------------------------------------------
    # Plot all ensemble members
    #
    if make_plot:
        plt.rcParams['font.size'] = 10
        # Create a figure
        fig, ax1 = plt.subplots(1, 1)
        # Loop over all standardized ensemble members and plot their kernel
        for member in range(num_members):
            if member == 0:
                ax1.plot(x, kernels[member], 'b', label='Ensemble member')
            else:
                ax1.plot(x, kernels[member], 'b')
        # Plot the average of all kernels (final PDF)
        ax1.plot(x, final_pdf, 'r', label='Ensemble PDF')
        # Plot the average of all kernels in POE form
        ax2 = ax1.twinx()
        ax2.plot(x, final_poe, 'k', label='Ensemble POE')
        # Plot X's at each percentile on the POE
        for ptile in scipy.stats.norm.ppf(np.array(ptiles)/100):
            plt.text(ptile, final_poe[find_nearest_index(x, ptile)], '+', horizontalalignment='center', verticalalignment='center', color='r')
        # Create legends
        leg1 = ax1.legend(loc="upper left")
        ax2.add_artist(leg1)
        leg2 = ax2.legend(loc="upper right")
        # Save the plot
        plt.savefig('output.png')

    return output


def poe_to_terciles(poe, ptiles):
    """

    Parameters
    ----------
    discrete_members : array_like
        1-dimensional Numpy array of discrete member values
    ptiles : list
        List of percentiles at which to return the POE
    kernel_std : real, optional
        Standard deviation of the kernels. Defaults to a PDF in which the best
        member has a 0.7 correlation with observations.
    make_plot : boolean
        Whether to make a plot of the PDFs and POE. Defaults to False

    Returns
    -------
    array_like
        NumPy array of POE values at the given percentiles

    Examples
    --------


    """
    # --------------------------------------------------------------------------
    # Verify input
    #
    # ptiles must contain 33 and 67
    if 33 not in ptiles or 67 not in ptiles:
        raise ValueError('ptiles must contain 33 and 67')

    below = 1 - poe[find_nearest_index(ptiles, 33), :]
    above = poe[find_nearest_index(ptiles, 67), :]
    near = 1 - (below + above)

    return below, near, above

