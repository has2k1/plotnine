from __future__ import annotations

import html
import typing
from pathlib import Path
from textwrap import indent

from griffe import dataclasses as dc
from griffe import expressions as expr
from griffe.docstrings import dataclasses as ds
from numpydoc.docscrape import NumpyDocString
from plum import dispatch
from quartodoc import MdRenderer
from quartodoc import ast as qast
from quartodoc.layout import DocClass
from quartodoc.renderers.base import convert_rst_link_to_md, sanitize
from tabulate import tabulate

DOC_DIR = Path(__file__).parent
EXAMPLES_DIR = DOC_DIR / "plotnine_examples"

DOCSTRING_TPL = """\
{rendered}

Examples
--------

{examples}
"""

INDENT = " " * 4
PARAM_TPL = """\
<code class="python">{name}{annotation}{default}</code>

:{indented_description}
"""

# NOTE: https://github.com/mkdocstrings/griffe/pull/194
# will break this module.


class Renderer(MdRenderer):
    style = "plotnine"

    @dispatch
    def render(self, el: DocClass):  # type: ignore
        return super().render(el)

    @dispatch
    def render(self, el: dc.Object | dc.Alias):  # type: ignore # noqa: F811
        rendered = super().render(el)

        converted = convert_rst_link_to_md(rendered)

        example_path = EXAMPLES_DIR / "examples" / (el.name + ".ipynb")
        if example_path.exists():
            rel_path = Path("..") / example_path.relative_to(DOC_DIR)
            example = "{{< embed" f" {rel_path} " "echo=true >}}"
            return DOCSTRING_TPL.format(rendered=converted, examples=example)

        return converted

    @dispatch
    def render(  # type: ignore
        self, el: qast.DocstringSectionSeeAlso  # noqa: F811
    ):
        lines = el.value.split("\n")

        # each entry in result has form:
        # ([('func1', '<directive>), ...], <description>)
        parsed = NumpyDocString("")._parse_see_also(lines)

        result = []
        for funcs, description in parsed:
            links = [f"[{name}](`{name}`)" for name, role in funcs]

            str_links = ", ".join(links)

            if description:
                str_description = "<br>".join(description)
                result.append(f"{str_links}: {str_description}")
            else:
                result.append(str_links)

        return "* " + "\n* ".join(result)

    @dispatch
    def render_annotation(self, el: None):  # type: ignore
        return ""

    @dispatch
    def render_annotation(self, el: expr.Expression):  # type: ignore
        # an expression is essentially a list[expr.Name | str]
        # e.g. Optional[TagList]
        #   -> [Name(source="Optional", ...), "[", Name(...), "]"]

        return "".join([self.render_annotation(a) for a in el])

    @dispatch
    def render_annotation(self, el: expr.Name):  # type: ignore
        # e.g. Name(source="Optional", full="typing.Optional")
        return f"[{el.source}](`{el.full}`)"

    @dispatch
    def render_annotation(self, el: str):
        """
        Override base class so that no escaping is done
        """
        return sanitize(el)

    @dispatch
    def summarize(self, el: dc.Object | dc.Alias):
        result = super().summarize(el)
        return html.escape(result)

    @dispatch
    def signature(self, el: dc.Object | dc.Alias):
        # Informative geom and stat signatures are generated dynamically and
        # are part of the docstring. quartoc has empty signatures because it
        # (or griffe) cannot pickup those of the base class.
        skip = el.name.startswith("geom_") or el.name.startswith("stat_")
        if skip:
            return ""
        return super().signature(el)  # type: ignore

    # parameters ----
    @dispatch
    def render(self, el: ds.DocstringParameter) -> str:  # type: ignore # noqa: F811
        """
        Return parameter docstring as a definition term & description

        output-format: quarto/pandoc
        """
        annotation = self.render_annotation(el.annotation)  # type: ignore
        kwargs = {
            "name": el.name,
            "annotation": f": {annotation}" if annotation else "",
            "default": f" = {el.default}" if el.default else "",
            "indented_description": indent(el.description, INDENT),
        }
        return PARAM_TPL.format(**kwargs)

    @dispatch
    def render(self, el: ds.DocstringSectionParameters) -> str:
        """
        Return parameters docstring as a definition list

        output-format: quarto/pandoc
        """
        definitions = [
            self.render(ds_parameter)  # type: ignore
            for ds_parameter in el.value
        ]
        return "\n".join(definitions)
