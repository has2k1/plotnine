from __future__ import annotations

from dataclasses import replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from warnings import warn

import numpy as np

from .._mpl._radial_axes import p9RadialAxes  # noqa: TCH001
from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from ..iapi import panel_ranges, radial_panel_view
from .coord import _activate_axis, _set_fixed_ticks, coord, dist_euclidean

if TYPE_CHECKING:
    import numpy.typing as npt
    import pandas as pd
    from matplotlib.axes import Axes

    from plotnine.iapi import labels_view, layout_details, panel_view
    from plotnine.scales.scale import scale
    from plotnine.typing import FloatArrayLike, FloatSeries, Side

T1 = TypeVar("T1")
T2 = TypeVar("T2")


def polar_bbox(
    arc: tuple[float, float], inner_radius: float = 0.0
) -> tuple[float, float, float, float]:
    """
    Tight bounding box of a polar sector in unit-circle coordinates

    The box is expressed as `(left, right, bottom, top)` in the `[0, 1]`
    space of the full circle, where the centre is `(0.5, 0.5)` and the
    outer radius is `0.5`. A cardinal direction (top, right, bottom, left)
    that lies inside the arc extends the box to the circle's full extent
    there; otherwise the box is clamped to the arc endpoints. `inner_radius`
    pulls the inner edge toward the centre for donut sectors. No margin is
    added, so the box matches the wedge the panel is sized to fill.
    """
    lo, hi = arc
    if abs(hi - lo) >= 2 * np.pi:
        return (0.0, 1.0, 0.0, 1.0)

    lo, hi = sorted((lo, hi))
    ends = np.array([lo, hi])
    x_outer = 0.5 * np.sin(ends) + 0.5
    y_outer = 0.5 * np.cos(ends) + 0.5
    # `inner_radius` is a fraction of the outer radius, and the outer
    # radius is 0.5 in this unit-circle space, so the inner ring sits at
    # `inner_radius * 0.5` from the centre.
    r_inner = inner_radius * 0.5
    x_inner = r_inner * np.sin(ends) + 0.5
    y_inner = r_inner * np.cos(ends) + 0.5

    def in_arc(theta: float) -> bool:
        folded = (theta - lo) % (2 * np.pi) + lo
        return lo <= folded <= hi

    top = 1.0 if in_arc(0.0) else max(y_outer.max(), y_inner.max())
    right = 1.0 if in_arc(np.pi / 2) else max(x_outer.max(), x_inner.max())
    bottom = 0.0 if in_arc(np.pi) else min(y_outer.min(), y_inner.min())
    left = 0.0 if in_arc(1.5 * np.pi) else min(x_outer.min(), x_inner.min())
    return (float(left), float(right), float(bottom), float(top))


