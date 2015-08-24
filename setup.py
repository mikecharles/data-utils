#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='data-utils',
    version='v0.9.4',
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
        'numpy>=1.9.2',
        'scipy>=0.15.1',
        'matplotlib>=1.4.3',
        'basemap>=1.0.7',
        'pyyaml>=3.11',
        'stats-utils>=1.2'
    ]
)


