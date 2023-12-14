from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent
from typing import TypeGuard

from _renderers.numpydoc import NumpyDocRenderer
from _renderers.utils import InterLink, shortcode
from griffe import dataclasses as dc
from griffe import expressions as expr
from plum import dispatch
from quartodoc import layout
from quartodoc.pandoc.blocks import Blocks, CodeBlock, Div, Header
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Inlines, Span

DOC_DIR = Path(__file__).parent
EXAMPLES_DIR = DOC_DIR / "examples"

DOC_SIGNATURE_TPL = """\
::: {{.doc-signature}}
{signature}
:::\
"""

doc_signature_pattern = re.compile(
    r"::: {.doc-signature}" r".+?" r":::\n", re.DOTALL
)

usage_pattern = re.compile(
    r"\n\n?\*\*Usage\*\*"
    r".+?\n"
    r"(?P<usage_signature>"
    # Indented signature block
    r"\s{4}\w"
    r".*?\n"
    r"\s{4}\)"
    r")",
    re.DOTALL,
)


class Renderer(NumpyDocRenderer):
    style = "plotnine"

    def render_plotnine_alias_class(self, el: dc.Class) -> str:
        base: expr.ExprName = el.bases[0]  # type: ignore
        res = Inlines(
            [Span("alias of"), InterLink(base.name, base.canonical_path)]
        )
        return str(res)

    @dispatch
    def render(self, el: dc.Object | dc.Alias):  # type: ignore
        """
        Override method

        1. to embed examples notebook after the docstring
        2. to customize text for plotnine aliases
        """
        if is_plotnine_alias_class(el):
            docstring_qmd = self.render_plotnine_alias_class(el)
        else:
            docstring_qmd = super().render(el)  # type: ignore

        notebook = EXAMPLES_DIR / f"{el.name}.ipynb"
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

    @dispatch
    def summarize(self, obj: dc.Object | dc.Alias) -> str:
        """
        Override method to customize text for plotnine alias classes
        """
        if is_plotnine_alias_class(obj):
            return self.render_plotnine_alias_class(obj)
        return super().summarize(obj)


def is_plotnine_alias_class(el: dc.Object | dc.Alias) -> TypeGuard[dc.Class]:
    """
    Detect plotnine alias objects

    These are created with.

        class scale_colour_blah(scale_color_blah, alias):
            pass

    scale_colour_blah is an alias of scale_color_blah
    """
    # Note that the alias:
    # 1. does not have a docstring, therefore griffe does not assign
    #    it a parser.
    # 2. the name of its 2nd base class is "alias"
    return (
        el.docstring
        and el.docstring.parser is None
        and hasattr(el, "bases")
        and len(el.bases) == 2
        and el.bases[1].name  # type: ignore
        == "alias"  # type: ignore
    )
