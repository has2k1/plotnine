from __future__ import annotations

import typing
from pathlib import Path

from _renderers.numpydoc import NumpyDocRenderer
from _renderers.utils import shortcode
from griffe import dataclasses as dc
from plum import dispatch

# from quartodoc.renderers import NumpyDocRenderer
from quartodoc.pandoc.blocks import Blocks, Header

DOC_DIR = Path(__file__).parent
EXAMPLES_DIR = DOC_DIR / "plotnine_examples"


class Renderer(NumpyDocRenderer):
    style = "plotnine"

    @dispatch
    def render(self, el: dc.Object | dc.Alias):
        """
        Override method to embed examples notebook after the docstring
        """
        docstring_qmd = super().render(el)
        notebook = EXAMPLES_DIR / "examples" / f"{el.name}.ipynb"
        if not notebook.exists():
            return docstring_qmd

        # path from the references directory where the qmd files
        # are placed
        relpath = Path("..") / notebook.relative_to(DOC_DIR)
        embed_notebook = shortcode("embed", f"{relpath}", echo="true")
        header = Header(self.header_level + 1, "Examples")
        return str(Blocks([docstring_qmd, header, embed_notebook]))
