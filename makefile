install:
	conda install --yes --file conda-requirements.txt
	pip install -r pip-requirements.txt
	pip install .
test:
	nosetests --rednose --force-color --with-coverage --cover-erase --with-doctest --cover-package data_utils
doc:
	export PYTHONPATH=$(shell pwd) ; pdoc --html --html-dir docs/api --overwrite --only-pypath --html-no-source --template-dir lib/api-doc-templates data_utils
