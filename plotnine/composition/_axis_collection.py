"""
Axis and axis title collection for plot compositions
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from .._utils import OPPOSITE_SIDE

if TYPE_CHECKING:
    from typing import Iterable

    from plotnine import ggplot, theme
    from plotnine._mpl.layout_manager._grid import Grid
    from plotnine._mpl.layout_manager._plot_side_space import PlotSideSpaces
    from plotnine.scales.scale_xy import ScaleX, ScaleY
    from plotnine.typing import Side


AXIS_TEXT_AND_TICKS: dict[Side, tuple[str, str, str]] = {
    "bottom": (
        "axis_text_x_bottom",
        "axis_ticks_major_x_bottom",
        "axis_ticks_minor_x_bottom",
    ),
    "top": (
        "axis_text_x_top",
        "axis_ticks_major_x_top",
        "axis_ticks_minor_x_top",
    ),
    "left": (
        "axis_text_y_left",
        "axis_ticks_major_y_left",
        "axis_ticks_minor_y_left",
    ),
    "right": (
        "axis_text_y_right",
        "axis_ticks_major_y_right",
        "axis_ticks_minor_y_right",
    ),
}
"""
Themeable names for axis ticks and tick labels, indexed by side
"""

AXIS_TITLE: dict[Side, str] = {
    "bottom": "axis_title_x_bottom",
    "top": "axis_title_x_top",
    "left": "axis_title_y_left",
    "right": "axis_title_y_right",
}
"""
Themeable name for each axis title, indexed by side
"""


def axis_titles(plot: ggplot) -> dict[Side, str]:
    """
    Resolve a plot's axis titles by side without building it

    A position scale's name overrides its mapped label. A secondary axis
    titles the side opposite its primary, and the coordinate system can
    swap the x and y labels. Omit sides without titles.

    Resolve labels on a copy to preserve the plot's unbuilt state.

    Parameters
    ----------
    plot :
        Plot to inspect, whether built or unbuilt.

    Returns
    -------
    :
        Title text for each side that has one.
    """
    labels = copy(plot.labels)
    labels.add_defaults(plot.mapping.labels)
    plot.layers.update_labels(labels)
    labels = plot.coordinates.labels(labels)
    # The scale annotation permits strings, but every position is a `Side`.
    x_side, y_side = cast("tuple[Side, Side]", plot.scales.axis_positions)

    titles: dict[Side, str] = {}
    positions: tuple[tuple[Side, ScaleX | ScaleY | None, str | None], ...] = (
        (x_side, plot.scales.x, labels.x),
        (y_side, plot.scales.y, labels.y),
    )
    for side, scale, label in positions:
        name = scale.name if scale is not None else None
        title = name or label or ""
        if title:
            titles[side] = title

        # Discrete position scales do not support secondary axes.
        sec = getattr(scale, "sec_axis", None)
        if sec is not None:
            sec_title = title if sec.name is None else sec.name
            if sec_title:
                titles[OPPOSITE_SIDE[side]] = sec_title

    return titles


def blank_theme(names: Iterable[str]) -> theme:
    """
    Return a theme that blanks the named themeables

    Parameters
    ----------
    names :
        Themeable names.

    Returns
    -------
    :
        Theme that sets each name to `element_blank`.
    """
    from plotnine import element_blank, theme

    return theme(**{name: element_blank() for name in names})  # pyright: ignore[reportArgumentType]


@dataclass(frozen=True)
class PanelSpan:
    """
    Combined bounds of one or more plot panels in figure space
    """

    spaces: tuple[PlotSideSpaces, ...]
    """
    Plot side spaces that define the combined bounds
    """

    @property
    def left(self) -> float:
        """
        Leftmost panel edge in figure space
        """
        return min(s.panel_left for s in self.spaces)

    @property
    def right(self) -> float:
        """
        Rightmost panel edge in figure space
        """
        return max(s.panel_right for s in self.spaces)

    @property
    def bottom(self) -> float:
        """
        Lowest panel edge in figure space
        """
        return min(s.panel_bottom for s in self.spaces)

    @property
    def top(self) -> float:
        """
        Highest panel edge in figure space
        """
        return max(s.panel_top for s in self.spaces)


# Keep remover equality independent of plot equality; visual tests replace
# plot equality with baseline-image comparison.
@dataclass(eq=False)
class AxisRemover:
    """
    Axis elements relinquished by one plot during collection
    """

    plot: ggplot
    """
    Plot being considered for axis collection
    """

    titles: dict[Side, str]
    """
    Axis titles indexed by side
    """

    dropped: set[Side]
    """
    Sides whose axes this plot relinquishes
    """

    blanks: list[str] = field(default_factory=list)
    """
    Themeables to blank after all sides are resolved
    """

    @classmethod
    def make(
        cls, plot: ggplot, grid: Grid, sides: frozenset[Side]
    ) -> AxisRemover:
        """
        Build axis removal state for a plot

        Relinquish each selected side when another grid item lies beyond
        the plot on that side.

        Parameters
        ----------
        plot :
            Direct plot to inspect.
        grid :
            Composition grid containing the plot and neighbouring items.
        sides :
            Sides that collect axes.

        Returns
        -------
        :
            Axis removal state with resolved titles, relinquished sides,
            and themeables to blank.
        """
        dropped: set[Side] = {
            s for s in sides if not grid.is_outermost(plot, s)
        }
        blanks = [n for s in dropped for n in AXIS_TEXT_AND_TICKS[s]]
        return cls(plot, axis_titles(plot), dropped, blanks)

    def shows_axis(self, side: Side) -> bool:
        """
        Return whether the plot retains its axis on `side`

        Parameters
        ----------
        side :
            Side of the plot to ask about.

        Returns
        -------
        :
            Whether the axis on that side survived collection.
        """
        return side not in self.dropped

    def remove_title(self, side: Side):
        """
        Mark the axis title on `side` for removal

        Parameters
        ----------
        side :
            Side whose title the plot gives up.
        """
        self.blanks.append(AXIS_TITLE[side])

    def apply(self):
        """
        Blank the axis elements this plot relinquished
        """
        if self.blanks:
            self.plot.theme += blank_theme(self.blanks)


def collect_title(side: Side, removers: list[AxisRemover], grid: Grid):
    """
    Collect matching axis titles on one side

    Remove a title when its axis was relinquished. If two or more retained
    axes share a title, keep the title nearest the requested grid side and
    record the panels it spans. Leave differing titles unchanged.

    Parameters
    ----------
    side :
        Side to collect the title on.
    removers :
        Collection state for each direct plot, in composition item order.
    grid :
        Composition grid containing those plots.
    """
    for r in removers:
        if side in r.titles and not r.shows_axis(side):
            r.remove_title(side)

    participants = [
        r for r in removers if side in r.titles and r.shows_axis(side)
    ]
    texts = {r.titles[side] for r in participants}
    if len(participants) < 2 or len(texts) != 1:
        return

    # Both extrema preserve the first participant in a tie, so composition
    # order selects the title keeper.
    nearest = min if side in ("top", "left") else max
    keeper = nearest(participants, key=lambda r: grid.edge_index(r.plot, side))
    for r in participants:
        if r is not keeper:
            r.remove_title(side)

    keeper.plot._axis_title_span[side] = tuple(r.plot for r in participants)
