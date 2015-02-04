#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='data-utils',
    version='0.1',
    packages=find_packages(),
    url='http://vm-lnx-ncep-gitlab.ncep.noaa.gov/mike.charles/data-utils',
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
    requires=['numpy',
              'matplotlib',
              'scipy',
              'sphinx_rtd_theme'],
    include_package_data=True,
)


