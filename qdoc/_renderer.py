from __future__ import annotations

import html
import typing
from pathlib import Path

from griffe import dataclasses as dc
from numpydoc.docscrape import NumpyDocString
from plum import dispatch
from quartodoc import MdRenderer
from quartodoc import ast as qast
from quartodoc.layout import DocClass
from quartodoc.renderers.base import convert_rst_link_to_md
from tabulate import tabulate

P_ROOT = Path(__file__).parent
EXAMPLES_FOLDER = P_ROOT / "plotnine-examples/plotnine_examples"

DOCSTRING_TMPL = """\
{rendered}

Examples
--------

{examples}
"""


class Renderer(MdRenderer):
    style = "plotnine"

    def _render_table(self, rows, headers):
        colalign = [""] * len(headers)
        table = tabulate(
            rows, headers=headers, tablefmt="unsafehtml", colalign=colalign
        )

        return table.replace("<table", '<table class="table" ')

    @dispatch
    def render(self, el: DocClass):  # type: ignore
        return super().render(el)

    @dispatch
    def render(self, el: dc.Object | dc.Alias):  # type: ignore # noqa: F811
        rendered = super().render(el)

        converted = convert_rst_link_to_md(rendered)

        p_example = EXAMPLES_FOLDER / "examples" / (el.name + ".ipynb")
        if p_example.exists():
            rel_path = Path("..") / p_example.relative_to(P_ROOT)
            example = f"{{{{< embed {rel_path} echo=true >}}}}"
            return DOCSTRING_TMPL.format(rendered=converted, examples=example)

        return converted

    @dispatch
    def render(self, el: qast.DocstringSectionSeeAlso):  # noqa: F811
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

    def render_annotation(
        self, el: dc.Name | dc.Expression | None  # type: ignore
    ):
        return super().render_annotation(el)

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
