from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np
from matplotlib import markers as mmarkers
from matplotlib.projections.polar import (
    PolarAxes,
    RadialAxis,
    RadialTick,
    ThetaAxis,
    ThetaTick,
)
from matplotlib.transforms import Affine2D

if TYPE_CHECKING:
    from matplotlib.transforms import Transform


class p9ThetaTick(ThetaTick):
    """
    Theta tick whose labels sit on the rim of their matching tick marks
    """

    def _get_text1_transform(self) -> tuple[Transform, str, str]:
        # matplotlib anchors the theta labels through a flipr-reversed
        # transform, sending label1 to tick2line's radius and label2 to
        # tick1line's. Use the unflipped tick transform so label1 shares
        # tick1line's inner radius instead.
        return self.axes.get_xaxis_transform("tick1"), "center", "center"

    def _get_text2_transform(self) -> tuple[Transform, str, str]:
        # Counterpart to _get_text1_transform: label2 shares tick2line's
        # outer radius.
        return self.axes.get_xaxis_transform("tick2"), "center", "center"

    def _update_padding(self, pad: float, angle: float) -> None:
        # With the base radii corrected above, flip matplotlib's pad signs
        # so the clearance pushes label1 further inward and label2 further
        # outward -- toward the correct side of each now-repaired label.
        padx = pad * np.cos(angle) / 72
        pady = pad * np.sin(angle) / 72
        self._text1_translate._t = (-padx, -pady)  # pyright: ignore[reportAttributeAccessIssue]
        self._text1_translate.invalidate()  # pyright: ignore[reportAttributeAccessIssue]
        self._text2_translate._t = (padx, pady)  # pyright: ignore[reportAttributeAccessIssue]
        self._text2_translate.invalidate()  # pyright: ignore[reportAttributeAccessIssue]


class p9ThetaAxis(ThetaAxis):
    """
    Theta axis whose labels follow their matching tick marks
    """

    _tick_class = p9ThetaTick


class p9RadialTick(RadialTick):
    """
    Radial tick whose mark and label share the start-spoke sweep side
    """

    def update_position(self, loc: float) -> None:
        # Matplotlib already handles the two radial axes at the ends of a
        # partial arc. For a full circle it places the labels at
        # `rlabel_position`, but leaves the tick marker unrotated. Convert
        # that position to its rendered screen angle, then turn the marker
        # perpendicular to the spoke, opposite the effective theta sweep.
        super().update_position(loc)

        axes = cast("PolarAxes", self.axes)
        thetamin = axes.get_thetamin()
        thetamax = axes.get_thetamax()
        if abs(abs(thetamax - thetamin) - 360.0) >= 1e-12:
            return

        direction = axes.get_theta_direction()
        offset = np.rad2deg(axes.get_theta_offset())
        spoke_angle = (axes.get_rlabel_position() * direction + offset) % 360
        marker_angle = np.deg2rad(spoke_angle - direction * 90)

        # Replace the marker's base transform so its one-sided tick points
        # along the computed tangent. `MarkerStyle.transformed()` would
        # compose with the existing TICKLEFT/TICKRIGHT transform instead.
        marker = self.tick1line.get_marker()
        if marker == mmarkers.TICKLEFT:
            transform = Affine2D().rotate(marker_angle)
        elif marker == mmarkers.TICKRIGHT:
            transform = Affine2D().scale(-1, 1).rotate(marker_angle)
        elif marker == "_":
            transform = Affine2D().rotate(marker_angle + np.pi / 2)
        else:
            transform = self.tick1line._marker._transform  # pyright: ignore[reportAttributeAccessIssue]
        self.tick1line._marker._transform = transform  # pyright: ignore[reportAttributeAccessIssue]

        mode, _ = self._labelrotation  # pyright: ignore[reportAttributeAccessIssue]
        angle = spoke_angle - 90
        ha, va = self._determine_anchor(mode, angle, direction > 0)  # pyright: ignore[reportAttributeAccessIssue]
        self.label1.set_horizontalalignment(ha)
        self.label1.set_verticalalignment(va)


class p9RadialAxis(RadialAxis):
    """
    Radial axis whose ticks follow plotnine's start-spoke geometry
    """

    _tick_class = p9RadialTick

    def _copy_tick_props(self, src: p9RadialTick, dest: p9RadialTick) -> None:
        super()._copy_tick_props(src, dest)  # pyright: ignore[reportAttributeAccessIssue]
        dest.update_position(dest.get_loc())
