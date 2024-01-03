from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from griffe import dataclasses as dc
from quartodoc import layout
from quartodoc.pandoc.blocks import (
    Block,
    Blocks,
    Header,
)
from quartodoc.pandoc.components import Attr
from tabulate import tabulate

from ..utils import isDoc, no_init
from .doc import RenderDoc

if TYPE_CHECKING:
    from typing import Literal, Optional, Sequence

    from ..typing import DocType


@dataclass
class RenderedMembersGroup(Block):
    title: Optional[Header] = None
    summary: Optional[str] = None
    members_body: Optional[Block] = None

    def __str__(self):
        return str(Blocks([self.title, self.summary, self.members_body]))


@dataclass
class __RenderDocMembersMixin(RenderDoc):
    """
    Mixin to render Doc objects that have members

    i.e. modules and classes
    """

    show_members: bool = no_init(True)
    """All members (attributes, classes and functions) """
    show_attributes: bool = no_init(True)
    show_classes: bool = no_init(True)
    show_functions: bool = no_init(True)

    show_members_summary: bool = no_init(True)
    """All member (attribute, class and function) summaries"""
    show_attributes_summary: bool = no_init(True)
    show_classes_summary: bool = no_init(True)
    show_functions_summary: bool = no_init(True)

    show_members_body: bool = no_init(True)
    """All member (attribute, class and function) bodies"""
    show_attributes_body: bool = no_init(True)
    show_classes_body: bool = no_init(True)
    show_functions_body: bool = no_init(True)

    def __post_init__(self):
        super().__post_init__()
        self.doc = cast(layout.DocClass | layout.DocModule, self.doc)
        self.obj = cast(dc.Class | dc.Module, self.obj)

    def render_body(self):
        """
        Render the docstring and member docs
        """
        docstring = super().render_body()
        return Blocks([docstring, *self.render_members()])

    def render_members(self) -> list[Optional[RenderedMembersGroup]]:
        """
        Render the docs of member objects

        The member objects are attributes, classes and functions/methods
        """
        if not self.show_members:
            return []
        return [
            self.render_attributes(),
            self.render_classes(),
            self.render_functions(),
        ]

    def render_classes(self) -> Optional[RenderedMembersGroup]:
        """
        Render the class members of the Doc
        """
        if not self.show_classes:
            return None
        classes = [x for x in self.doc.members if isDoc.Class(x)]
        return self._render_members_group(classes, "classes")

    def render_functions(self) -> Optional[RenderedMembersGroup]:
        """
        Render the function members of the Doc
        """
        if not self.show_functions:
            return None
        functions = [x for x in self.doc.members if isDoc.Function(x)]
        name = (
            "methods" if isinstance(self.doc, layout.DocClass) else "functions"
        )
        return self._render_members_group(functions, name)

    def render_attributes(self) -> Optional[RenderedMembersGroup]:
        """
        Render the function members of the Doc
        """
        if not self.show_attributes:
            return None
        attributes = [x for x in self.doc.members if isDoc.Attribute(x)]
        return self._render_members_group(attributes, "attributes")

    def _render_members_group(
        self,
        docables: Sequence[DocType],
        member_group: Literal["classes", "methods", "functions", "attributes"],
    ) -> Optional[RenderedMembersGroup]:
        """
        Render all of class, function or attribute members

        Parameters
        ----------
        docables
            List of layout.Doc subclasses. One for each member.

        member_group
            An identifier for the type of the members.
        """
        if not docables:
            return None

        from . import get_render_type

        _RenderType = get_render_type(docables[0])

        def _render_obj(obj: DocType):
            """
            Make a render object
            """
            r = _RenderType(obj, self.renderer, self.level + 2)
            r.path = ""  # Path is on the parent page
            return r

        mgroup = "functions" if member_group == "methods" else member_group
        show_summary: bool = getattr(self, f"show_{mgroup}_summary")
        show_body: bool = getattr(self, f"show_{mgroup}_body")
        render_objs = [_render_obj(obj) for obj in docables]

        title = Header(
            self.level + 1,
            member_group.title(),
            Attr(classes=[f"doc-{member_group}"]),
        )

        if self.show_members_summary and show_summary:
            rows = [row for r in render_objs for row in r.render_summary()]
            summary = tabulate(rows, ("Name", "Description"), "grid")
        else:
            summary = None

        body = Blocks(render_objs) if show_body else None
        return RenderedMembersGroup(title, summary, body)


class RenderDocMembersMixin(__RenderDocMembersMixin, RenderDoc):
    """
    Extend Rendering of objects that have members
    """
