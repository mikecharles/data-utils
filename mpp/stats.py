#!/usr/bin/env python

import numpy as np


def anomalize(raw_values, climo):
    anomalies = raw_values - climo
    return anomalies


if __name__ == '__main__':
    raw_values = np.array([1, 2, 0, 3, 2, 3, 3, 2, 4, 6])
    climo = 2
    print(anomalize(raw_values, climo))
