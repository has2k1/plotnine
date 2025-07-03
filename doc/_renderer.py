from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from qrenderer import (
    QRenderer,
    RenderDoc,
    RenderDocClass,
    exclude_parameters,
)
from qrenderer._pandoc.inlines import shortcode
from quartodoc.pandoc.blocks import Blocks, CodeBlock, Div, Header, Para
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code

if TYPE_CHECKING:
    from typing import Literal


DOC_DIR = Path(__file__).parent
REFERENCE_DIR = DOC_DIR / "reference"
EXAMPLES_DIR = REFERENCE_DIR / "examples"

# We expect the usage to contain an indented block of code
usage_pattern = re.compile(
    r"^\*\*Usage\*\*"
    r"\s+"
    r"(?P<indented_block>(?:"
    r"^\s{4}[^\n]+\n*"
    r")+)",
    re.MULTILINE,
)
signature_pattern = re.compile(r"([a-zA-Z_]\w*)\s*\(([^)]*)\)")


class Renderer(QRenderer):
    pass


exclude_parameters(
    {
        "plotnine.scale_color_hue": ("s", "color_space"),
    }
)

summary_name_lookup = {
    "Beside": f"{Code('|')} Beside",
    "Stack": f"{Code('/')} Stack",
}


class _RenderDoc(RenderDoc):
    def render_body(self):
        body = super().render_body()
        if self.kind == "type":
            return body

        notebook = EXAMPLES_DIR / f"{self.obj.name}.ipynb"
        if not notebook.exists():
            return body

        relpath = notebook.relative_to(REFERENCE_DIR)
        embed_notebook = shortcode("embed", f"{relpath}", echo="true")
        header = Header(self.level + 1, "Examples")
        return Blocks([body, header, embed_notebook])

    @property
    def summary_name(self):
        name = super().summary_name
        if name.startswith("options."):
            # Until quartodoc makes it possible to use a tilde to use
            # and objects name and not the qualified path, we have to
            # create exceptions for all the qualified paths that we want
            # to be short.
            # Ref: https://github.com/machow/quartodoc/issues/230
            name = name[8:]
        elif name in summary_name_lookup:
            name = summary_name_lookup[name]
        return name


class _RenderDocClass(RenderDocClass):
    @cached_property
    def _usage(self) -> tuple[str, Literal["signature", "code"]] | None:
        """
        Parse the docstring **Usage** block
        """
        docstring = self.obj.docstring.value if self.obj.docstring else ""
        if m := usage_pattern.search(docstring):
            content = dedent(m.group("indented_block")).strip()
            return (
                content,
                "signature" if signature_pattern.match(content) else "code",
            )
        return None

    def __str__(self):
        content = super().__str__()
        # R
        if res := self._usage:
            # Render the content of the usage as code and if it looks
            # a signature mark it as one.
            usage, kind = res
            before, classes = Para("Usage"), ["doc-class", "doc-usage"]
            if kind == "signature":
                before = None
                classes.insert(0, "doc-signature")
            new = Div(
                [before, CodeBlock(usage, Attr(classes=["python"]))],
                Attr(classes=classes),
            )
            content = usage_pattern.sub(f"{new}\n", content)
        return content

    def render_signature(self):
        # A "Usage" that is a function signature voids the original
        # signature
        if (res := self._usage) and res[1] == "signature":
            return None
        return super().render_signature()
