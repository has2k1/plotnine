from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np

from .coord import coord, dist_euclidean

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes
    from plotnine.iapi import panel_view
    from plotnine.scales.scale import scale


class coord_polar(coord):
    """
    Polar coordinate system.

    Maps one aesthetic to angle (theta) and the other to radius.
    Data is transformed at the Cartesian level so every standard geom
    works without modification.  Concentric circle and radial-spoke
    grid lines are drawn automatically from the scale breaks.

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
        Add a small buffer around the unit circle. Default ``True``.
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

    def setup_panel_params(
        self, scale_x: scale, scale_y: scale
    ) -> panel_view:
        from .coord_cartesian import coord_cartesian

        # Theta should always fill exactly one full revolution — no expansion.
        # R uses the caller-controlled expand flag (for padding around data).
        pv_theta = coord_cartesian(expand=False).setup_panel_params(scale_x, scale_y)
        pv_r     = coord_cartesian(expand=self.expand).setup_panel_params(scale_x, scale_y)

        # Store original ranges and breaks so transform() and
        # draw() can use them.
        if self.theta == "x":
            self.params["theta_range"] = pv_theta.x.range
            self.params["r_range"]     = pv_r.y.range
            self.params["r_breaks"]    = list(pv_r.y.breaks)
            self.params["theta_breaks"] = list(pv_theta.x.breaks)
        else:
            self.params["theta_range"] = pv_theta.y.range
            self.params["r_range"]     = pv_r.x.range
            self.params["r_breaks"]    = list(pv_r.x.breaks)
            self.params["theta_breaks"] = list(pv_theta.y.breaks)

        pv = pv_r  # use r-expanded view as the base for output ranges

        # Return a fixed unit-square output range; drop all tick marks so
        # the Cartesian theming draws nothing — the polar grid is drawn
        # explicitly in draw().
        pad = 0.1 if self.expand else 0.0
        out_range = (-1.0 - pad, 1.0 + pad)
        empty = np.array([], dtype=float)
        new_x = replace(
            pv.x, limits=out_range, range=out_range, breaks=[], minor_breaks=empty, labels=[]
        )
        new_y = replace(
            pv.y, limits=out_range, range=out_range, breaks=[], minor_breaks=empty, labels=[]
        )
        return replace(pv, x=new_x, y=new_y)

    def transform(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        munch: bool = False,
    ) -> pd.DataFrame:
        if self.theta == "x":
            theta_col, r_col = "x", "y"
        else:
            theta_col, r_col = "y", "x"

        if theta_col not in data.columns or r_col not in data.columns:
            return data

        theta_vals = data[theta_col].to_numpy(dtype=float)
        r_vals = data[r_col].to_numpy(dtype=float)

        t_min, t_max = (
            float(self.params["theta_range"][0]),
            float(self.params["theta_range"][1]),
        )
        r_min, r_max = (
            float(self.params["r_range"][0]),
            float(self.params["r_range"][1]),
        )

        # Normalise theta → [0, 1] → radians.
        denom_t = t_max - t_min
        theta_norm = (theta_vals - t_min) / denom_t if denom_t else np.zeros_like(theta_vals)
        angle = self.start + self.direction * theta_norm * 2.0 * np.pi

        # Normalise r → [0, 1].  Clamp below zero only; values slightly above
        # 1.0 land between the unit circle and the panel edge (which extends
        # to 1 + pad ≈ 1.1) and are used for axis-label annotations.
        denom_r = r_max - r_min
        r_norm = (r_vals - r_min) / denom_r if denom_r else np.zeros_like(r_vals)
        r_norm = np.clip(r_norm, 0.0, None)

        # Project to Cartesian.  Angle is measured from the positive-y axis
        # (12 o'clock) so x = r·sin(θ), y = r·cos(θ).
        data = data.copy()
        data[theta_col] = r_norm * np.sin(angle)
        data[r_col] = r_norm * np.cos(angle)
        return data

    def _r_norm(self, r_val: float) -> float:
        r_min, r_max = self.params["r_range"]
        denom = float(r_max) - float(r_min)
        return (float(r_val) - float(r_min)) / denom if denom else 0.0

    def _theta_angle(self, t_val: float) -> float:
        t_min, t_max = self.params["theta_range"]
        denom = float(t_max) - float(t_min)
        t_norm = (float(t_val) - float(t_min)) / denom if denom else 0.0
        return self.start + self.direction * t_norm * 2.0 * np.pi

    def draw(self, axs: list[Axes]) -> None:
        """Draw concentric circles and radial spokes onto each panel axes."""
        import matplotlib.patches as mpatches
        import matplotlib.lines as mlines

        r_breaks = [v for v in self.params.get("r_breaks", []) if v is not None]
        t_breaks = [v for v in self.params.get("theta_breaks", []) if v is not None]

        if not r_breaks and not t_breaks:
            return

        # Outermost circle radius (used as spoke length).
        valid_r = [self._r_norm(v) for v in r_breaks if np.isfinite(v)]
        r_outer = max(valid_r) if valid_r else 1.0

        grid_kw = dict(color="gray", alpha=0.3, linewidth=0.5, zorder=0.5)

        for ax in axs:
            # Concentric circles at each r break.
            for r_val in r_breaks:
                if not np.isfinite(r_val):
                    continue
                r = self._r_norm(r_val)
                circle = mpatches.Circle(
                    (0, 0), r,
                    fill=False, transform=ax.transData,
                    **grid_kw,
                )
                ax.add_patch(circle)

            # Radial spokes at each theta break.
            for t_val in t_breaks:
                if not np.isfinite(t_val):
                    continue
                angle = self._theta_angle(t_val)
                line = mlines.Line2D(
                    [0, r_outer * np.sin(angle)],
                    [0, r_outer * np.cos(angle)],
                    transform=ax.transData,
                    **grid_kw,
                )
                ax.add_line(line)

    def aspect(self, panel_params: panel_view) -> float:
        return 1.0

    def distance(
        self,
        x: pd.Series,
        y: pd.Series,
        panel_params: panel_view,
    ) -> np.ndarray:
        # Output space is [-1, 1]² so max diagonal ≈ 2√2.
        return dist_euclidean(x, y) / (2.0 * np.sqrt(2.0))
