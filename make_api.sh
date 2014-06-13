#!/bin/sh

DOCS_DIR="docs/api"

rm -rf $DOCS_DIR

sphinx-apidoc -f -F -o docs/api gridded_data_utils
cd $DOCS_DIR
echo "sys.path.insert(0, os.path.abspath('../..'))" >> conf.py
echo "extensions.append('numpydoc')" >> conf.py
echo "html_theme = 'sphinxdoc'" >> conf.py
echo "html_title = 'Documentation for CPC\'s Gridded Data Utilities Python package'" >> conf.py
pwd
make html

