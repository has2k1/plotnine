from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from quartodoc.pandoc.blocks import Div
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code

from .doc import RenderDoc
from .mixin_members import RenderDocMembersMixin

if TYPE_CHECKING:
    from griffe import dataclasses as dc
    from quartodoc import layout


@dataclass
class __RenderDocModule(RenderDocMembersMixin, RenderDoc):
    """
    Render documentation for a module (layout.DocModule)
    """

    def __post_init__(self):
        super().__post_init__()
        # We narrow the type with a TypeAlias since we do not expect
        # any subclasses to have narrower types
        self.doc: layout.DocModule = self.doc
        self.obj: dc.Module = self.obj

    # TODO: Verify that this is really required.
    # Why isn't the header/title enough?
    def render_signature(self):
        if not self.signature_name:
            return None
        return Div(Code(self.signature_name), Attr(classes=["doc-signature"]))


class RenderDocModule(__RenderDocModule):
    """
    Extend Rendering of a layout.DocModule object
    """
