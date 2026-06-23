from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from matplotlib.patches import FancyBboxPatch
from matplotlib.text import Text

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotnine.typing import StripPosition


class StripText(Text):
    """
    Strip Text
    """

    patch: FancyBboxPatch
    position: StripPosition

    def __init__(
        self,
        ax: Axes,
        position: StripPosition,
        label: str,
    ):
        self.position = position
        is_oneline = len(label.split("\n")) == 1
        kwargs = {
            "transform": ax.transAxes,
            "clip_on": False,
            "zorder": 3.3,
            # The strip_text themeable rotates the text. We anchor it at
            # the center so that alignment holds under any rotation it
            # applies. Vertically, center_baseline places the text in the
            # visual center, but only if it is one line. For multiline
            # text, we are better off with plain center.
            "ha": "center",
            "va": "center_baseline" if is_oneline else "center",
            "rotation_mode": "anchor",
        }

        super().__init__(0, 0, label, **kwargs)
        self.ax = ax
        self.patch = FancyBboxPatch(
            (0, 0),
            width=1,
            height=1,
            boxstyle="square, pad=0",
            clip_on=False,
            zorder=2.2,
        )
        # The layout manager groups patches by the side they sit on
        self.patch.position = position  # pyright: ignore[reportAttributeAccessIssue]

    # TODO: This should really be part of the unit conversions in the
    # margin class.
    @lru_cache(2)
    def _line_height(self, renderer) -> float:
        """
        The line height in display space of the text on the canvas
        """
        # Text string, (width, height), x, y
        parts: list[tuple[str, tuple[float, float], float, float]]

        try:
            # matplotlib.Text._get_layout is a private API. If its name or
            # return shape changes we fall back to an estimate.
            _, parts, _ = self._get_layout(renderer)  # pyright: ignore[reportAttributeAccessIssue]
        except (AttributeError, ValueError, TypeError):
            from warnings import warn

            from plotnine.exceptions import PlotnineWarning

            # The canvas height is nearly always bigger than the stated
            # fontsize. 1.36 is a good multiplication factor obtained by
            # some rough exploration. A non-numeric size (e.g. "large")
            # falls back to a fixed estimate.
            f = 1.36
            size = self.get_fontsize()
            height = size * f if isinstance(size, (int, float)) else 14
            warn(
                f"Could not calculate line height for {self.get_text()}. "
                "Using an estimate, please let us know about this at "
                "https://github.com/has2k1/plotnine/issues",
                PlotnineWarning,
            )
        else:
            # The the text has multiple lines, we use the maximum height
            # of anyone single line.
            height = max([p[1][1] for p in parts])

        return height
