from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Literal, cast
from warnings import warn

import numpy as np

from .._mpl._polar_axes import p9PolarAxes  # noqa: TCH001
from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from ..iapi import panel_ranges
from .coord import _activate_axis, coord, dist_euclidean

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.projections.polar import PolarAxes

    from plotnine.iapi import labels_view, layout_details, panel_view
    from plotnine.scales.scale import scale


class coord_radial(coord):
    """
    Radial coordinate system

    `coord_radial` maps one position aesthetic to the angle and the other
    to the radius. It supports full and partial arcs, inner radius holes,
    theta/radius limits, radial-axis placement, and rotation of the
    ``angle`` aesthetic. It supersedes `coord_polar`.

    Parameters
    ----------
    theta :
        Which variable maps to the angle axis, ``"x"`` (default) or ``"y"``.
    start :
        Starting angle in radians, measured clockwise from 12 o'clock.
        Default 0.
    end :
        Ending angle in radians, measured clockwise from 12 o'clock.
        ``None`` (default) gives a full circle (``start + 2π * direction``).
    direction :
        Angular rotation sense: ``1`` = clockwise (default), ``-1`` =
        counter-clockwise. Applied regardless of *end*, so it also sets
        the sweep direction of a partial arc.
    expand :
        Add a small buffer around the data on the radius axis.
        Default ``True``.
    inner_radius :
        Size of the inner hole as a fraction of the outer radius, in
        ``[0, 1)``.  ``0`` (default) means no hole; ``0.3`` creates a 30 %
        donut hole, useful for gauge and donut charts.
    rotate_angle :
        If ``True``, rotate the ``angle`` aesthetic so that text or other
        rotated marks align tangentially with the arc at their spoke. The
        rotation is folded so labels stay upright (readable) rather than
        appearing upside-down in the lower half.  Default ``False``.
    thetalim :
        Data-space limits for the theta axis as ``(lo, hi)``.  Only data
        within this range is mapped to the arc; equivalent to zooming on the
        angular axis.  ``None`` (default) uses the full data range.
    rlim :
        Data-space limits for the r axis as ``(lo, hi)``.  Only data within
        this range is shown; equivalent to zooming on the radial axis.
        ``None`` (default) uses the full data range.
    reverse :
        Which axes run in the opposite direction.

        * ``"none"`` (default) — neither axis is reversed.
        * ``"theta"`` — the angular axis runs the other way around.
        * ``"r"`` — the radial axis is inverted, so large values sit
          toward the centre.
        * ``"thetar"`` — both the angular and radial axes are reversed.

    Notes
    -----
    Theta-axis tick labels are shown by default. Since a polar axes' x-axis
    *is* the theta axis, they are styled through the theme: hide them with
    ``theme(axis_text_x=element_blank())`` and adjust the gap to the outer
    circle through the ``axis_text_x`` margin.

    Unlike ggplot2, plotnine coordinate systems do not currently expose a
    ``clip`` argument.

    Examples
    --------
    A donut chart is a stacked bar chart with an inner radius.

    ```python
    import pandas as pd
    from plotnine import aes, coord_radial, geom_col, ggplot

    df = pd.DataFrame({
        "x": [1, 1, 1],
        "y": [2, 3, 5],
        "group": ["a", "b", "c"],
    })

    (
        ggplot(df, aes("x", "y", fill="group"))
        + geom_col()
        + coord_radial(theta="y", inner_radius=0.4)
    )
    ```

    Partial arcs can be used for gauge-like displays.

    ```python
    import numpy as np
    import pandas as pd
    from plotnine import aes, coord_radial, geom_point, ggplot

    df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 3]})

    ggplot(df, aes("x", "y")) + geom_point() + coord_radial(
        start=-0.4 * np.pi,
        end=0.4 * np.pi,
        inner_radius=0.3,
    )
    ```
    """

    is_linear = False
    _projection = "p9polar"

    def __init__(
        self,
        theta: str = "x",
        start: float = 0,
        end: float | None = None,
        direction: int = 1,
        expand: bool = True,
        inner_radius: float = 0,
        rotate_angle: bool = False,
        thetalim: tuple[float, float] | None = None,
        rlim: tuple[float, float] | None = None,
        reverse: str = "none",
    ) -> None:
        if reverse not in {"none", "theta", "r", "thetar"}:
            raise ValueError(
                "reverse must be one of 'none', 'theta', 'r', 'thetar'; "
                f"got {reverse!r}."
            )
        self.theta = theta
        self.start = start
        self.end = end
        self.direction = direction
        self.expand = expand
        self.inner_radius = inner_radius
        self.rotate_angle = rotate_angle
        self.thetalim = thetalim
        self.rlim = rlim
        self.reverse = reverse

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        from ..scales.scale_continuous import scale_continuous
        from .coord_cartesian import coord_cartesian

        # One expanded cartesian view supplies both the theta/r ranges and
        # the theta breaks. Theta follows the expand flag like every other
        # axis: expand=True buffers the data off the arc ends; expand=False
        # keeps it flush so a pie closes cleanly.
        pv_exp = coord_cartesian(expand=self.expand).setup_panel_params(
            scale_x, scale_y
        )

        if self.theta == "x":
            theta_range, r_sv = pv_exp.x.range, pv_exp.y
            theta_breaks = list(pv_exp.x.breaks)
            theta_labels = list(pv_exp.x.labels)
            theta_minor_breaks = list(pv_exp.x.minor_breaks)
        else:
            theta_range, r_sv = pv_exp.y.range, pv_exp.x
            theta_breaks = list(pv_exp.y.breaks)
            theta_labels = list(pv_exp.y.labels)
            theta_minor_breaks = list(pv_exp.y.minor_breaks)

        r_range = r_sv.range
        empty = np.array([], dtype=float)

        # theta axis: [start, start+2π] display span so bars rotated by a
        # non-zero start stay within range. Data ticks (original units) are
        # converted to radian positions and applied at the end of this method.
        theta_start = float(self.start)
        new_x = replace(
            pv_exp.x,
            limits=(theta_start, theta_start + 2 * np.pi),
            range=(theta_start, theta_start + 2 * np.pi),
            breaks=[],
            minor_breaks=empty,
            labels=[],
        )
        new_y = replace(r_sv)

        pv = replace(
            pv_exp,
            x=new_x,
            y=new_y,
            theta_range=tuple(theta_range),
            r_range=tuple(r_range),
        )

        # thetalim: zoom the theta data range — only this slice maps to the
        # arc. Expand on top of the zoom (like coord_cartesian expands on top
        # of xlim) and recompute nice breaks over the expanded range so labels
        # are not reduced to sparse endpoints.
        if self.thetalim is not None:
            from mizani.transforms import identity_trans

            theta_scale = scale_x if self.theta == "x" else scale_y
            coord_limits = (
                theta_scale.transform(self.thetalim)
                if isinstance(theta_scale, scale_continuous)
                else self.thetalim
            )
            expansion = theta_scale.default_expansion(expand=self.expand)
            theta_zoom = theta_scale.expand_limits(
                theta_scale.final_limits,
                expansion,
                coord_limits,
                identity_trans(),
            ).range
            pv = replace(pv, theta_range=tuple(theta_zoom))
            theta_breaks = [
                b
                for b in theta_scale.get_bounded_breaks(theta_zoom)
                if np.isfinite(b)
            ]
            theta_labels = list(theta_scale.get_labels(theta_breaks))
            # Only a continuous theta scale has minor breaks; a discrete one
            # has none, so leave theta_minor_breaks empty.
            if isinstance(theta_scale, scale_continuous):
                theta_minor_breaks = [
                    b
                    for b in theta_scale.get_minor_breaks(
                        theta_breaks, theta_zoom
                    )
                    if np.isfinite(b)
                ]
            else:
                theta_minor_breaks = []

        # rlim: zoom the r data range — update ranges and recompute nice breaks
        # over the zoomed range (rather than filtering the full-range breaks,
        # which leaves sparse endpoint-only labels).
        if self.rlim is not None:
            pv = replace(pv, r_range=tuple(self.rlim))
            r_scale = scale_y if self.theta == "x" else scale_x
            breaks = [
                b
                for b in r_scale.get_bounded_breaks(self.rlim)
                if np.isfinite(b)
            ]
            labels = r_scale.get_labels(breaks)
            new_y = replace(
                pv.y,
                limits=tuple(self.rlim),
                range=tuple(self.rlim),
                breaks=breaks,
                labels=labels,
            )
            pv = replace(pv, y=new_y)

        # Compute arc bounds for partial-arc plots (None means full circle).
        arc_lo = arc_hi = None
        if self.end is not None:
            arc = self._arc
            arc_lo = min(self.start, self.start + arc)
            arc_hi = max(self.start, self.start + arc)

        # Convert data-space theta breaks to radian positions and restore them
        # as theta axis tick labels on the outer edge.
        x_updates: dict = {}
        if theta_breaks:
            assert pv.theta_range is not None
            radian_pos = list(
                self._to_radians(
                    np.asarray(theta_breaks, dtype=float), pv.theta_range
                )
            )
            if arc_lo is not None:
                keep = [arc_lo <= r <= arc_hi for r in radian_pos]
                radian_pos = [r for r, k in zip(radian_pos, keep) if k]
                theta_labels = [l for l, k in zip(theta_labels, keep) if k]
            x_updates["breaks"] = radian_pos
            x_updates["labels"] = theta_labels

        if theta_minor_breaks:
            assert pv.theta_range is not None
            minor_radian_pos = list(
                self._to_radians(
                    np.asarray(theta_minor_breaks, dtype=float),
                    pv.theta_range,
                )
            )
            if arc_lo is not None:
                minor_radian_pos = [
                    r for r in minor_radian_pos if arc_lo <= r <= arc_hi
                ]
            x_updates["minor_breaks"] = minor_radian_pos

        # Partial arc: x panel range must match [arc_lo, arc_hi] so that
        # coord.setup_ax calls ax.set_xlim(arc_lo, arc_hi) rather than
        # ax.set_xlim(0, 2π), which would override set_thetalim.
        if arc_lo is not None:
            x_updates["limits"] = (arc_lo, arc_hi)
            x_updates["range"] = (arc_lo, arc_hi)

        if x_updates:
            pv = replace(pv, x=replace(pv.x, **x_updates))

        # reverse="r"/"thetar": flip the displayed radial range so large r
        # values sit toward the centre. set_ylim(hi, lo) inverts the axis.
        # pv.r_range stays in natural (lo, hi) order, so setup_ax reads it
        # (not y.range) for the inner_radius origin: reversing only y.range
        # inverts the display without breaking the hole, and distance() is
        # likewise unaffected.
        if self.reverse in ("r", "thetar"):
            lo, hi = pv.y.range
            pv = replace(pv, y=replace(pv.y, range=(hi, lo)))

        return pv

    def labels(self, cur_labels: labels_view) -> labels_view:
        # When theta="y" the data x/y columns are swapped in transform so that
        # PolarAxes sees x=theta, y=r. Swap the axis titles to match, the same
        # way coord_flip does for its flipped axes.
        if self.theta == "y":
            from .coord_flip import flip_labels

            return flip_labels(super().labels(cur_labels))
        return super().labels(cur_labels)

    @property
    def _arc(self) -> float:
        """
        Total angular span of the plotted region, in radians

        For a partial radial plot this is the distance between ``start`` and
        ``end``; otherwise it is a full turn. The sense of rotation
        (clockwise vs counter-clockwise) is a PolarAxes property applied at
        draw time and is not encoded in this magnitude.
        """
        if self.end is not None:
            return self.end - self.start
        return 2.0 * np.pi

    def _mpl_theta_direction(self) -> Literal[-1, 1]:
        """
        Matplotlib theta direction for this coordinate system

        ``-1`` draws clockwise and ``+1`` counter-clockwise, the opposite of
        plotnine's own ``direction`` convention. ``reverse="theta"``/
        ``"thetar"`` runs the angular axis the other way by folding into the
        PolarAxes direction here, rather than into the radian mapping.
        """
        mpl_direction: Literal[-1, 1] = -1 if self.direction == 1 else 1
        if self.reverse in ("theta", "thetar"):
            return 1 if mpl_direction == -1 else -1
        return mpl_direction

    def _to_radians(
        self, vals: np.ndarray, theta_range: tuple[float, float]
    ) -> np.ndarray:
        """Normalize theta values to [start, start + arc]"""
        t_min, t_max = theta_range
        denom = float(t_max) - float(t_min)
        if denom == 0:
            return np.zeros_like(vals, dtype=float)
        norm = (np.asarray(vals, dtype=float) - float(t_min)) / denom
        # Rotation direction is a PolarAxes property set in draw via
        # set_theta_direction; it is not baked into these radian values.
        return self.start + norm * self._arc

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

        if self.theta == "x":
            theta_col, r_col = "x", "y"
            theta_end_col, r_end_col = "xend", "yend"
        else:
            theta_col, r_col = "y", "x"
            theta_end_col, r_end_col = "yend", "xend"

        if theta_col not in data.columns or r_col not in data.columns:
            return data

        theta_range = panel_params.theta_range
        assert theta_range is not None

        data = data.copy()
        data[theta_col] = self._to_radians(
            data[theta_col].to_numpy(), theta_range
        )
        has_endpoints = (
            theta_end_col in data.columns and r_end_col in data.columns
        )
        if has_endpoints:
            data[theta_end_col] = self._to_radians(
                data[theta_end_col].to_numpy(), theta_range
            )

        # PolarAxes always expects x = theta (radians) and y = r.
        # When theta = "y" we need to swap the columns.
        if self.theta == "y":
            data["x"], data["y"] = data["y"].copy(), data["x"].copy()
            if has_endpoints:
                data["xend"], data["yend"] = (
                    data["yend"].copy(),
                    data["xend"].copy(),
                )

        # After the swap, data["x"] is always theta in radians.
        if (
            self.rotate_angle
            and "angle" in data.columns
            and "x" in data.columns
        ):
            # Align marks tangentially to their spoke. The PolarAxes places
            # a data theta t at on-screen angle (deg, CCW from East)
            #   screen = 90 + mpl_dir * degrees(t),  mpl_dir = -1 if cw else 1
            # Tangential text rotation is screen - 90; folding into (-90, 90]
            # keeps labels upright (a bottom label reads "6", not "9").
            mpl_dir = self._mpl_theta_direction()
            rot = mpl_dir * np.degrees(data["x"].to_numpy())
            rot = (rot + 90.0) % 180.0 - 90.0
            data["angle"] = data["angle"] + rot

        return data

    def distance(
        self,
        x: pd.Series,
        y: pd.Series,
        panel_params: panel_view,
    ) -> np.ndarray:
        # Normalise theta and r to [0, 1] then compute Euclidean distance.
        assert panel_params.theta_range is not None
        assert panel_params.r_range is not None
        t_min, t_max = panel_params.theta_range
        r_min, r_max = panel_params.r_range
        t_denom = float(t_max - t_min) or 1.0
        r_denom = float(r_max - r_min) or 1.0

        if self.theta == "x":
            theta_vals = np.asarray(x, dtype=float)
            r_vals = np.asarray(y, dtype=float)
        else:
            theta_vals = np.asarray(y, dtype=float)
            r_vals = np.asarray(x, dtype=float)

        theta_norm = (theta_vals - float(t_min)) / t_denom
        r_norm = (r_vals - float(r_min)) / r_denom
        return dist_euclidean(theta_norm, r_norm)

    def backtransform_range(self, panel_params: panel_view) -> panel_ranges:
        assert panel_params.theta_range is not None
        assert panel_params.r_range is not None
        t_range = panel_params.theta_range
        r_range = panel_params.r_range
        if self.theta == "x":
            return panel_ranges(x=t_range, y=r_range)
        return panel_ranges(x=r_range, y=t_range)

    def setup_ax(
        self,
        ax: Axes,
        panel_params: panel_view,
        layout_info: layout_details,
    ) -> None:
        """
        Configure each PolarAxes from this panel's limits

        Sets limits, breaks, tick labels, the fixed active side, arc limits,
        inner radius, and radial-axis placement using ``panel_params`` so
        faceted panels with free scales each get their own radial range.

        The primary theta axis always renders on the outside and the primary
        r axis always on r_start, independent of `scale.position` (which moves
        only the axis title). The fixed choice is recorded on
        `p9PolarAxes.axis_at_side` so theming can find it.
        """
        if panel_params.x.sec is not None:
            warn(
                f"{self.__class__.__name__}() does not support a secondary "
                "theta axis.",
                PlotnineWarning,
            )

        self._setup_ticks_labels(ax, panel_params)
        polar_ax = cast("p9PolarAxes", ax)

        _activate_axis(ax.xaxis, "top", True)
        _activate_axis(ax.yaxis, "left", True)

        polar_ax.axis_at_side["theta_outside"] = polar_ax.thetaaxis
        polar_ax.axis_at_side["r_start"] = polar_ax.raxis

        # The theme styles these tick objects later; keep matplotlib's
        # tick resets from replacing their styling with the default look.
        polar_ax.lock_raxis_tick_style()

        arc = self._arc

        # Restrict visible theta range for partial arcs.
        if self.end is not None:
            polar_ax.set_thetalim(
                min(self.start, self.start + arc),
                max(self.start, self.start + arc),
            )

        # Inner radius: push the data away from the centre by setting a
        # virtual r-origin below r_min.  Formula: solve
        #   inner_radius = (r_min - r_origin) / (r_max - r_origin)
        # Use the natural r range (always (lo, hi), reflects rlim) rather
        # than y.range, which reverse="r"/"thetar" inverts to (hi, lo) and
        # would fail the r_max > r_min guard, dropping the donut hole.
        assert panel_params.r_range is not None
        r_min, r_max = panel_params.r_range
        if (
            self.inner_radius > 0
            and np.isfinite(r_min)
            and np.isfinite(r_max)
            and r_max > r_min
            and self.inner_radius < 1.0
        ):
            r_origin = (r_min - self.inner_radius * r_max) / (
                1.0 - self.inner_radius
            )
            polar_ax.set_rorigin(r_origin)

        # Radial axis label placement. RadialTick.update_position (mpl)
        # reads rlabel_position only for a full circle; a partial arc
        # ignores it and always uses thetamin/thetamax directly, so this
        # only matters here.
        if self.end is None:
            polar_ax.set_rlabel_position(270)

        ax.tick_params(axis="x", which="major", direction="out")
        if (angle := self._theta_guide_angle()) is not None:
            # Use Matplotlib's 'auto' mode so labels orient tangentially
            # to the arc, with `angle` as an offset — matching ggplot2's
            # guide_axis_theta() semantics where angle=0 means tangential.
            # ax.tick_params(labelrotation=...) always sets 'default' mode
            # (absolute degrees), so we patch each tick directly instead.
            for tick in ax.xaxis.get_major_ticks():
                tick._labelrotation = ("auto", angle)
        # Allow geom_text labels to extend past the polar axes bounding box
        # (e.g. spoke labels placed just beyond the outermost bar tip).
        for text in ax.texts:
            text.set_clip_on(False)

    def _theta_guide_angle(self) -> float | None:
        """
        Return the angle from guides(theta=guide_axis_theta(...))
        """
        try:
            return self._owner.guides.theta.angle
        except AttributeError:
            return None

    def draw(self, axs: list[Axes]) -> None:
        """Configure each PolarAxes: zero location and rotation direction

        R-limits are set per panel by setup_ax.
        """
        # PolarAxes theta_direction: -1 = clockwise, +1 = counter-clockwise.
        mpl_direction = self._mpl_theta_direction()
        for ax in axs:
            polar_ax = cast("PolarAxes", ax)
            polar_ax.set_theta_zero_location("N")  # 12 o'clock
            polar_ax.set_theta_direction(mpl_direction)

    def aspect(self, panel_params: panel_view) -> float:
        return 1.0


@alias
class coord_polar(coord_radial):
    pass
