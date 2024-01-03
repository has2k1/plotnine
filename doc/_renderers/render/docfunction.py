from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .doc import RenderDoc
from .mixin_call import RenderDocCallMixin

if TYPE_CHECKING:
    from griffe import dataclasses as dc
    from quartodoc import layout


@dataclass
class __RenderDocFunction(RenderDocCallMixin, RenderDoc):
    """
    Render documentation for a function (layout.DocFunction)
    """

    def __post_init__(self):
        super().__post_init__()
        # We narrow the type with a TypeAlias since we do not expect
        # any subclasses to have narrower types
        self.doc: layout.DocClass = self.doc
        self.obj: dc.Function = self.obj


class RenderDocFunction(__RenderDocFunction):
    """
    Extend Rendering of a layout.DocFunction object
    """
