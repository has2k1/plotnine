from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from functools import cached_property
from typing import cast

from quartodoc import layout
from quartodoc.pandoc.blocks import (
    Block,
    BlockContent,
    Blocks,
    Div,
    Header,
)
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Link

from ..format import markdown_escape
from ..pandoc.blocks import RawHTMLBlockTag
from .base import RenderBase


@dataclass
class __RenderPage(RenderBase):
    """
    Render a Page object (layout.Page)
    """

    def __post_init__(self):
        self.page = cast(layout.Page, self.layout_obj)
        """Page in the documentation"""

    def __str__(self):
        """
        The Page object rendered to quarto markdown
        """
        return str(Blocks([self.title, self.description, self.body]))

    def _has_one_object(self):
        return len(self.page.contents) == 1

    @cached_property
    def render_objs(self):
        from . import RenderObjType, get_render_type

        level = self.level if self._has_one_object else self.level + 1
        render_objs: list[RenderObjType] = [
            get_render_type(c)(c, self.renderer, level)  # type: ignore
            for c in self.page.contents
        ]
        return render_objs

    def render_title(self) -> Block:
        """
        Render the title/header of a docstring, including any anchors
        """
        title = ""
        # If a page documents a single object, lift-up the title of
        # that object to be the quarto-title of the page.
        if self._has_one_object:
            body = cast(Blocks, self.body)
            if body.elements:
                from . import RenderDoc

                rendered_obj = cast(RenderDoc, body.elements[0])
                rendered_obj.show_title = False
                title = cast(Header, copy(rendered_obj.title))
        elif self.page.summary:
            title = Header(self.level, markdown_escape(self.page.summary.name))

        header = RawHTMLBlockTag(
            "header",
            Div(title, Attr(classes=["quarto-title"])),
            Attr(
                "title-block-header", classes=["quarto-title-block", "default"]
            ),
        )
        return header

    def render_description(self) -> BlockContent:
        """
        Render the description of the documentation page
        """
        return self.page.summary.desc if self.page.summary else None

    def render_body(self) -> BlockContent:
        """
        Render the body of the documentation page
        """
        return Blocks(self.render_objs)

    def render_summary(self):
        page = self.page
        if page.summary is not None:
            link = Link(markdown_escape(page.summary.name), f"{page.path}.qmd")
            items = [(str(link), page.summary.desc)]
        elif len(page.contents) > 1 and not page.flatten:
            msg = (
                f"Cannot summarize page {page.path}. "
                "Either set its `summary` attribute with name and"
                "description details, or set `flatten` to True."
            )
            raise ValueError(msg)
        else:
            items = [
                row for d in self.render_objs for row in d.render_summary()
            ]
        return items


class RenderPage(__RenderPage):
    """
    Extend Rendering of a layout.Page object
    """
