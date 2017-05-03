# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = plotnine
SOURCEDIR     = .
PAPER         =
BUILDDIR      = _build

# For make theme
BOOTSWATCHTHEME = united
brand-primary = \#9E2F68
headings-font-weight = bold
font-family-sans-serif = '"Lato", "proxima-nova", "Helvetica Neue", Arial, sans-serif'

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "  theme    to create a custom sphinx boostrap theme"
	@echo "  logo     to generate logo images"
	@echo "  readme_images to generate images used in README.rst"

.PHONY: help Makefile theme logo readme_images

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

theme:
	../tools/build_theme.sh --theme $(BOOTSWATCHTHEME) \
	   --brand-primary '$(brand-primary)' \
	   --headings-font-weight $(headings-font-weight) \
	   --font-family-sans-serif '$(font-family-sans-serif)'

logo:
	cd images; \
	python logo.py; \
	convert -trim -density 100 -alpha remove -background '#FFFFFF' \
	   -gravity center -scale 176x176 -extent 180x180 \
	   -border 2 -bordercolor '#441A3F'\
	   logo.pdf logo-180.png; \
	convert -trim -density 100 -alpha remove -background '#FFFFFF' \
	   -gravity center -scale 32x32 \
	   -border 2 -bordercolor '#441A3F'\
	   logo-small.pdf logo-32.png; \
	convert -trim -density 100 -alpha remove -background '#FFFFFF' \
	   -gravity center -scale 32x32 \
	   -border 2 -bordercolor '#441A3F'\
	   logo-small.pdf favicon.ico;

readme_images:
	cd images; \
	python readme_images.py
