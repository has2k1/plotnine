from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from qrenderer import QRenderer, RenderDoc, RenderDocClass, extend_base_class
from qrenderer._pandoc.inlines import InterLink, shortcode
from quartodoc.pandoc.blocks import Blocks, CodeBlock, Div, Header
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Inlines, Span

if TYPE_CHECKING:
    from griffe import expressions as expr

DOC_DIR = Path(__file__).parent
EXAMPLES_DIR = DOC_DIR / "examples"

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


class Renderer(QRenderer):
    pass


@extend_base_class
class _RenderDoc(RenderDoc):
    def render_body(self):
        body = super().render_body()
        if self.kind == "type":
            return body

        notebook = EXAMPLES_DIR / f"{self.obj.name}.ipynb"
        if not notebook.exists():
            return body

        # path from the references directory where the qmd files
        # are placed
        relpath = Path("..") / notebook.relative_to(DOC_DIR)
        embed_notebook = shortcode("embed", f"{relpath}", echo="true")
        header = Header(self.level + 1, "Examples")
        return Blocks([body, header, embed_notebook])


@extend_base_class
class _RenderDocClass(RenderDocClass):
    def _render_body_plotnine_alias(self):
        base: expr.ExprName = self.obj.bases[0]  # type: ignore
        return Inlines(
            [Span("alias of"), InterLink(base.name, base.canonical_path)]
        )

    def _is_plotnine_alias(self):
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
            self.obj.docstring
            and self.obj.docstring.parser is None
            and hasattr(self.obj, "bases")
            and len(self.obj.bases) == 2
            and self.obj.bases[1].name == "alias"  # type: ignore
        )

    def render_signature(self):
        signature = super().render_signature()
        docstring = self.obj.docstring.value if self.obj.docstring else ""
        m = usage_pattern.search(docstring)
        if not m:
            return signature

        usage_signature = dedent(m.group("usage_signature"))
        return Div(
            CodeBlock(usage_signature, Attr(classes=["py"])),
            Attr(classes=["doc-signature"]),
        )

    def render_body(self):
        if self._is_plotnine_alias():
            body = self._render_body_plotnine_alias()
        else:
            body = str(super().render_body())
            body = usage_pattern.sub("", body)
        return Blocks([body])

    def render_summary(self):
        """
        Override method to customize text for plotnine alias classes
        """
        summary = super().render_summary()
        if self._is_plotnine_alias():
            description = self._render_body_plotnine_alias()
            summary[0] = (summary[0][0], str(description))
        return summary
