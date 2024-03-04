.PHONY: help Makefile
.DEFAULT_GOAL := help

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

define CREATE_OBJECTS_INV
import sphobjinv as soi
inv = soi.Inventory(source="objects.txt")
soi.writebytes("objects.inv", soi.compress(inv.data_file()))
endef
export CREATE_OBJECTS_INV

QRENDERER_STYLE_FILE=qrenderer.scss
QRENDERER_STYLE_URL=https://raw.githubusercontent.com/has2k1/qrenderer/main/doc/qrenderer.scss

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

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
	cd images; python readme_images.py

download_qrenderer_style:  ## Download qrenderer stylesheet
	@if [ ! -f $(QRENDERER_STYLE_FILE) ]; then \
		echo "Downloading $(QRENDERER_STYLE_FILE)"; \
		wget $(QRENDERER_STYLE_URL) -O $(QRENDERER_STYLE_FILE); \
	fi

extensions:  ## Install quarto/pandoc extensions
	quarto add --no-prompt has2k1/issuey
	quarto add --no-prompt has2k1/interlinks

deps: extensions download_qrenderer_style  ## Install build dependencies

interlinks:  ## Gather interlinks
	quartodoc interlinks

config:  ## Configure project for quartodoc and quarto
	python _config.py

docstrings: config  ## Generate qmd files from the docstrings
	quartodoc build --config _quartodoc.yml
	@python -c "$$CREATE_OBJECTS_INV"

html: docstrings download_qrenderer_style ## Build html site
	quarto render

doc: clean interlinks html  ## Build html documentation from a clean slate

preview:  ## Preview html website
	quarto preview --port 42000 --no-browser
