#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand


# Get the version
script_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(script_path, 'VERSION')) as version_file:
    version = version_file.read().strip()

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='data-utils',
    version=version,
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
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
