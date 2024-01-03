from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from griffe import dataclasses as dc
from quartodoc import layout
from quartodoc.pandoc.blocks import (
    Blocks,
    Div,
)
from quartodoc.pandoc.components import Attr

from ..format import markdown_escape
from ..utils import InterLink
from .base import RenderBase


@dataclass
class __RenderLink(RenderBase):
    """
    Render a Link object (layout.Link)
    """

    def __post_init__(self):
        self.link = cast(layout.Link, self.layout_obj)
        """Link being documented"""

        self.obj = cast(dc.Object | dc.Alias, self.link.obj)
        """Griffe object"""

    def __str__(self):
        """
        The Doc object rendered to quarto markdown
        """
        return str(
            Div(
                Blocks([self.title, self.description, self.body]),
                Attr(classes=["doc"]),
            )
        )

    def render_summary(self):
        link = InterLink(None, markdown_escape(self.link.name))
        return [(str(link), self._describe_object(self.obj))]


class RenderLink(__RenderLink):
    """
    Extend Rendering of a layout.Link object
    """
