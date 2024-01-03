from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from quartodoc.renderers.base import Renderer

from .typing_information import TypeInformation

if TYPE_CHECKING:
    from quartodoc import layout

    from .typing import DisplayNameFormat


@dataclass
class NumpyDocRenderer(Renderer):
    """
    Render strings to markdown in Numpydoc style
    """

    header_level: int = 1
    show_signature: bool = True
    display_name_format: DisplayNameFormat | Literal["auto"] = "auto"
    signature_name_format: DisplayNameFormat = "name"
    typing_module_paths: list[str] = field(default_factory=list)

    style: str = field(init=False, default="numpydoc")

    def render(self, el: layout.Page):
        """
        Render a page
        """
        from .render import RenderPage

        return str(RenderPage(el, self, self.header_level))

    def summarize(self, el: layout.Layout):
        """
        Summarize a Layout

        A Layout consists of a sequence of layout sections and/or layout pages
        """
        from .render import RenderLayout

        return str(RenderLayout(el, self, self.header_level))

    def _pages_written(self, builder):
        self._write_typing_information(builder)

    def _write_typing_information(self, builder):
        """
        Render typing information and the interlinks
        """
        for module_path in self.typing_module_paths:
            TypeInformation(module_path, self, builder).write()
