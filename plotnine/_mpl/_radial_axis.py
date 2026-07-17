from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np
from matplotlib import artist as martist
from matplotlib import markers as mmarkers
from matplotlib.projections.polar import (
    PolarAxes,
    RadialAxis,
    RadialTick,
    ThetaAxis,
    ThetaTick,
)
from matplotlib.transforms import Affine2D, ScaledTranslation

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase
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
        # The rendered label extent replaces matplotlib's fixed allowance.
        self._radial_angle = angle
        self._text1_translate._t = (0, 0)  # pyright: ignore[reportAttributeAccessIssue]
        self._text1_translate.invalidate()  # pyright: ignore[reportAttributeAccessIssue]
        self._text2_translate._t = (0, 0)  # pyright: ignore[reportAttributeAccessIssue]
        self._text2_translate.invalidate()  # pyright: ignore[reportAttributeAccessIssue]

    def _position_labels(self, renderer: RendererBase) -> None:
        # Matplotlib pads theta labels from their centres by a fixed amount,
        # which leaves angle-dependent gaps at the edges. We override to place
        # each nearest edge at the themed margin beyond its tick or the axis
        # boundary.
        axes = cast("PolarAxes", self.axes)
        radial = np.array(
            [np.cos(self._radial_angle), np.sin(self._radial_angle)]
        )

        for label, tickline, translate, direction in (
            (
                self.label1,
                self.tick1line,
                self._text1_translate,  # pyright: ignore[reportAttributeAccessIssue]
                -1,
            ),
            (
                self.label2,
                self.tick2line,
                self._text2_translate,  # pyright: ignore[reportAttributeAccessIssue]
                1,
            ),
        ):
            if not label.get_visible() or not label.get_text():
                continue

            label.set_verticalalignment("center")
            label.set_verticalalignment("center")
            tick_length = (
                self._size  # pyright: ignore[reportAttributeAccessIssue]
                if tickline.get_visible()
                else 0
            )
            base_pad = (
                self._base_pad  # pyright: ignore[reportAttributeAccessIssue]
                + tick_length
            )
            unit = radial * direction
            translate._t = tuple(unit * base_pad / 72)
            translate.invalidate()

            anchor = label.get_transform().transform(label.get_position())
            corners = label.get_window_extent(renderer).corners()
            # Offset the label by its radial extent so the margin starts at
            # the nearest text edge, not at the label centre.
            edge_offset = np.min((corners - anchor) @ unit)
            corrected = base_pad - edge_offset * 72 / axes.figure.dpi
            translate._t = tuple(unit * corrected / 72)
            translate.invalidate()

    @martist.allow_rasterization
    def draw(self, renderer: RendererBase) -> None:
        self._position_labels(renderer)
        super().draw(renderer)


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

        # A constant theta offset fans labels farther from the spoke as the
        # radius grows. Keep every label on the spoke and apply its padding
        # in display space so their edges remain aligned.
        mode, _ = self._labelrotation  # pyright: ignore[reportAttributeAccessIssue]
        angle = spoke_angle - 90
        ha, va = self._determine_anchor(mode, angle, direction > 0)  # pyright: ignore[reportAttributeAccessIssue]
        # self._pad includes the tick length and the gap between
        # the tick and text.
        shift = self._pad  # pyright: ignore[reportAttributeAccessIssue]
        text_transform = (
            # Place the text flush with the spoke. For a full circle,
            # matplotlib ignores the pad passed to this method.
            axes.get_yaxis_text1_transform(0)[0]
            # Move the text by a fixed physical distance independent of the
            # data radius.
            + ScaledTranslation(
                np.cos(marker_angle) * shift / 72,
                np.sin(marker_angle) * shift / 72,
                axes.figure.dpi_scale_trans,
            )
        )
        self.label1.set_x(0)
        self.label1.set_transform(text_transform)
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
