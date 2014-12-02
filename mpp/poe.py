#!/usr/bin/env python

import numpy
import scipy.stats
from stats_utils.stats import find_nearest_index
import matplotlib.pyplot
import math


def make_poe(discrete_members, ptiles, kernel_std=math.sqrt(1 - 0.7 ** 2)):
    """ Converts a set of discrete ensemble members into a continuous
    Probability of Exceedance (POE) distribution. The members are each "dressed"
    with a "kernel" (small Gaussian PDF), and then the kernels are all averaged
    to obtain a single PDF that is essentially a continuous representation of
    the distribution described by the discrete members.

    Parameters
    ----------
    discrete_members : array_like
        1-dimensional Numpy array of discrete member values
    ptiles : list
        List of percentiles at which to return the POE
    kernel_std : real, optional
        Standard deviation of the kernels. Defaults to a PDF in which the best
        member has a 0.7 correlation with observations.

    Returns
    -------
    array_like
        NumPy array of POE values at the given percentiles

    Examples
    --------

    >>> import numpy
    >>> import stats_utils.stats
    >>> arr = numpy.array([4, 5, 6, 7, 8])
    >>> stats_utils.stats.find_nearest_index(arr, 6.1)
    2
    """

    # --------------------------------------------------------------------------
    # Options
    #
    num_xvals = 1000  # Number of discrete X values for generating PDFs
    make_plot = False # Whether to make a plot of all steps of the POE creation

    #---------------------------------------------------------------------------
    # Create kernels for all members
    #
    # Create list of x values in standardized space
    x = numpy.linspace(-4, 4, num_xvals)
    # Create an empty NumPy array to store the kernels
    kernels = numpy.empty(shape=(discrete_members.shape[0], num_xvals))
    # Loop over all ensemble members and create their kernels
    for m in range(num_members):
        kernels[m] = scipy.stats.norm.pdf(x, discrete_members[m],
                                          kernel_std) / num_members

    # --------------------------------------------------------------------------
    # Sum all member kernels into a final PDF
    #
    final_pdf = numpy.sum(kernels, axis=0)

    # --------------------------------------------------------------------------
    # Convert into a POE (1 - CDF)
    #
    final_poe = 1 - numpy.cumsum(final_pdf) / numpy.max(numpy.cumsum(final_pdf))

    # --------------------------------------------------------------------------
    # Return the POE at the given percentiles
    #
    output = []
    for ptile in scipy.stats.norm.ppf(numpy.array(ptiles)/100):
        output.append(final_poe[find_nearest_index(x, ptile)])

    #---------------------------------------------------------------------------
    # Plot all ensemble members
    #
    if make_plot:
        matplotlib.rcParams['font.size'] = 10
        #matplotlib.rcParams['legend.fontsize'] = 'small'
        # Create a figure
        fig, ax1 = matplotlib.pyplot.subplots(1, 1)
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
        for ptile in scipy.stats.norm.ppf(numpy.array(ptiles)/100):
            matplotlib.pyplot.text(ptile, final_poe[find_nearest_index(x, ptile)], '+', horizontalalignment='center', verticalalignment='center', color='r')
        # Create legends
        leg1 = ax1.legend(loc="upper left")
        ax2.add_artist(leg1)
        leg2 = ax2.legend(loc="upper right")
        # Save the plot
        matplotlib.pyplot.savefig('output.png')

    return output


if __name__ == '__main__':
    # --------------------------------------------------------------------------
    # Make a set of fake, standardized ensemble members
    num_members = 21  # Number of ensemble members
    discrete_members = numpy.random.randn(num_members)

    # Use R_best to calculate the standard deviation of the kernels
    R_best = 0.7  # Correlation of best member
    kernel_std = math.sqrt(1 - R_best ** 2)

    # Define ptiles
    ptiles = [ 1,  2,  5, 10, 15,
              20, 25, 33, 40, 50,
              60, 67, 75, 80, 85,
              90, 95, 98, 99]

    poe = make_poe(discrete_members, ptiles, kernel_std)

    print(poe)
