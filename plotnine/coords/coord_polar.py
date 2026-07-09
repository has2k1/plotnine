from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Literal, cast
from warnings import warn

import numpy as np

from .._mpl._polar_axes import p9PolarAxes  # noqa: TCH001
from ..exceptions import PlotnineWarning
from ..iapi import panel_ranges
from .coord import _activate_axis, coord, dist_euclidean

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.projections.polar import PolarAxes

    from plotnine.iapi import labels_view, layout_details, panel_view
    from plotnine.scales.scale import scale
    from plotnine.typing import PolarSide, Side


def _resolve_theta_side(position: Side) -> PolarSide:
    """
    Return which theta side a scale's x position resolves to

    `"bottom"` (the default `scale_x_*` position) is the outer rim,
    matching today's only visible placement; `"top"` moves theta to the
    inner (donut-hole) side.
    """
    return "theta_outside" if position == "bottom" else "theta_inside"


def _resolve_r_side(position: Side) -> PolarSide:
    """
    Return which r side a scale's y position resolves to

    `"left"` (the default `scale_y_*` position) is the start-angle
    spoke, matching the existing 270-degree default placement on a full
    circle; `"right"` moves r to the end-angle spoke.
    """
    return "r_start" if position == "left" else "r_end"


class coord_polar(coord):
    """
    Polar coordinate system

    `coord_polar` maps one position aesthetic to the angle and the other
    to the radius. It is commonly used for pie charts, which are stacked
    bar charts in polar coordinates.

    Parameters
    ----------
    theta :
        Which variable maps to the angle axis, ``"x"`` (default) or ``"y"``.
    start :
        Starting angle in radians, measured clockwise from 12 o'clock
        (i.e. from the positive-y axis). Default 0.
    direction :
        ``1`` = clockwise (default), ``-1`` = counter-clockwise.
    expand :
        Add a small buffer around the data on the radius axis.
        Default ``True``.

    Notes
    -----
    Unlike ggplot2, plotnine coordinate systems do not currently expose a
    ``clip`` argument.

    For partial arcs, donut charts, and theta/radius limits, use
    ``coord_radial``.

    Examples
    --------
    A pie chart is a stacked bar chart with the y position mapped to angle.

    ```python
    import pandas as pd
    from plotnine import aes, coord_polar, geom_col, ggplot

    df = pd.DataFrame({
        "x": [1, 1, 1],
        "y": [2, 3, 5],
        "group": ["a", "b", "c"],
    })

    ggplot(df, aes("x", "y", fill="group")) + geom_col() + coord_polar("y")
    ```
    """

    is_linear = False
    _projection = "p9polar"

    def __init__(
        self,
        theta: str = "x",
        start: float = 0,
        direction: int = 1,
        expand: bool = True,
    ) -> None:
        self.theta = theta
        self.start = start
        self.direction = direction
        self.expand = expand

    # ------------------------------------------------------------------
    # Panel params
    # ------------------------------------------------------------------

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        from .coord_cartesian import coord_cartesian

        # Theta fills exactly one full revolution — no expansion on that axis.
        # R uses the caller-controlled expand flag.
        pv_no_exp = coord_cartesian(expand=False).setup_panel_params(
            scale_x, scale_y
        )
        pv_exp = coord_cartesian(expand=self.expand).setup_panel_params(
            scale_x, scale_y
        )

        if self.theta == "x":
            theta_range = pv_no_exp.x.range
            r_sv = pv_exp.y
        else:
            theta_range = pv_no_exp.y.range
            r_sv = pv_exp.x

        r_range = r_sv.range

        empty = np.array([], dtype=float)

        # x → theta axis: data ticks are in original units (not radians), so
        # suppress them.  Limits span [start, start+2π] so that bars rotated
        # by a non-zero start angle stay within the displayed theta range.
        theta_start = float(self.start)
        new_x = replace(
            pv_exp.x,
            limits=(theta_start, theta_start + 2 * np.pi),
            range=(theta_start, theta_start + 2 * np.pi),
            breaks=[],
            minor_breaks=empty,
            labels=[],
        )

        # y → r axis: use the scale for the r dimension with its natural
        # breaks.
        new_y = replace(r_sv)

        return replace(
            pv_exp,
            x=new_x,
            y=new_y,
            theta_range=tuple(theta_range),
            r_range=tuple(r_range),
        )

    def labels(self, cur_labels: labels_view) -> labels_view:
        # When theta="y" the data x/y columns are swapped in transform so that
        # PolarAxes sees x=theta, y=r. Swap the axis titles to match, the same
        # way coord_flip does for its flipped axes.
        if self.theta == "y":
            from .coord_flip import flip_labels

            return flip_labels(super().labels(cur_labels))
        return super().labels(cur_labels)

    def setup_ax(
        self,
        ax: Axes,
        panel_params: panel_view,
        layout_info: layout_details,
    ) -> None:
        """
        Limits, breaks, tick labels, and active side for a polar panel

        Activates exactly one theta side (from `panel_params.x.position`)
        and one r side (from `panel_params.y.position`). It records the
        choice on `p9PolarAxes.axis_at_side` so theming can find it.
        """
        if panel_params.x.sec is not None:
            warn(
                f"{self.__class__.__name__}() does not support a secondary "
                "theta axis.",
                PlotnineWarning,
            )

        self._setup_ticks_labels(ax, panel_params)
        polar_ax = cast("p9PolarAxes", ax)
        theta_side = _resolve_theta_side(panel_params.x.position)
        r_side = _resolve_r_side(panel_params.y.position)

        _activate_axis(
            ax.xaxis,
            "top" if theta_side == "theta_outside" else "bottom",
            True,
        )
        _activate_axis(
            ax.yaxis, "left" if r_side == "r_start" else "right", True
        )

        polar_ax.axis_at_side[theta_side] = polar_ax.thetaaxis
        polar_ax.axis_at_side[r_side] = polar_ax.raxis

        # The theme styles these tick objects later; keep matplotlib's
        # tick resets from replacing their styling with the default look.
        polar_ax.lock_raxis_tick_style()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_radians(
        self, vals: np.ndarray, theta_range: tuple[float, float]
    ) -> np.ndarray:
        """Normalise data-space theta values to [start, start + 2π]."""
        t_min, t_max = theta_range
        denom = float(t_max) - float(t_min)
        if denom == 0:
            return np.zeros_like(vals, dtype=float)
        norm = (np.asarray(vals, dtype=float) - float(t_min)) / denom
        # Rotation direction is a PolarAxes property set in draw via
        # set_theta_direction; it is not baked into these radian values.
        return self.start + norm * 2.0 * np.pi

    # ------------------------------------------------------------------
    # Data transformation
    # ------------------------------------------------------------------

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

        return data

    # ------------------------------------------------------------------
    # Distance (used by munch, called before transform)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Draw decorations on PolarAxes
    # ------------------------------------------------------------------

    def _mpl_theta_direction(self) -> Literal[-1, 1]:
        """
        Matplotlib theta direction for this coordinate system

        ``-1`` draws clockwise and ``+1`` counter-clockwise, the opposite of
        plotnine's own ``direction`` convention.
        """
        return -1 if self.direction == 1 else 1

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

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def aspect(self, panel_params: panel_view) -> float:
        return 1.0
