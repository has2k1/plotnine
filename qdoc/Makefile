setup:
	rm -rf plotnine-examples
	git clone https://github.com/has2k1/plotnine-examples.git

interlinks:
	quartodoc interlinks

render:
	GENERATING_QUARTODOC=1 python -m quartodoc build
	quarto render

doc: interlinks render

preview:
	quarto preview
