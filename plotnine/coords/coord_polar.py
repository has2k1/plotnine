from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np

from ..iapi import panel_ranges
from .coord import coord, dist_euclidean

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes
    from plotnine.iapi import panel_view
    from plotnine.scales.scale import scale


class coord_polar(coord):
    """
    Polar coordinate system.

    Uses Matplotlib's native ``PolarAxes`` so every standard geom
    (including bar → pie/bullseye) renders correctly without manual
    Cartesian conversion.  Concentric-circle and radial-spoke grid
    lines are drawn automatically by Matplotlib.

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
        Add a small buffer around the data on the radius axis. Default ``True``.
    """

    is_linear = False

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
        self.params: dict = {}

    # ------------------------------------------------------------------
    # Panel params
    # ------------------------------------------------------------------

    def setup_panel_params(
        self, scale_x: scale, scale_y: scale
    ) -> panel_view:
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

        self.params["theta_range"] = theta_range
        self.params["r_range"] = r_sv.range

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

        # y → r axis: use the scale for the r dimension with its natural breaks.
        new_y = replace(r_sv)

        return replace(pv_exp, x=new_x, y=new_y)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_radians(self, vals: np.ndarray) -> np.ndarray:
        """Normalise data-space theta values to [start, start + 2π]."""
        t_min, t_max = self.params["theta_range"]
        denom = float(t_max) - float(t_min)
        if denom == 0:
            return np.zeros_like(vals, dtype=float)
        norm = (np.asarray(vals, dtype=float) - float(t_min)) / denom
        return self.start + self.direction * norm * 2.0 * np.pi

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
        else:
            theta_col, r_col = "y", "x"

        if theta_col not in data.columns or r_col not in data.columns:
            return data

        data = data.copy()
        data[theta_col] = self._to_radians(data[theta_col].to_numpy())

        # PolarAxes always expects x = theta (radians) and y = r.
        # When theta = "y" we need to swap the columns.
        if self.theta == "y":
            data["x"], data["y"] = data["y"].copy(), data["x"].copy()

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
        t_min, t_max = self.params["theta_range"]
        r_min, r_max = self.params["r_range"]
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
        t_range = tuple(self.params["theta_range"])
        r_range = tuple(self.params["r_range"])
        if self.theta == "x":
            return panel_ranges(x=t_range, y=r_range)  # type: ignore[arg-type]
        return panel_ranges(x=r_range, y=t_range)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Draw decorations on PolarAxes
    # ------------------------------------------------------------------

    def draw(self, axs: list[Axes]) -> None:
        """Configure each PolarAxes: zero location, direction, r limits."""
        r_min, r_max = self.params.get("r_range", (0.0, 1.0))

        # Matplotlib PolarAxes theta_direction: -1 = clockwise, 1 = counter-CW.
        mpl_direction = -1 if self.direction == 1 else 1

        for ax in axs:
            ax.set_theta_zero_location("N")   # 12 o'clock = 0
            ax.set_theta_direction(mpl_direction)
            if np.isfinite(r_min) and np.isfinite(r_max) and r_min != r_max:
                ax.set_rlim(float(r_min), float(r_max))

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def aspect(self, panel_params: panel_view) -> float:
        return 1.0
