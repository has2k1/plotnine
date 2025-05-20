.PHONY: help Makefile
.DEFAULT_GOAL := help

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
else
  PYTHON ?= python
endif

define PRINT_HELP_PYSCRIPT
import re
import sys

target_pattern = re.compile(r"^([a-zA-Z1-9_-]+):.*?## (.*)$$")
for line in sys.stdin:
    match = target_pattern.match(line)
    if match:
        target, help = match.groups()
        print(f"{target:<20} {help}")
endef
export PRINT_HELP_PYSCRIPT


help:
	@$(PYTHON) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean:  ## Remove build artefacts
	rm -rf .quarto
	rm -rf tutorials/*.ipynb
	rm -rf examples/*.ipynb
	rm -rf reference/
	rm -rf _site/
	rm -rf _inv/
	rm -f objects.txt
	rm -f objects.inv

readme-images:
	cd images; $(PYTHON) readme_images.py

install-stylesheets:  ## Install qrenderer stylesheet(s)
	$(PYTHON) -m qrenderer.stylesheets.install $(CURDIR)

extensions:  ## Install quarto/pandoc extensions
	quarto add --no-prompt has2k1/issuey
	quarto add --no-prompt has2k1/interlinks

dependencies: extensions install-stylesheets  ## Install build dependencies

interlinks:  ## Gather interlinks
	$(PYTHON) -m quartodoc interlinks

config:  ## Configure project for quartodoc and quarto
	$(PYTHON) _config.py

docstrings: config  ## Generate qmd files from the docstrings
	$(PYTHON) -m quartodoc build --config _quartodoc.yml
	# Create a objects.inv
	@$(PYTHON) -m sphobjinv convert -o zlib objects.txt

html: docstrings  ## Build html site
	quarto render

doc: clean interlinks html  ## Build html documentation from a clean slate

preview:  ## Preview html website
	quarto preview --port 42000 --no-browser
