from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING

from griffe.docstrings import dataclasses as ds
from quartodoc.pandoc.blocks import (
    Block,
    BlockContent,
    Blocks,
)

if TYPE_CHECKING:
    from griffe import dataclasses as dc
    from quartodoc import layout

    from ..numpydoc import NumpyDocRenderer
    from ..typing import SummaryItem


@dataclass
class __RenderBase(Block):
    """
    Render an object
    """

    layout_obj: (
        layout.DocClass
        | layout.DocFunction
        | layout.DocAttribute
        | layout.DocModule
        | layout.Page  # structural
        | layout.Section  # structural
        | layout.Link  #
        | layout.Layout  # structural
    )
    """layout object to be documented"""

    renderer: NumpyDocRenderer
    """Renderer that holds the configured values"""

    level: int = 1
    """The deepth of the object in the documentation"""

    show_title: bool = field(init=False, default=True)
    """Whether to show the title of the object"""

    show_signature: bool = field(init=False, default=True)
    """
    Whether to show the signature

    This only applies to objects that have signatures
    """

    show_description: bool = field(init=False, default=True)
    """
    Whether to show the description of the object

    This only applies to objects that have descriptions that are not
    considered part of the body documentation body.

    This attribute is not well defined and it may change in the future.
    """

    show_body: bool = field(init=False, default=True)
    """Whether to show the documentation body of the object"""

    def __str__(self):
        """
        The documentation as quarto markdown
        """
        return str(
            Blocks(
                [
                    self.title if self.show_title else None,
                    self.signature if self.show_signature else None,
                    self.description if self.show_description else None,
                    self.body if self.show_body else None,
                ]
            )
        )

    @cached_property
    def title(self) -> BlockContent:
        """
        The title/header of a docstring, including any anchors
        """
        return self.render_title()

    @cached_property
    def signature(self) -> BlockContent:
        """
        The signature of the object (if any)
        """
        return self.render_signature()

    @cached_property
    def description(self) -> BlockContent:
        """
        The description that the documented object
        """
        return self.render_description()

    @cached_property
    def body(self) -> BlockContent:
        """
        The body that the documented object
        """
        return self.render_body()

    # TODO: Finish typeing me
    @cached_property
    def summary(self):
        """
        The summary of the documented object
        """
        return self.render_summary()

    def _describe_object(self, obj: dc.Object | dc.Alias) -> str:
        """
        Return oneline description of the griffe object
        """
        # oneline description of the object being documented
        # This is the first line of the docstring
        parts = obj.docstring.parsed if obj.docstring else []
        section = parts[0] if parts else None
        return (
            section.value.split("\n")[0]
            if isinstance(section, ds.DocstringSectionText)
            else ""
        )

    def render_title(self) -> BlockContent:
        """
        Render the header of a docstring, including any anchors
        """

    def render_signature(self) -> BlockContent:
        """
        Render the signature of the object being documented
        """

    def render_description(self) -> BlockContent:
        """
        Render the description of the documentation page
        """

    def render_body(self) -> BlockContent:
        """
        Render the body of the object being documented
        """

    def render_summary(self) -> list[SummaryItem]:
        """
        Return a line(s) item that summarises the object
        """
        return []


class RenderBase(__RenderBase):
    """
    Extend the base render class
    """
