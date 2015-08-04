About
=====

This package contains utilities for working with station and gridded data, such as reading and writing data, interpolating grids between resolutions, merging two datasets, and plotting data.

Requirements
============

- Python>=3.0
- numpy>=1.9.2
- scipy>=0.15.1
- matplotlib>=1.4.3
- pyyaml>=3.11

Installing
==========

If you have all the requirements above, then simply run this command to install the package:

    pip install data-utils

If not, then continue with the instructions below.

### Clone the repo

    git clone git@github.com:noaa-nws-cpc/data-utils.git
    cd data-utils

### Install dependencies

If you have [Anaconda installed](http://docs.continuum.io/anaconda/install.html), it's much easier to install the dependencies, since Anaconda uses pre-compiled binaries.

    conda install --file requirements.txt

If you don't, then pip will attempt to install the dependencies when you run `python setup.py` below, though you may run into trouble with the big packages (specifically NumPy and SciPy).

### Install this package

    python setup.py install

It's installed correctly if this doesn't return anything:

    cd $HOME
    python -c 'import data_utils'

Documentation
=============

The API documentation can be found [here](http://cpcwebapps.ncep.noaa.gov/python-docs/data_utils)