class coord_radial(coord):
    """
    Radial coordinate system

    A system where position aesthetic is mapped to the angle and the other
    to the radius.

    Parameters
    ----------
    theta :
        Which variable maps to the angle axis, `"x"` (default) or `"y"`.
    start :
        Starting angle in radians, measured clockwise from 12 o'clock.
        Default 0.
    end :
        Ending angle in radians, measured clockwise from 12 o'clock.
        Equivalent angles are interpreted as the same endpoint. `None`
        (default) gives a full circle.
    expand :
        Add a small buffer around the data on the radius axis.
        Default `True`.
    inner_radius :
        Size of the inner hole as a fraction of the outer radius, in
        `[0, 1)`.  `0` (default) means no hole; `0.3` creates a 30 %
        donut hole, useful for gauge and donut charts.
    rotate_angle :
        If `True`, rotate the `angle` aesthetic so that text or other
        rotated marks align tangentially with the arc at their spoke. The
        rotation is folded so labels stay upright (readable) rather than
        appearing upside-down in the lower half.  Default `False`.
    thetalim :
        Data-space limits for the theta axis as `(lo, hi)`.  Only data
        within this range is mapped to the arc; equivalent to zooming on the
        angular axis.  `None` (default) uses the full data range.
    rlim :
        Data-space limits for the r axis as `(lo, hi)`.  Only data within
        this range is shown; equivalent to zooming on the radial axis.
        `None` (default) uses the full data range.
    reverse :
        Which axes run in the opposite direction.

        * `"none"` (default) — neither axis is reversed.
        * `"theta"` — the angular axis runs the other way around the
          same arc, so the data sweeps from `end` back to `start`.
        * `"r"` — the radial axis is inverted, so large values sit
          toward the centre.
        * `"thetar"` — both the angular and radial axes are reversed.

        The sweep itself is always clockwise. A full circle runs the other
        way with `reverse="theta"`; a partial arc mirrors onto the opposite
        side with `start=-end, end=-start, reverse="theta"`.

    Notes
    -----
    Theta-axis tick labels are shown by default. Since a polar axes' x-axis
    *is* the theta axis, they are styled through the theme: hide them with
    `theme(axis_text_x=element_blank())` and adjust the gap to the outer
    circle through the `axis_text_x` margin.
    """

    is_linear = False
    _projection = "p9radial"

    def __init__(
        self,
        theta: str = "x",
        start: float = 0,
        end: float | None = None,
        expand: bool = True,
        inner_radius: float = 0,
        rotate_angle: bool = False,
        thetalim: tuple[float, float] | None = None,
        rlim: tuple[float, float] | None = None,
        reverse: Literal["none", "theta", "r", "thetar"] = "none",
    ) -> None:
        if reverse not in {"none", "theta", "r", "thetar"}:
            raise ValueError(
                "reverse must be one of 'none', 'theta', 'r', 'thetar'; "
                f"got {reverse!r}."
            )
        self.theta = theta
        self.start = start
        self.end = end
        self.expand = expand
        self.inner_radius = inner_radius
        self.rotate_angle = rotate_angle
        self.thetalim = thetalim
        self.rlim = rlim
        self.reverse = reverse

    @property
    def is_default_axes(self) -> bool:
        return self.theta == "x"

    def _flip(self, p1: T1, p2: T2) -> tuple[T1, T2] | tuple[T2, T1]:
        return (p1, p2) if self.is_default_axes else (p2, p1)

    def setup_panel_params(
        self, scale_x: scale, scale_y: scale
    ) -> radial_panel_view:
        """
        Compute the range and break information for the panel

        The panel_params are created in only this method. If the axes
        have been switched (i.e. `theta = "y"`) from the default
        (`theta = "x"` is the default), the panel_params are adjusted
        accordingly.
        """
        from .coord_cartesian import coord_cartesian

        # One expanded cartesian view supplies both the theta/r ranges and
        # the theta breaks. Theta follows the expand flag like every other
        # axis: expand=True buffers the data off the arc ends; expand=False
        # keeps it flush so a pie closes cleanly.
        xlim, ylim = self._flip(self.thetalim, self.rlim)
        cartesian_view = coord_cartesian(
            xlim=xlim, ylim=ylim, expand=self.expand
        ).setup_panel_params(scale_x, scale_y)
        theta, r = self._flip(cartesian_view.x, cartesian_view.y)
        theta.breaks = cast("list[float]", theta.breaks)
        arc_range = self._arc_range

        # The display range keeps its requested order; a full circle ends
        # one turn after start. Data ticks are converted to radians below.
        x = replace(
            theta,
            limits=arc_range,
            range=arc_range,
            breaks=self._to_radians(theta.breaks, theta.range),
            minor_breaks=np.asarray(
                self._to_radians(theta.minor_breaks, theta.range)
            ),
            labels=list(theta.labels),
        )
        y = replace(r)

        # Partial arcs keep only breaks inside their visible bounds.
        if not self._is_full_circle:
            arc_lo, arc_hi = sorted(arc_range)
            x_breaks = cast("list[float]", x.breaks)
            keep = [arc_lo <= value <= arc_hi for value in x_breaks]
            x = replace(
                x,
                breaks=[
                    value for value, include in zip(x_breaks, keep) if include
                ],
                minor_breaks=[
                    value
                    for value in x.minor_breaks
                    if arc_lo <= value <= arc_hi
                ],
                labels=[
                    label for label, include in zip(x.labels, keep) if include
                ],
            )

        # Keep r in trained scale space. For radial reversal, make y match
        # the display space produced by a reversed scale; descending polar
        # limits alone do not reverse radial geometry.
        if self.reverse in ("r", "thetar"):
            r_limits = cast("tuple[float, float]", r.limits)
            r_breaks = cast("list[float]", r.breaks)
            # The secondary axis lives in the same reversed display frame,
            # so its breaks are negated alongside the primary ones; leaving
            # them positive would place its ticks outside the data band and
            # stretch the radial range.
            r_sec = r.sec
            if r_sec is not None:
                r_sec = replace(
                    r_sec, breaks=[-value for value in r_sec.breaks]
                )
            y = replace(
                y,
                limits=(-r_limits[1], -r_limits[0]),
                range=(-r.range[1], -r.range[0]),
                breaks=[-value for value in r_breaks],
                minor_breaks=-np.asarray(r.minor_breaks, dtype=float),
                labels=list(r.labels),
                sec=r_sec,
            )

        # theta="y" transposes the x and y views, so their axis position
        # rotates with them (matching coord_flip): the angular title lands
        # on x's bottom/top and the radial title on y's left/right, the
        # sides the layout manager repositions. theta="x" keeps them as is.
        if not self.is_default_axes:
            from .coord_flip import _FLIP_POSITION

            x = replace(x, position=_FLIP_POSITION[x.position])
            y = replace(y, position=_FLIP_POSITION[y.position])
            for sv in (x, y):
                if sv.sec:
                    # A secondary theta axis is rejected in setup_ax, so a
                    # secondary position here is always cartesian.
                    pos = cast("Side", sv.sec.position)
                    sv.sec.position = _FLIP_POSITION[pos]

        return radial_panel_view(x=x, y=y, theta=theta, r=r)

    def labels(self, cur_labels: labels_view) -> labels_view:
        labels = super().labels(cur_labels)
        if self.theta == "x":
            return labels

        # The default theta="x", so when theta="y", we also swap the labels
        # and axis titles.
        from .coord_flip import flip_labels

        return flip_labels(labels)

    @cached_property
    def _arc_range(self) -> tuple[float, float]:
        """
        Forward angular limits of the displayed arc

        Equivalent endpoints select the same clockwise arc. An explicit
        non-zero whole turn remains a full circle, while equal endpoints
        remain a zero-width arc.
        """
        turn = 2 * np.pi
        if self.end is None:
            return (self.start, self.start + turn)

        delta = self.end - self.start
        if delta == 0:
            return (self.start, self.start)

        span = delta % turn
        if span == 0:
            span = turn
        return (self.start, self.start + span)

    @cached_property
    def _is_full_circle(self) -> bool:
        """True when the displayed arc covers one complete turn"""
        start, end = self._arc_range
        return bool(np.isclose(end - start, 2 * np.pi))

    @cached_property
    def _r_axis_side(self) -> Literal["r_start", "r_end"]:
        """
        Polar side the radial axis occupies

        The radial axis sits where the data begins. `reverse="theta"` runs
        the data from `end` back to `start`, so a partial arc moves the axis
        to the end spoke. A full circle has a single shared spoke, so it
        stays at the start.
        """
        if self.reverse in ("theta", "thetar") and not self._is_full_circle:
            return "r_end"
        return "r_start"

    @cached_property
    def _sec_r_axis_side(self) -> Literal["r_start", "r_end"]:
        """
        Polar side the secondary radial axis occupies

        The secondary axis sits on the spoke opposite the primary one, so it
        follows the primary when `reverse="theta"` moves it to the end spoke.
        """
        return "r_start" if self._r_axis_side == "r_end" else "r_end"

    def _to_radians(
        self, vals: FloatArrayLike, theta_range: tuple[float, float]
    ) -> list[float]:
        """Normalize theta values to [start, start + arc]"""
        lo, hi = theta_range
        span = hi - lo

        if span == 0:
            return [0] * len(vals)

        arc_start, arc_end = self._arc_range
        norm = (np.asarray(vals) - lo) / span
        # Traverse the same arc the other way, so data runs from
        # end back to start.
        if self.reverse in ("theta", "thetar"):
            norm = 1 - norm
        return list(arc_start + norm * (arc_end - arc_start))

    def transform(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        munch: bool = False,
    ) -> pd.DataFrame:
        # Munch first (in original data space) so curved edges get enough
        # interpolation points before we convert theta → radians.
        if munch:
            data = self.munch(data, panel_params)

        if "x" not in data or "y" not in data:
            return data

        t = self._flip("x", "y")[0]
        tend = self._flip("xend", "yend")[0]
        view = cast("radial_panel_view", panel_params)

        data = data.copy()
        data[t] = self._to_radians(data[t], view.theta.range)
        if tend in data.columns:
            data[tend] = self._to_radians(data[tend], view.theta.range)

        # PolarAxes always expects x = theta (radians) and y = r.
        # When theta = "y" we need to swap the columns.
        if not self.is_default_axes:
            data["x"], data["y"] = data["y"], data["x"]
            if "xend" in data and "yend" in data:
                data["xend"], data["yend"] = data["yend"], data["xend"]

        if self.reverse in ("r", "thetar"):
            data["y"] = -data["y"]
            if "yend" in data:
                data["yend"] = -data["yend"]

        # After the swap, data["x"] is always theta in radians.
        if self.rotate_angle and "angle" in data and "x" in data:
            # Align marks tangentially to their spoke. The PolarAxes places
            # a data theta t at on-screen angle (deg, CCW from East)
            #   screen = 90 - degrees(t),  since the sweep is clockwise
            # Tangential text rotation is screen - 90; folding into (-90, 90]
            # keeps labels upright (a bottom label reads "6", not "9").
            rot = -np.degrees(data["x"])
            rot = (rot + 90.0) % 180.0 - 90.0
            data["angle"] = data["angle"] + rot
        return data

    def distance(
        self,
        x: FloatSeries,
        y: FloatSeries,
        panel_params: panel_view,
    ) -> npt.NDArray[Any]:
        # Normalise theta and r to [0, 1] then compute Euclidean distance.
        view = cast("radial_panel_view", panel_params)

        t_lo, t_hi = view.theta.range
        r_lo, r_hi = view.r.range

        t_span = (t_hi - t_lo) or 1
        r_span = (r_hi - r_lo) or 1

        # While the panel_params are flipped, the x and y parameters
        # have not be reoriented.
        x, y = self._flip(x, y)
        t_vals = np.asarray(x, dtype=float)
        r_vals = np.asarray(y, dtype=float)

        t_norm = (t_vals - t_lo) / t_span
        r_norm = (r_vals - r_lo) / r_span

        return dist_euclidean(t_norm, r_norm)

    def backtransform_range(self, panel_params: panel_view) -> panel_ranges:
        view = cast("radial_panel_view", panel_params)
        x, y = self._flip(view.theta.range, view.r.range)
        return panel_ranges(x=x, y=y)

    def setup_ax(
        self,
        ax: Axes,
        panel_params: panel_view,
        layout_info: layout_details,
    ) -> None:
        """
        Configure each polar axes from this panel's limits

        Sets limits, breaks, tick labels, the fixed active side, arc limits,
        inner radius, and radial-axis placement using `panel_params` so
        faceted panels with free scales each get their own radial range.

        The primary theta axis always renders on the outside. The primary r
        axis sits on the spoke where the data begins (`_r_axis_side`): the
        start spoke normally, the end spoke when `reverse="theta"` runs a
        partial arc the other way. Neither follows `scale.position`, which
        moves only the axis title. The fixed choice is recorded on
        `p9RadialAxes.axis_at_side` so theming can find it.
        """
        view = cast("radial_panel_view", panel_params)
        radial_ax = cast("p9RadialAxes", ax)

        # plotnine sweeps clockwise, which is matplotlib's -1.
        radial_ax.set_theta_direction(-1)

        if view.x.sec is not None:
            warn(
                f"{self.__class__.__name__}() does not support a secondary "
                "theta axis.",
                PlotnineWarning,
            )

        self._setup_ticks_labels(ax, view)

        # The radial axis is the yaxis; its start spoke is matplotlib's
        # "left" tick pair and its end spoke the "right" pair.
        r_side = "right" if self._r_axis_side == "r_end" else "left"
        _activate_axis(ax.xaxis, "top", True)
        _activate_axis(ax.yaxis, r_side, True)

        radial_ax.axis_at_side["theta_outside"] = radial_ax.thetaaxis
        radial_ax.axis_at_side[self._r_axis_side] = radial_ax.raxis

        if (sec := view.y.sec) is not None:
            sec_raxis = radial_ax.add_sec_raxis()
            _set_fixed_ticks(sec_raxis, sec.breaks, sec.labels)
            # The secondary axis occupies the spoke opposite the primary; that
            # spoke's tick pair is its "left"/"right" mpl side and its spine.
            sec_side = "right" if self._sec_r_axis_side == "r_end" else "left"
            _activate_axis(sec_raxis, sec_side, True)
            sec_spoke = "end" if sec_side == "right" else "start"
            radial_ax.set_spine_visible(sec_spoke, True)
            radial_ax.axis_at_side[self._sec_r_axis_side] = sec_raxis

        # The theme styles these tick objects later; keep matplotlib's
        # tick resets from replacing their styling with the default look.
        radial_ax.lock_raxis_tick_style()

        # Restrict visible theta range for partial arcs.
        if not self._is_full_circle:
            radial_ax.set_thetalim(*self._arc_range)

        # Inner radius: push the data away from the centre by setting a
        # virtual r-origin below r_min.  Formula: solve
        #   inner_radius = (r_lo - r_origin) / (r_hi - r_origin)
        # Use the ordered display range so the origin follows ordinary,
        # scale-reversed, and coordinate-reversed radial geometry.
        r_lo, r_hi = view.y.range

        if (
            self.inner_radius > 0
            and np.isfinite(r_lo)
            and np.isfinite(r_hi)
            and r_lo < r_hi
            and self.inner_radius < 1.0
        ):
            r_origin = (r_lo - self.inner_radius * r_hi) / (
                1.0 - self.inner_radius
            )
            radial_ax.set_rorigin(r_origin)

        # Full-circle r ticks and labels share the start spoke. Partial arcs
        # use matplotlib's distinct start/end radial axes.
        if self._is_full_circle:
            radial_ax.set_rlabel_position(np.degrees(self.start))

        ax.tick_params(axis="x", which="major", direction="out")
        if (angle := self._theta_guide_angle()) is not None:
            # Use Matplotlib's 'auto' mode so labels orient tangentially
            # to the arc, with `angle` as an offset — matching ggplot2's
            # guide_axis_theta() semantics where angle=0 means tangential.
            # ax.tick_params(labelrotation=...) always sets 'default' mode
            # (absolute degrees), so we patch each tick directly instead.
            for tick in ax.xaxis.get_major_ticks():
                tick._labelrotation = (  # pyright: ignore[reportAttributeAccessIssue]
                    "auto",
                    angle,
                )
        # Allow geom_text labels to extend past the polar axes bounding box
        # (e.g. spoke labels placed just beyond the outermost bar tip).
        for text in ax.texts:
            text.set_clip_on(False)

    def _theta_guide_angle(self) -> float | None:
        """
        Return the angle from guides(theta=guide_axis_theta(...))
        """
        if self._owner is None:
            return None
        guide = cast("Any", self._owner.guides.theta)
        return getattr(guide, "angle", None)

    def aspect(self, panel_params: panel_view) -> float:
        left, right, bottom, top = polar_bbox(
            self._arc_range, self.inner_radius
        )
        return (top - bottom) / (right - left)


@alias
class coord_polar(coord_radial):
    pass
