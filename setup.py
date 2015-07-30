#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='data-utils',
    version='v0.9.1',
    packages=find_packages(),
    include_package_data=True,
    url='https://cpc-devtools.ncep.noaa.gov/trac/projects/model-post-processing',
    license='',
    author='Mike Charles',
    author_email='mike.charles@noaa.gov',
    description='Set of utilities for post-processing gridded model data',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'basemap',
        'pyyaml',
        'stats-utils'
    ]
)


