"""
Contains methods for merging gridded data.
"""

from __future__ import print_function
import numpy
import pygrib


def stack_grids(bottom, top, threshold):
    pass


if __name__ == "__main__":
    # Read in d0 data (bottom grid)
    bottom = numpy.array()
    bottom = numpy.fromfile('/cpc/efsr_realtime/raw/gefs/06h/2013/01/01/00/gefs_tmp_2m_20130101_00z_f006_m00.grb2')
    # Read in Wei Shi's data (top grid)
    top = numpy.fromfile('/cpc/sfc_temp/GLOBAL-T/OUTPUT/y2013/CPC_GLOBAL_T_V0.x_10min.lnx.20131220','float32')

    stack_grids(bottom, top, -999)