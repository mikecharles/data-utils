#!/usr/bin/env python

from distutils.core import setup

setup(
    name='model_data_utilities',
    version='0.1',
    packages=['data_utils'],
    url='https://cpc-devtools.ncep.noaa.gov/trac/projects/data_utils',
    license='',
    author='Mike Charles',
    author_email='mike.charles@noaa.gov',
    description='Set of utilities for manipulating gridded data',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    requires=['numpy', 'matplotlib']
)


