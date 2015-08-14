test:
	nosetests --rednose --force-color --with-coverage --cover-erase --cover-package data_utils
doc:
	export PYTHONPATH=$(shell pwd) ; pdoc --html --html-dir docs/api --overwrite --only-pypath --html-no-source --template-dir lib/api-doc-templates data_utils
