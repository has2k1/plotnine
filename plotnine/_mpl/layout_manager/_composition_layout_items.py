from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from matplotlib.text import Text

from plotnine._mpl.utils import (
    ArtistGeometry,
    TextJustifier,
    resize_footer_background,
    resize_footer_line,
)

if TYPE_CHECKING:
    from typing import Any

    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle

    from plotnine.composition._compose import Compose

    from ._composition_side_space import CompositionSideSpaces


@dataclass
class CompositionLayoutItems:
    """
    plot_annotation artists
    """

    def __init__(self, cmp: Compose):
        def get(name: str) -> Any:
            """
            Return themeable target or None
            """
            if self._is_blank(name):
                return None
            else:
                t = getattr(cmp.theme.targets, name)
                if isinstance(t, Text) and t.get_text() == "":
                    return None
                return t

        self.cmp = cmp
        self.geometry = ArtistGeometry(cmp.figure)

        self.plot_title: Text | None = get("plot_title")
        self.plot_subtitle: Text | None = get("plot_subtitle")
        self.plot_caption: Text | None = get("plot_caption")
        self.plot_footer: Text | None = get("plot_footer")
        self.plot_footer_background: Rectangle | None = get(
            "plot_footer_background"
        )
        self.plot_footer_line: Line2D | None = get("plot_footer_line")

    def _is_blank(self, name: str) -> bool:
        return self.cmp.theme.T.is_blank(name)

    def _move_artists(self, spaces: CompositionSideSpaces):
        """
        Move the annotations to their final positions
        """
        theme = self.cmp.theme
        plot_title_position = theme.getp("plot_title_position", "panel")
        plot_caption_position = theme.getp("plot_caption_position", "panel")
        plot_footer_position = theme.getp("plot_footer_position", "plot")
        justify = TextJustifier.from_boundaries(
            spaces.cmp.figure,
            plot_left=spaces.plot_left,
            plot_right=spaces.plot_right,
            plot_bottom=spaces.plot_bottom,
            plot_top=spaces.plot_top,
            panel_left=spaces.panel_left,
            panel_right=spaces.panel_right,
            panel_bottom=spaces.panel_bottom,
            panel_top=spaces.panel_top,
        )

        if self.plot_title:
            ha = theme.getp(("plot_title", "ha"))
            self.plot_title.set_y(spaces.t.y2("plot_title"))
            justify.horizontally_about(
                self.plot_title, ha, plot_title_position
            )

        if self.plot_subtitle:
            ha = theme.getp(("plot_subtitle", "ha"))
            self.plot_subtitle.set_y(spaces.t.y2("plot_subtitle"))
            justify.horizontally_about(
                self.plot_subtitle, ha, plot_title_position
            )

        if self.plot_caption:
            ha = theme.getp(("plot_caption", "ha"), "right")
            self.plot_caption.set_y(spaces.b.y1("plot_caption"))
            justify.horizontally_about(
                self.plot_caption, ha, plot_caption_position
            )

        if self.plot_footer:
            ha = theme.getp(("plot_footer", "ha"), "left")
            self.plot_footer.set_y(spaces.b.y1("plot_footer"))
            justify.horizontally_about(
                self.plot_footer, ha, plot_footer_position
            )
            if self.plot_footer_background:
                resize_footer_background(
                    self.plot_footer_background,
                    x=spaces.l.offset,
                    y=spaces.b.offset,
                    height=spaces.b.footer_height,
                    width=spaces.plot_width,
                )
            if self.plot_footer_line:
                resize_footer_line(
                    self.plot_footer_line,
                    x=spaces.l.offset,
                    width=spaces.plot_width,
                    y=spaces.b.offset + spaces.b.footer_height,
                )
