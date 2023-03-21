.PHONY: clean-pyc clean-build doc clean visualize-tests build
BROWSER := python -mwebbrowser

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with ruff"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo "develop - install the package in development mode"

clean: clean-build clean-cache clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	find . -name '*.egg-info' -exec rm -fr {} +

clean-cache:
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr tests/result_images/*

ruff:
	ruff . $(args)

ruff-isort:
	ruff --select I001 --quiet . $(args)

format:
	black . --check

format-fix:
	black .

lint: ruff ruff-isort

lint-fix:
	make lint args="--fix"

fix: format-fix lint-fix

typecheck:
	pyright

test: clean-test
	export MATPLOTLIB_BACKEND=agg
	pytest

visualize-tests:
	python tools/visualize_tests.py

coverage:
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

doc:
	$(MAKE) -C doc clean
	$(MAKE) -C doc html
	$(BROWSER) doc/_build/html/index.html

release: clean
	bash ./tools/release.sh

dist: clean
	python -m build
	ls -l dist

build: dist

install: clean
	pip install ".[extra]"

develop: clean-cache
	pip install -e ".[all]"

develop-update: clean-cache
	pip install --upgrade -e ".[all]"
	pre-commit autoupdate
