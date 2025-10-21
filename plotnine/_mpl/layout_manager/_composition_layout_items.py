from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from matplotlib.text import Text

from plotnine._mpl.utils import (
    ArtistGeometry,
    JustifyBoundaries,
    TextJustifier,
)

if TYPE_CHECKING:
    from typing import Any

    from plotnine.composition._compose import Compose

    from ._composition_side_space import CompositionLayoutSpaces


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

    def _is_blank(self, name: str) -> bool:
        return self.cmp.theme.T.is_blank(name)

    def _adjust_positions(self, spaces: CompositionLayoutSpaces):
        theme = self.cmp.theme
        plot_title_position = theme.getp("plot_title_position", "panel")
        plot_caption_position = theme.getp("plot_caption_position", "panel")
        justify = CompositionTextJustifier(spaces)

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


class CompositionTextJustifier(TextJustifier):
    """
    Justify Text about a composition or it's panels
    """

    def __init__(self, spaces: CompositionLayoutSpaces):
        boundaries = JustifyBoundaries(
            plot_left=spaces.l.composition_left,
            plot_right=spaces.r.composition_right,
            plot_bottom=spaces.b.composition_bottom,
            plot_top=spaces.t.composition_top,
            panel_left=spaces.l.composition_panel_left,
            panel_right=spaces.r.composition_panel_right,
            panel_bottom=spaces.b.composition_panel_bottom,
            panel_top=spaces.t.composition_panel_top,
        )
        super().__init__(spaces.cmp.figure, boundaries)
