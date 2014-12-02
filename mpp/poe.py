#!/usr/bin/env python

import numpy
import scipy.stats
import stats_utils.stats
import matplotlib.pyplot
import math


def make_poe(discrete_members, std):
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
                                          std) / num_members

    # --------------------------------------------------------------------------
    # Sum all member kernels into a final PDF
    #
    final_pdf = numpy.sum(kernels, axis=0)

    # --------------------------------------------------------------------------
    # Convert into a POE (1 - CDF)
    #
    final_poe = 1 - numpy.cumsum(final_pdf) / numpy.max(numpy.cumsum(final_pdf))

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
        # Create legends
        leg1 = ax1.legend(loc="upper left")
        ax2.add_artist(leg1)
        leg2 = ax2.legend(loc="upper right")
        # Save the plot
        matplotlib.pyplot.savefig('output.png')
        # Print the probability of exceeding a z-value of 0
        print('Probability of exceeding {} Z-values is {}'.format(0, final_poe[
            stats_utils.stats.find_nearest_index(x, 0)]))


if __name__ == '__main__':
    # --------------------------------------------------------------------------
    # Make a set of fake, standardized ensemble members
    num_members = 21  # Number of ensemble members
    discrete_members = numpy.random.randn(num_members)

    # Use R_best to calculate the standard deviation of the kernels
    R_best = 0.7  # Correlation of best member
    std = math.sqrt(1 - R_best ** 2)

    make_poe(discrete_members, std)
