#!/bin/sh

docs_dir="docs/api"
pkg_dir="data_utils"

# Clean DOCS dir
rm -rf $docs_dir

# Generate a list of directories that contain Python modules
python_dirs=`find $pkg_dir -mindepth 1 -type d -not -iwholename '*.svn*'`

# Setup the Sphinx API docs
sphinx-apidoc -f -F -o docs/api $pkg_dir

# Copy JS file for hiding code prompts
cp library/copybutton.js docs/api/_static

# Change into the DOCS dir
cd $docs_dir

# Add the main package dir to the PYTHONPATH
echo "sys.path.insert(0, os.path.abspath('../..'))" >> conf.py

# Add the main package dir and all sub-package dirs to the PYTHONPATH
for python_dir in $python_dirs ; do
	echo "sys.path.insert(0, os.path.abspath('../../$python_dir'))" >> conf.py
done

# Add extensions
echo "extensions.append('numpydoc')" >> conf.py
echo "extensions.append('sphinx.ext.autosummary')" >> conf.py
echo "extensions.append('sphinx.ext.autodoc')" >> conf.py

# Set some options
echo "html_title = 'Documentation for CPC\'s Data Utilities Python package'" >> conf.py
#echo "html_theme = \"\"" >> conf.py

# Setup Sphinx RTD theme
echo "import sphinx_rtd_theme" >> conf.py
echo "html_theme = 'sphinx_rtd_theme'" >> conf.py
echo "html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]" >> conf.py

# Set some intersphinx mapping settings
echo "intersphinx_mapping = {}" >> conf.py
echo "intersphinx_mapping['python'] = ('http://docs.python.org/2', None)" >> conf.py
echo "intersphinx_mapping['numpy'] = ('http://docs.scipy.org/doc/numpy/', None)" >> conf.py
echo "intersphinx_mapping['scipy'] = ('http://docs.scipy.org/doc/scipy/reference/', None)" >> conf.py
echo "intersphinx_mapping['matplotlib'] = ('http://matplotlib.org/1.3.1/api/', None)" >> conf.py

# Add code to use JS to hide Python prompts in code snippets
echo "def setup(app):" >> conf.py
echo "    app.add_javascript('copybutton.js')" >> conf.py

# Generate API HTML
make html

