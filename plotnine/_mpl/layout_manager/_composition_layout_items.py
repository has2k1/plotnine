from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.text import Text

from plotnine._mpl.utils import ArtistGeometry

if TYPE_CHECKING:
    from typing import Any

    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle

    from plotnine.composition._compose import Compose
    from plotnine.iapi import legend_artists

    from ._composition_side_space import CompositionSideSpaces


class CompositionLayoutItems:
    """
    plot_annotation artists
    """

    def __init__(self, cmp: Compose, *, is_root: bool = True):
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
        self.is_root = is_root
        self.geometry = ArtistGeometry(cmp.figure)

        self.plot_title: Text | None = get("plot_title")
        self.plot_subtitle: Text | None = get("plot_subtitle")
        self.plot_caption: Text | None = get("plot_caption")
        self.plot_footer: Text | None = get("plot_footer")
        self.plot_footer_background: Rectangle | None = get(
            "plot_footer_background"
        )
        self.plot_footer_line: Line2D | None = get("plot_footer_line")
        self.legends: legend_artists | None = get("legends")

    def _is_blank(self, name: str) -> bool:
        return self.cmp.theme.T.is_blank(name)

    def _move_artists(self, spaces: CompositionSideSpaces):
        """
        Move the annotations and legends to their final positions
        """
        from ._plot_layout_items import (
            _position_legends,
            _position_plot_labels,
        )

        # Only the root composition can have annotations (labels).
        # So positioning them is a no-op. Skip the traversal entirely.
        if self.is_root:
            _position_plot_labels(
                spaces.cmp.figure, self.cmp.theme, spaces, self
            )
        if self.legends:
            _position_legends(self.legends, spaces)
