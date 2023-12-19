clean:
	rm -rf tutorials/*.ipynb
	rm -rf examples/*.ipynb
	rm -rf .quarto/interlinks
	rm -rf reference/
	rm -rf _site/
	rm -rf _inv/

interlinks:
	quartodoc interlinks

build:
	python _config.py
	quartodoc build

render: build
	quarto render

doc: clean interlinks render

preview:
	quarto preview --port 42000 --no-browser
