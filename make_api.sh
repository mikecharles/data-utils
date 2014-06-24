#!/bin/sh

DOCS_DIR="docs/api"

rm -rf $DOCS_DIR

sphinx-apidoc -f -F -o docs/api gridded_data_utils
cd $DOCS_DIR
echo "sys.path.insert(0, os.path.abspath('../../gridded_data_utils'))" >> conf.py
echo "extensions.append('numpydoc')" >> conf.py
echo "extensions.append('sphinx.ext.autosummary')" >> conf.py
echo "html_title = 'Documentation for CPC\'s Gridded Data Utilities Python package'" >> conf.py
echo "html_theme = \"sphinxdoc\"" >> conf.py
echo "intersphinx_mapping = {}" >> conf.py
echo "intersphinx_mapping['python'] = ('http://docs.python.org/2', None)" >> conf.py
echo "intersphinx_mapping['numpy'] = ('http://docs.scipy.org/doc/numpy/', None)" >> conf.py
echo "intersphinx_mapping['scipy'] = ('http://docs.scipy.org/doc/scipy/reference/', None)" >> conf.py
echo "intersphinx_mapping['matplotlib'] = ('http://matplotlib.org/1.3.1/api/', None)" >> conf.py
make html

