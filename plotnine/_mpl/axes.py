from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from matplotlib import cbook
from matplotlib.axes import Axes
from matplotlib.axis import XAxis, YAxis
from matplotlib.projections import register_projection

if TYPE_CHECKING:
    from plotnine.typing import Side

AxisT = TypeVar("AxisT", XAxis, YAxis)


class p9Axes(Axes):
    """
    Axes of a plotnine panel

    In addition to the regular x & y axes, a panel can hold one
    secondary axis per dimension (`sec_xaxis`/`sec_yaxis`), drawn on
    the side opposite the primary with its own fixed breaks and labels.

    The panel is the shared substrate (data space, patch, grid, and the
    four spines); each `Axis` carries the per-axis state (ticks,
    labels, locator/formatter, and its active side); a secondary axis
    is just one more `Axis` living in the panel's data space.

    Spines start hidden; each axis shows the panel spine of the side it
    occupies.
    """

    name = "plotnine"

    # mpl resolves every Axis operation through the per-name axis
    # registries; the secondary axes register under their own names.
    _shared_axes = {
        **Axes._shared_axes,  # pyright: ignore[reportAttributeAccessIssue]
        "sec_x": cbook.Grouper(),
        "sec_y": cbook.Grouper(),
    }

    # The secondary axis of each dimension; None until added
    sec_xaxis: XAxis | None
    sec_yaxis: YAxis | None

    # Sides of the panel that carry an axis (primary or secondary);
    # setup shows their spines.
    sides_with_an_axis: set[Side]

    def __init__(self, *args, **kwargs):
        self.sec_xaxis = None
        self.sec_yaxis = None
        self.sides_with_an_axis = set()
        super().__init__(*args, **kwargs)
        self._sharesec_x = None
        self._sharesec_y = None
        # Spines are opt-in: each axis (primary or secondary) shows
        # the spine of the side it occupies.
        self.spines[:].set_visible(False)

    def add_sec_axis(self, side: Side) -> XAxis | YAxis:
        """
        Return the secondary axis for `side`, creating it if needed

        The axis starts bare — no breaks, labels or active side; the
        caller configures it like any other axis.

        Parameters
        ----------
        side :
            Side of the panel the secondary axis will occupy.

        Returns
        -------
        :
            The secondary axis of the side's dimension.
        """
        if side in ("top", "bottom"):
            if self.sec_xaxis is None:
                self.sec_xaxis = self._make_sec_axis(XAxis, "sec_x")
            return self.sec_xaxis
        else:
            if self.sec_yaxis is None:
                self.sec_yaxis = self._make_sec_axis(YAxis, "sec_y")
            return self.sec_yaxis

    def _make_sec_axis(self, cls: type[AxisT], name: str) -> AxisT:
        axis = cls(self)
        # Register the axis so mpl can resolve its name, and add it to
        # the draw tree. Panels are never cleared after this point;
        # Axes.clear() would detach the artist.
        self._axis_map[name] = axis
        self.add_artist(axis)
        axis.set_clip_on(False)
        axis.grid(False)
        return axis


def axis_at(ax: Axes, side: Side) -> XAxis | YAxis | None:
    """
    Return the axis of `ax` whose ticks occupy `side`, if any

    Considers the primary axis of the side's dimension and, on a
    `p9Axes`, the secondary one.

    Parameters
    ----------
    ax :
        Panel axes.
    side :
        Side of the panel.

    Returns
    -------
    :
        The axis with active ticks on `side`, or `None` when that side
        shows no ticks (e.g. an interior facet panel).
    """
    if side in ("top", "bottom"):
        candidates = (ax.xaxis, getattr(ax, "sec_xaxis", None))
    else:
        candidates = (ax.yaxis, getattr(ax, "sec_yaxis", None))
    for axis in candidates:
        if axis and axis.get_tick_params(which="major").get(side):
            return axis
    return None


register_projection(p9Axes)
