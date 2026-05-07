from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..ggplot import ggplot
    from ._compose import Compose


INSET_ZORDER_STEP = 10
"""
Width of the zorder band reserved for each inset

The Nth sibling inset is drawn at `host._zorder + N * INSET_ZORDER_STEP`,
so every figure-level artist on a later inset (axes, plot_background,
titles, strip text, legends, ...) sits above every figure-level artist
on an earlier inset and the host. The step must exceed the largest
within-plot figure-level zorder — watermarks at 9 — by enough that the
next band's lowest artist (`plot_background` at -0.5) still clears it.
"""


@dataclass
class inset_element:
    """
    Place a plot as an inset within another plot

    The inset is rendered on top of the host. Adding an `inset_element`
    to a composition attaches it to the most recently added plot in that
    composition.

    Parameters
    ----------
    obj :
        The object to render as an inset.
    left, bottom, right, top :
        Bounding box of the inset as fractional coordinates in the
        range ``[0, 1]``, relative to the host region selected by
        `align_to`. The bottom-left corner of that region is
        ``(0, 0)`` and the top-right is ``(1, 1)``.
    align_to :
        Which region of the host plot the bounding box is relative to:

        - ``"panel"`` — the data area only (default).
        - ``"plot"``  — the panel plus axes, labels, titles, captions
           and legends
        - ``"full"``  — everything the host plot occupies plus plot margin
    """

    obj: ggplot | Compose
    left: float
    bottom: float
    right: float
    top: float
    align_to: Literal["panel", "plot", "full"] = "panel"

    def __post_init__(self):
        from ..ggplot import ggplot
        from ._compose import Compose

        if not isinstance(self.obj, (ggplot, Compose)):
            raise TypeError(
                "inset_element requires a ggplot or Compose, got "
                f"{type(self.obj).__name__!r}."
            )

        if not 0.0 <= self.left < self.right <= 1.0:
            raise ValueError(
                "inset_element requires 0.0 <= left < right <= 1.0, got "
                f"left={self.left!r}, right={self.right!r}."
            )

        if not 0.0 <= self.bottom < self.top <= 1.0:
            raise ValueError(
                "inset_element requires 0.0 <= bottom < top <= 1.0, got "
                f"bottom={self.bottom!r}, top={self.top!r}."
            )

    def _setup(self, parent: ggplot, index: int):
        """
        Receive the host figure and zorder from parent

        `index` is the 1-based position of this inset among its siblings.
        Each sibling occupies its own zorder band so a later inset's
        figure-level artists all sit above an earlier inset's.
        """
        self.obj.figure = parent.figure
        self.obj._zorder = parent._zorder + index * INSET_ZORDER_STEP

    def draw(self):
        """
        Render this inset
        """
        self.obj.draw()

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Attach this inset to a ggplot
        """
        other._insets.append(deepcopy(self))
        return other


class Insets(list[inset_element]):
    """
    List of insets attached to a ggplot
    """

    def _setup(self, parent: ggplot):
        """
        Receive the host figure and zorder for every inset
        """
        for i, inset in enumerate(self, start=1):
            inset._setup(parent, i)

    def draw(self):
        """
        Render every inset attached to the host
        """
        for inset in self:
            inset.draw()
