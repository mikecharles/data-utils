#!/usr/bin/env python

import os
import sys
import subprocess
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


class MakeAPI(Command):
    """Command to create API documentation using the pdoc package"""
    description = 'Create API documentation using the pdoc package'
    user_options = [('api-dir=', 'o', 'Directory to write API docs to')]

    def initialize_options(self):
        """Set default values for options."""
        self.api_dir = None

    def finalize_options(self):
        """Post-process options."""

    def run(self):
        """Run command."""
        template_dir = script_path+'/lib/api-doc-templates'
        if not self.api_dir:
            self.api_dir = script_path+'/docs/api'
        print('Writing API docs to {}'.format(self.api_dir))
        # Deleting existing API docs
        subprocess.call('rm -rf {}/*'.format(self.api_dir), shell=True)
        # Running pdoc to create API docs
        subprocess.call('export PYTHONPATH={} ; pdoc --html '
                        '--html-dir {} --overwrite --only-pypath '
                        '--external-links --template-dir {} '
                        './data_utils'.format(script_path, self.api_dir,
                                              template_dir),
                        shell=True)
        # Move all HTML files out of the 'data_utils/' directory that was
        # created (unnecessary level)
        subprocess.call('mv {}/data_utils/* {}'.format(self.api_dir,
                                                       self.api_dir),
                        shell=True)
        subprocess.call('rm -rf {}/data_utils'.format(self.api_dir), shell=True)

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
        'stats-utils>=1.2',
        'palettable>=2.1.1'
    ],
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest,
        'makeapi': MakeAPI
    },
)
