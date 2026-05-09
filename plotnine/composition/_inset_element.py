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

Each inset occupies its own zorder band above or below the host. With zorder
offsets relative to the host's `_zorder`:

    +20  -----  above-inset 2
    +10  -----  above-inset 1     (on_top=True)
      0  =====  host
    -10  -----  below-inset 1     (on_top=False, last declared)
    -20  -----  below-inset 2     (first declared)

A band's within-plot stack runs from `plot_background` (-0.5) to
`watermark` (+9), so STEP = 10 keeps consecutive bands clear. When
the host has below-insets, `_draw_plot_background` drops the host's
`plot_background` one STEP beneath the lowest below-band, so they
all paint above it.
"""


@dataclass
class inset_element:
    """
    Place a plot as an inset within another plot

    By default the inset is rendered on top of the host (`on_top=True`).
    With `on_top=False` it is rendered behind the host's panel and
    labels but above the host's `plot_background`. Adding an
    `inset_element` to a composition attaches it to the most recently
    added plot in that composition.

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
    on_top :
        When `True` (default) the inset paints above the host plot.
        When `False`, the inset paints between the host's
        `plot_background` and the rest of the host (panel, titles,
        legends, ...), so the host's panel area covers the inset.
        Useful for backdrops, decorations, or branding that should
        look like part of the page rather than an overlay.

    Notes
    -----
    `figure_size` and `dpi` set on the inset's theme are ignored. The
    inset shares the host's figure, so these values come from the host
    theme. The canvas size of the inset is determined by the bounding
    box and the area it is `align_to`.
    """

    obj: ggplot | Compose
    left: float
    bottom: float
    right: float
    top: float
    align_to: Literal["panel", "plot", "full"] = "panel"
    on_top: bool = True

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

    def _setup(self, parent: ggplot, zorder_offset: int):
        """
        Receive the host figure and zorder from parent

        Parameters
        ----------
        parent :
            The host plot whose figure and zorder this inset adopts.
        zorder_offset :
            How to place this inset relative to the host.
            Positive for above-insets, negative for below-insets.
        """
        self.obj.figure = parent.figure
        self.obj._zorder = parent._zorder + zorder_offset
        self.obj.theme._inherit_figure_props(parent.theme)

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

        Later-declared insets paint above earlier-declared insets in
        *both* bands: above-band stacks upward in declaration order;
        below-band reverses so the last-declared inset gets the
        smallest `|offset|` (closest to the host).
        """
        above = [i for i in self if i.on_top]
        below = [i for i in self if not i.on_top]

        for n, inset in enumerate(above, start=1):
            inset._setup(parent, n * INSET_ZORDER_STEP)

        for n, inset in enumerate(reversed(below), start=1):
            inset._setup(parent, -n * INSET_ZORDER_STEP)

    @property
    def plot_background_offset(self) -> float:
        """
        zorder offset for the host's `plot_background`

        It is a relative offset used to place the `plot_background`
        below every below-inset's stack.

        Returns
        -------
        :
            Zorder offset relative to the host's `_zorder`.
            `-0.5` when no below-insets are attached.
        """
        n_below = sum(not i.on_top for i in self)
        if n_below == 0:
            return -0.5
        # Sit one full band below the deepest below-inset, whose
        # own plot_background lives at this offset:
        deepest_below_bg = -n_below * INSET_ZORDER_STEP - 0.5
        return deepest_below_bg - INSET_ZORDER_STEP

    def draw(self, which: Literal["above", "below"]):
        """
        Render insets in a single band, in paint order

        Parameters
        ----------
        which :
            ``"above"`` paints above-insets only, in declaration
            order. ``"below"`` paints below-insets only,
            last-declared first so it lands closest to the host.
        """
        if which == "above":
            insets = [inset for inset in self if inset.on_top]
        else:
            insets = [inset for inset in self if not inset.on_top][::-1]

        for inset in insets:
            inset.draw()
