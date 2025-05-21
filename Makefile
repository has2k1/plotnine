.PHONY: clean-pyc clean-build doc clean visualize-tests build

# NOTE: Take care not to use tabs in any programming flow outside the
# make target

# Use uv (if it is installed) to run all python related commands,
# and prefere the active environment over .venv in a parent folder
ifeq ($(OS),Windows_NT)
  HAS_UV := $(if $(shell where uv 2>NUL),true,false)
else
  HAS_UV := $(if $(shell command -v uv 2>/dev/null),true,false)
endif

ifeq ($(HAS_UV),true)
  PYTHON ?= uv run --active python
  PIP ?= uv pip
  UVRUN ?= uv run --active
else
  PYTHON ?= python
  PIP ?= pip
  UVRUN ?=
endif

BROWSER := $(PYTHON) -mwebbrowser

all:
	@echo "Using Python: $(PYTHON)"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with ruff"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "doc - generate HTML API documentation"
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
	$(UVRUN) coverage erase
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr tests/result_images/*

format:
	$(UVRUN) ruff format --check .

format-fix:
	$(UVRUN) ruff format .

lint:
	$(UVRUN) ruff check .

lint-fix:
	$(UVRUN) ruff check --fix .

fix: format-fix lint-fix

typecheck:
	$(UVRUN) pyright

test: clean-test
	export MATPLOTLIB_BACKEND=agg
	$(UVRUN) pytest

visualize-tests:
	$(PYTHON) tools/visualize_tests.py

update-baseline-images:
	$(PYTHON) tools/update_baseline_images.py

coverage:
	$(UVRUN) coverage report -m
	$(UVRUN) coverage html
	$(BROWSER) htmlcov/index.html

doc:
	$(MAKE) -C doc doc

doc-preview:
	$(MAKE) -C doc preview

release-major:
	@$(PYTHON) ./tools/release-checklist.py major

release-minor:
	@$(PYTHON) ./tools/release-checklist.py minor

release-patch:
	@$(PYTHON) ./tools/release-checklist.py patch

dist: clean-build
	$(PYTHON) -m build
	ls -l dist

build: dist

install: clean
	$(PIP) install ".[extra]"

doc-dependencies:
	$(PIP) install -e ".[doc]"
	$(PIP) install -r requirements/doc.txt
	$(MAKE) -C doc dependencies

develop: clean-cache
	$(PIP) install -e ".[all]"
	$(MAKE) doc-dependencies

develop-update: clean-cache
	$(PIP) install --upgrade -e ".[all]"
	$(UVRUN) pre-commit autoupdate
