from __future__ import annotations

import html
from importlib.resources import files
from pathlib import Path
from typing import Union

from griffe import dataclasses as dc
from griffe.docstrings import dataclasses as ds
from numpydoc.docscrape import NumpyDocString
from plum import dispatch
from quartodoc import MdRenderer, layout
from quartodoc import ast as qast
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
    def render(self, el: layout.DocClass):
        return super().render(el)

    @dispatch
    def render(self, el: Union[dc.Object, dc.Alias]):
        rendered = super().render(el)

        converted = convert_rst_link_to_md(rendered)

        p_example = EXAMPLES_FOLDER / "examples" / (el.name + ".ipynb")
        if p_example.exists():
            rel_path = Path("..") / p_example.relative_to(P_ROOT)
            example = f"{{{{< embed {rel_path} echo=true >}}}}"
            return DOCSTRING_TMPL.format(rendered=converted, examples=example)

        return converted

    @dispatch
    def render(self, el: qast.DocstringSectionSeeAlso):
        lines = el.value.split("\n")

        # each entry in result has form: ([('func1', '<directive>), ...], <description>)
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

    def render_annotation(self, el: dc.Name | dc.Expression | None):
        return super().render_annotation(el)

    @dispatch
    def summarize(self, el: dc.Object | dc.Alias):
        result = super().summarize(el)
        return html.escape(result)
