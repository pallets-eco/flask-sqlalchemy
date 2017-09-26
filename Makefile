.PHONY: all test

all: test

test:
	pytest

clean: clean-pyc

clean-pyc:
	@find . -name '*.pyc' -exec rm {} \;
	@find . -name '__pycache__' -type d | xargs rm -rf

develop:
	@pip install --editable .

release:
	@python scripts/make-release.py

tox-test:
	@tox

upload-docs:
	$(MAKE) -C docs html
	python setup.py upload-docs

.PHONY: test release all clean clean-pyc develop tox-test upload-docs
