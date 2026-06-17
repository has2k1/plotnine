from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, cast

import numpy as np

from .coord_polar import coord_polar

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.projections.polar import PolarAxes

    from plotnine import theme
    from plotnine.iapi import panel_view
    from plotnine.scales.scale import scale


class coord_radial(coord_polar):
    """
    Radial coordinate system

    `coord_radial` maps one position aesthetic to the angle and the other
    to the radius. Compared with ``coord_polar``, it adds support for
    partial arcs, inner radius holes, theta/radius limits, radial-axis
    placement, and rotation of the ``angle`` aesthetic.

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
        ``1`` = clockwise (default), ``-1`` = counter-clockwise.
        Only used when *end* is ``None``.
    expand :
        Add a small buffer around the data on the radius axis.
        Default ``True``.
    inner_radius :
        Size of the inner hole as a fraction of the outer radius, in
        ``[0, 1)``.  ``0`` (default) means no hole; ``0.3`` creates a 30 %
        donut hole, useful for gauge and donut charts.
    r_axis_inside :
        Where to place the radial (r) axis tick labels.

        * ``None`` (default) — let Matplotlib decide (usually outside).
        * ``True`` — force inside, aligned just past the *start* angle.
        * ``False`` — force outside (Matplotlib default).
        * *float* — place at this theta angle in radians (clockwise from
          North).

        Unlike ggplot2's ``r.axis.inside``, a length-2 value for separate
        primary and secondary axis placement is not supported.
    rotate_angle :
        If ``True``, automatically add the local theta angle (in degrees) to
        the ``angle`` aesthetic so that text or other rotated marks align with
        the spoke direction.  Default ``False``.
    thetalim :
        Data-space limits for the theta axis as ``(lo, hi)``.  Only data
        within this range is mapped to the arc; equivalent to zooming on the
        angular axis.  ``None`` (default) uses the full data range.
    rlim :
        Data-space limits for the r axis as ``(lo, hi)``.  Only data within
        this range is shown; equivalent to zooming on the radial axis.
        ``None`` (default) uses the full data range.

    Notes
    -----
    Theta-axis tick labels are shown by default, matching ggplot2. Since a
    polar axes' x-axis *is* the theta axis, they are styled through the
    theme: hide them with ``theme(axis_text_x=element_blank())`` and adjust
    the gap to the outer circle through the ``axis_text_x`` margin.

    The Python API uses snake_case names for arguments that are dotted in
    ggplot2: ``inner_radius``, ``r_axis_inside``, and ``rotate_angle``.

    Unlike ggplot2, plotnine coordinate systems do not currently expose a
    ``clip`` argument. The ggplot2 ``reverse`` argument is not currently
    implemented.

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

    def __init__(
        self,
        theta: str = "x",
        start: float = 0,
        end: float | None = None,
        direction: int = 1,
        expand: bool = True,
        inner_radius: float = 0,
        r_axis_inside: bool | float | None = None,
        rotate_angle: bool = False,
        thetalim: tuple[float, float] | None = None,
        rlim: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(
            theta=theta,
            start=start,
            direction=direction,
            expand=expand,
        )
        self.end = end
        self.inner_radius = inner_radius
        self.r_axis_inside = r_axis_inside
        self.rotate_angle = rotate_angle
        self.thetalim = thetalim
        self.rlim = rlim

    # ------------------------------------------------------------------
    # Panel params
    # ------------------------------------------------------------------

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        from .coord_cartesian import coord_cartesian

        # Capture data-space theta breaks before super() clears them.
        pv_data = coord_cartesian(expand=False).setup_panel_params(
            scale_x, scale_y
        )
        if self.theta == "x":
            theta_breaks = list(pv_data.x.breaks)
            theta_labels = list(pv_data.x.labels)
        else:
            theta_breaks = list(pv_data.y.breaks)
            theta_labels = list(pv_data.y.labels)

        pv = super().setup_panel_params(scale_x, scale_y)

        # thetalim: zoom the theta data range — only this slice maps to the
        # arc. Recompute nice breaks over the zoomed range so labels are not
        # reduced to sparse endpoints, matching ggplot2.
        if self.thetalim is not None:
            self.params["theta_range"] = tuple(self.thetalim)
            theta_scale = scale_x if self.theta == "x" else scale_y
            theta_breaks = [
                b
                for b in theta_scale.get_bounded_breaks(self.thetalim)
                if np.isfinite(b)
            ]
            theta_labels = list(theta_scale.get_labels(theta_breaks))

        # rlim: zoom the r data range — update params and recompute nice breaks
        # over the zoomed range (rather than filtering the full-range breaks,
        # which leaves sparse endpoint-only labels), matching ggplot2.
        if self.rlim is not None:
            self.params["r_range"] = tuple(self.rlim)
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
        # as theta axis tick labels on the outer edge.  Theta labels show by
        # default (matching ggplot2); hide them via theme(axis_text_x=...).
        x_updates: dict = {}
        if theta_breaks:
            radian_pos = list(
                self._to_radians(np.asarray(theta_breaks, dtype=float))
            )
            if arc_lo is not None:
                keep = [arc_lo <= r <= arc_hi for r in radian_pos]
                radian_pos = [r for r, k in zip(radian_pos, keep) if k]
                theta_labels = [l for l, k in zip(theta_labels, keep) if k]
            x_updates["breaks"] = radian_pos
            x_updates["labels"] = theta_labels

        # Partial arc: x panel range must match [arc_lo, arc_hi] so that
        # coord.setup_ax calls ax.set_xlim(arc_lo, arc_hi) rather than
        # ax.set_xlim(0, 2π), which would override set_thetalim.
        if arc_lo is not None:
            x_updates["limits"] = (arc_lo, arc_hi)
            x_updates["range"] = (arc_lo, arc_hi)

        if x_updates:
            pv = replace(pv, x=replace(pv.x, **x_updates))

        return pv

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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

    def _to_radians(self, vals: np.ndarray) -> np.ndarray:
        """Normalize theta values to [start, start + arc]."""
        t_min, t_max = self.params["theta_range"]
        denom = float(t_max) - float(t_min)
        if denom == 0:
            return np.zeros_like(vals, dtype=float)
        norm = (np.asarray(vals, dtype=float) - float(t_min)) / denom
        return self.start + norm * self._arc

    # ------------------------------------------------------------------
    # Data transformation
    # ------------------------------------------------------------------

    def transform(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        munch: bool = False,
    ) -> pd.DataFrame:
        data = super().transform(data, panel_params, munch=munch)
        # After super().transform(), data["x"] is always theta in radians.
        if (
            self.rotate_angle
            and "angle" in data.columns
            and "x" in data.columns
        ):
            data = data.copy()
            data["angle"] = data["angle"] + np.degrees(data["x"])
        return data

    # ------------------------------------------------------------------
    # Draw decorations on PolarAxes
    # ------------------------------------------------------------------

    def setup_ax(
        self, ax: Axes, panel_params: panel_view, theme: theme
    ) -> None:
        """
        Configure each PolarAxes from this panel's limits

        Sets the arc limits, inner radius, and radial-axis placement using
        ``panel_params`` so faceted panels with free scales each get their
        own radial range.
        """
        super().setup_ax(ax, panel_params, theme)
        polar_ax = cast("PolarAxes", ax)
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
        r_min, r_max = panel_params.y.range
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

        # Radial axis label placement.
        if self.r_axis_inside is None:
            # Left spoke, matching ggplot2's default.
            polar_ax.set_rlabel_position(270)
        elif isinstance(self.r_axis_inside, bool):
            if self.r_axis_inside:
                # Just inside the start angle keeps it out of the data.
                polar_ax.set_rlabel_position(np.degrees(self.start) + 10)
            else:
                polar_ax.set_rlabel_position(270)
        else:
            polar_ax.set_rlabel_position(np.degrees(float(self.r_axis_inside)))

        ax.tick_params(axis="x", which="major", direction="out")
        if (angle := self._theta_guide_angle(theme)) is not None:
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

    @staticmethod
    def _theta_guide_angle(theme: theme) -> float | None:
        """
        Return the angle from guides(theta=guide_axis_theta(...)).
        """
        guide = getattr(getattr(theme, "owner", None), "guides", None)
        guide = getattr(guide, "theta", None)
        return getattr(guide, "angle", None)
