setup:
	rm -rf plotnine-examples
	git clone https://github.com/has2k1/plotnine-examples.git

doc:
	DOC_GENERATION=1 python -m quartodoc build
	quarto render

render: doc

preview:
	quarto preview
