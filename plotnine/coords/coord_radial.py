from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .coord_polar import coord_polar

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes
    from plotnine.iapi import panel_view


class coord_radial(coord_polar):
    """
    Radial coordinate system.

    A modernised polar coordinate system that adds support for partial arcs,
    inner radius (donut/gauge charts), configurable radial-axis placement, and
    automatic rotation of the ``angle`` aesthetic to align with theta.

    Inherits from :class:`coord_polar`; all standard geoms work without
    modification.

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
        Add a small buffer around the data on the radius axis. Default ``True``.
    inner_radius :
        Size of the inner hole as a fraction of the outer radius, in
        ``[0, 1)``.  ``0`` (default) means no hole; ``0.3`` creates a 30 %
        donut hole, useful for gauge and donut charts.
    r_axis_inside :
        Where to place the radial (r) axis tick labels.

        * ``None`` (default) — let Matplotlib decide (usually outside).
        * ``True`` — force inside, aligned just past the *start* angle.
        * ``False`` — force outside (Matplotlib default).
        * *float* — place at this theta angle in radians (clockwise from North).
    rotate_angle :
        If ``True``, automatically add the local theta angle (in degrees) to
        the ``angle`` aesthetic so that text or other rotated marks align with
        the spoke direction.  Default ``False``.
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def _arc(self) -> float:
        """Total arc in radians (signed: positive when going clockwise for direction=1)."""
        if self.end is not None:
            return self.end - self.start
        return self.direction * 2.0 * np.pi

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
        if self.rotate_angle and "angle" in data.columns and "x" in data.columns:
            data = data.copy()
            data["angle"] = data["angle"] + np.degrees(data["x"])
        return data

    # ------------------------------------------------------------------
    # Draw decorations on PolarAxes
    # ------------------------------------------------------------------

    def draw(self, axs: list[Axes]) -> None:
        """Configure PolarAxes: arc limits, inner radius, axis placement."""
        super().draw(axs)

        r_min, r_max = self.params.get("r_range", (0.0, 1.0))
        arc = self._arc

        for ax in axs:
            # Restrict visible theta range for partial arcs.
            if self.end is not None:
                theta_lo = min(self.start, self.start + arc)
                theta_hi = max(self.start, self.start + arc)
                ax.set_thetalim(theta_lo, theta_hi)

            # Inner radius: push the data away from the centre by setting a
            # virtual r-origin below r_min.  Formula: solve
            #   inner_radius = (r_min - r_origin) / (r_max - r_origin)
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
                ax.set_rorigin(r_origin)

            # Radial axis label placement.
            if self.r_axis_inside is not None:
                if isinstance(self.r_axis_inside, bool):
                    if self.r_axis_inside:
                        # Just inside the start angle keeps it out of the data.
                        ax.set_rlabel_position(np.degrees(self.start) + 10)
                else:
                    ax.set_rlabel_position(np.degrees(float(self.r_axis_inside)))
