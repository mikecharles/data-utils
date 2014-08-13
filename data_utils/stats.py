#!/usr/bin/env python
import sys
import logging
import bisect

import numpy

"""
Contains statistical methods.
"""

# Initialize a logging object specific to this module
logger = logging.getLogger(__name__)

def values_to_ptiles(array,climo,ref_ptiles,k):
    """ Converts values to percentiles based on a set of climatology data containing values with associated percentiles.

    Method assumes that the values being converted follow a Gaussian distribution to estimated the percentiles.

    Parameters
    ----------
    array : array_like   
        1-dimensional (# locations) Numpy array of data to convert
    climo : array_like
        2-dimensional (# percentiles x # locations) Numpy array of climatology values associated with a set of percentiles
    ref_ptiles : array_like
        1-dimensional (# reference percentiles) Numpy array of reference percentiles that is associated with the percentiles used in the
        climatology data.
    k : Constant representing the ratio of the standard deviation of the percentile at the 100th percentile to the last available reference
        percentile. (std(100th ptile)/std(last ptile))

    Returns
    -------
    array_like
        A 1-dimensional (# locations) Numpy array of percentiles associated with the passed observation data (array).

    Raises
    ------
    Exception
        If input argument data arrays are not the required shape or dimensions or if the percentile calculation returns an exception.

    Examples
    --------

    >>> ref_ptiles = numpy.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])
    >>> num_ptiles = ref_ptiles.shape[0]
    >>> num_locations = 181*360
    >>> k = 1.343
    >>> array = numpy.array([14.9, 21.1, 30.2, 28.4, 12.12])
    >>> climo_data = numpy.fromfile("/cpc/data/climatologies/land_air/short_range/global/merged_tmean_poe/1deg/05d/tmean_clim_poe_05d_0815.bin","float32").astype('float64')
    >>> climo_data = numpy.array([[ 15.2,  15.2,  15.2,  15.2,  15.2],
    ...                           [ 16.4,  16.4,  16.4,  16.4,  16.4],
    ...                           [ 17.8,  17.8,  17.8,  17.8,  17.8],
    ...                           [ 18.8,  18.8,  18.8,  18.8,  18.8],
    ...                           [ 20.5,  numpy.nan, 20.5,  20.5,  20.5],
    ...                           [ 22.3,  22.3,  22.3,  22.3,  22.3],
    ...                           [23.7,  23.7,  23.7,  23.7,  23.7],
    ...                           [ 24.6 ,  24.6,  24.6,  24.6,  24.6],
    ...                           [ 27.6,   27.6,   27.6,   27.6,   27.6]])
    >>> obs_ptiles = values_to_ptiles(array,climo_data,ref_ptiles,k)
    >>> obs_ptiles
    [ 0.08349744         nan  1.          0.93285016  0.        ]
    """

    # Initialize returned array var
    ptiles = None
    
    # Check to see if number of dims are correct
    # Ref ptiles should be 1, Obs should be 1, Climo 2
    if ref_ptiles.ndim != 1:
        raise Exception("Reference percentile array has a dimension of " + str(ref_ptiles.ndim) + ". Must have an array dimension of 1.")
    if array.ndim != 1:
        raise Exception("Observation array has a dimension of " + str(array.ndim) + ". Must have an array dimension of 1.")
    if climo.ndim != 2:
        raise Exception("Observation array has a dimension of " + str(climo.ndim) + ". Must have an array dimension of 2.")    

    # Check to see if obs, climo, and ref_ptiles correct dimensions
    # Size of obs should match the size of climo 2nd dim
    if array.shape[0] != climo.shape[1]:
        raise Exception("Size of obs array does not match size of 2nd dim of climo array.")
    if climo.shape[0] != ref_ptiles.shape[0]:
        raise Exception("Size of climo array (1st dim) does not match size reference percentiles array.")

    # Set indices of the last, 50th, and 100th percentile associated with array ref_ptiles
    ptile_last = numpy.size(ref_ptiles)-1
    ptile_50th = bisect.bisect(ref_ptiles,0.50)-1

    # Print Estimated 100th ptile
    #loc = 4
    #p_100 = k*(climo[ptile_last,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]
    #logging.debug("est p 100th = " + str(p_100))

    # Print Estimated 0th ptile
    #p_0 = k*(climo[0,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]
    #logging.debug("est p 0th = " + str(p_0))
    
    try:    
        # Calculate the associated or corresponding climatological percentile with the observation array
        ptiles = numpy.array([    
            # If obs is nan, set to a nan value
            numpy.nan
                if numpy.isnan(obs)
     
            # If obs == a climo value, set ptile to the reference climo ptile
            # NOTE: Python gives a longer ref_ptiles precision value than specified, ie. 0.10000000000000001 instead of 0.1arg
            else ref_ptiles[numpy.argwhere(climo[:,loc] == obs)[0][0]]
                if obs in climo[:,loc]

            # If obs >= estimated T100th ptile, set ptile to 1.0
            else 1.00
                if obs >= k*(climo[ptile_last,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]

            # If obs > climo[last ptile] AND obs < est T100th, calculate ptile using linear interpolation
            else ref_ptiles[ptile_last] + ((obs - climo[ptile_last,loc])/(k*(climo[ptile_last,loc] - \
                climo[ptile_50th,loc]) + climo[ptile_50th,loc] - climo[ptile_last,loc]))*(1-ref_ptiles[ptile_last])
                if obs > climo[ptile_last,loc] and obs < k*(climo[ptile_last,loc] - climo[ptile_50th,loc]) \
                + climo[ptile_50th,loc]
            
            # If obs <= estimated T0th ptile, set ptile to 0.0
            else 0.00 
                if obs <= k*(climo[0,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]

            # If obs < climo 1st AND obs > est T0th, calculate ptile using linear interpolation
            else ref_ptiles[0] + ((obs - climo[0,loc])/(k*(climo[0,loc] - \
                climo[ptile_50th,loc]) + climo[ptile_50th,loc] - climo[0,loc])) * (0.00 - ref_ptiles[0])
                if obs < climo[0,loc] and obs > k*(climo[0,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]
          
            # If T1st < Tobs < Tlastptile, calculate ptile using linear interpolation
            else ref_ptiles[bisect.bisect(climo[:,loc],obs)-1] + \
            (ref_ptiles[bisect.bisect(climo[:,loc],obs)] - ref_ptiles[bisect.bisect(climo[:,loc],obs)-1]) \
            * ((obs - climo[bisect.bisect(climo[:,loc],obs)-1,loc])/ \
            (climo[bisect.bisect(climo[:,loc],obs),loc]-climo[bisect.bisect(climo[:,loc],obs)-1,loc])) 
                if obs > climo[0,loc] and obs < climo[ptile_last,loc]
     
            # Else set to NaN (a climo value may have potentially been a NaN that is necessary)
            else numpy.nan
            for loc, obs in enumerate(array)
        ])
    except:
        raise Exception("Percentile calculation failed.")

    return ptiles






