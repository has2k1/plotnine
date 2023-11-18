from __future__ import annotations

import re
import typing
from pathlib import Path
from textwrap import dedent

from _renderers.numpydoc import NumpyDocRenderer
from _renderers.utils import shortcode
from griffe import dataclasses as dc
from plum import dispatch
from quartodoc import layout
from quartodoc.pandoc.blocks import Blocks, CodeBlock, Div, Header
from quartodoc.pandoc.components import Attr

DOC_DIR = Path(__file__).parent
EXAMPLES_DIR = DOC_DIR / "plotnine_examples"

DOC_SIGNATURE_TPL = """\
::: {{.doc-signature}}
{signature}
:::\
"""

doc_signature_pattern = re.compile(
    r"::: {.doc-signature}" r".+?" r":::\n", re.DOTALL
)

usage_pattern = re.compile(
    r"\n\n?\*\*Usage\*\*" r".+?\n" r"(?P<usage_signature>"
    # Indented signature block
    r"\s{4}\w" r".*?\n" r"\s{4}\)" r")",
    re.DOTALL,
)


class Renderer(NumpyDocRenderer):
    style = "plotnine"

    @dispatch
    def render(self, el: dc.Object | dc.Alias):  # type: ignore
        """
        Override method to embed examples notebook after the docstring
        """
        docstring_qmd = super().render(el)  # type: ignore
        notebook = EXAMPLES_DIR / "examples" / f"{el.name}.ipynb"
        if not notebook.exists():
            return docstring_qmd

        # path from the references directory where the qmd files
        # are placed
        relpath = Path("..") / notebook.relative_to(DOC_DIR)
        embed_notebook = shortcode("embed", f"{relpath}", echo="true")
        header = Header(self.header_level + 1, "Examples")
        return str(Blocks([docstring_qmd, header, embed_notebook]))

    @dispatch
    def render(self, el: layout.DocClass | layout.DocModule):  # type: ignore
        """
        Render the docstring & make usage signature the main signature

        The dynamically generated Usage signature is more complete and
        this method grabs the "Usage signature" and makes it the
        main signature.
        """
        docstring = super().render(el)
        m = usage_pattern.search(docstring)
        if not m:
            return docstring

        usage_signature = dedent(m.group("usage_signature"))
        new_signature_block = str(
            Div(
                CodeBlock(usage_signature, Attr(classes=["py"])),
                Attr(classes=["doc-signature"]),
            )
        )

        res = usage_pattern.sub("", docstring)
        res = doc_signature_pattern.sub(new_signature_block, res)
        return res
