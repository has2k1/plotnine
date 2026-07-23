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
from matplotlib.transforms import Affine2D, Bbox, ScaledTranslation

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase
    from matplotlib.text import Text
    from matplotlib.transforms import Transform


_NON_DESCENDING_NUMERIC_CHARS = frozenset("0123456789.+-\N{MINUS SIGN}eE")


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

    def _label_bounds(self, label: Text, renderer: RendererBase) -> Bbox:
        """
        Return label bounds without unused numeric descent

        Matplotlib reserves the font's full descent even when a numeric label
        has no descenders. Removing that unused space prevents the visible
        gap between theta labels and ticks from varying around the circle.
        """
        bbox, parts, _ = label._get_layout(renderer)  # pyright: ignore[reportAttributeAccessIssue]
        descent = parts[-1][1][2]
        x, y = label.get_unitless_position()
        x, y = label.get_transform().transform((x, y))
        bbox = bbox.translated(x, y)

        text = label.get_text()
        _, ismath = label._preprocess_math(text)  # pyright: ignore[reportAttributeAccessIssue]
        # Common numeric ticks have no descenders, so exclude Matplotlib's
        # unused descent without measuring rendered ink.
        if (
            text
            and "\n" not in text
            and ismath is False
            and set(text) <= _NON_DESCENDING_NUMERIC_CHARS
        ):
            bbox = Bbox.from_extents(
                bbox.x0,
                bbox.y0 + descent,
                bbox.x1,
                bbox.y1,
            )

        return bbox

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
            corners = self._label_bounds(label, renderer).corners()
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

    # Which side of the shared full-circle spoke this axis's ticks occupy,
    # as a signed perpendicular (`-1` / `+1`). The primary and secondary
    # r-axes take opposite sides so their marks and labels never overlap.
    # The sign also selects the tick/label pair: the positive side draws the
    # end pair (`label2`/`tick2line`, the `r_end` side theming uses), the
    # negative side the start pair.
    _tick_side: int = -1

    def update_position(self, loc: float) -> None:
        # Matplotlib already handles the two radial axes at the ends of a
        # partial arc. For a full circle it places the labels at
        # `rlabel_position`, but leaves the tick marker unrotated. Convert
        # that position to its rendered screen angle, then turn the marker
        # perpendicular to the spoke, opposite the effective theta sweep.

        # On a full circle the two tick/label pairs would land on the same
        # spoke, so the `super().update_position` below hides the second
        # one. But the secondary r-axis draws that pair, on the opposite
        # side of the spoke — so save its visibility now and restore it,
        # after the super call, in the `_tick_side > 0` branch.
        want_label = self.label2.get_visible()
        want_tick = self.tick2line.get_visible()

        super().update_position(loc)

        axes = cast("PolarAxes", self.axes)
        thetamin = axes.get_thetamin()
        thetamax = axes.get_thetamax()
        if abs(abs(thetamax - thetamin) - 360.0) >= 1e-12:
            return

        if self._tick_side > 0:
            label, tickline = self.label2, self.tick2line
            text1_transform = axes.get_yaxis_text2_transform(0)[0]
            label.set_visible(want_label)
            tickline.set_visible(want_tick)
        else:
            label, tickline = self.label1, self.tick1line
            text1_transform = axes.get_yaxis_text1_transform(0)[0]

        # The end pair's tick line anchors at theta = thetamax (x = 1), which
        # for a full circle fans away from the shared start spoke as the
        # radius grows. Anchor it on the spoke (x = 0), where the start pair
        # already sits, so the mirrored marker below stays on the spoke.
        tickline.set_xdata([0])

        direction = axes.get_theta_direction()
        offset = np.rad2deg(axes.get_theta_offset())
        spoke_angle = (axes.get_rlabel_position() * direction + offset) % 360
        # `_tick_side` flips the perpendicular so a secondary axis mirrors
        # the primary across the shared spoke.
        marker_angle = np.deg2rad(
            spoke_angle + self._tick_side * direction * 90
        )

        # Replace the marker's base transform so its one-sided tick points
        # along `marker_angle`. `MarkerStyle.transformed()` would compose
        # with the existing TICKLEFT/TICKRIGHT transform instead.
        #
        # `marker_angle` already carries the full direction (the primary and
        # secondary sides differ by 180°), and TICKLEFT/TICKRIGHT share the
        # same `[[0, 0], [1, 0]]` path, so both rotate by it directly. Adding
        # TICKRIGHT's own `scale(-1, 1)` here would undo the `_tick_side`
        # mirror and send the secondary mark back onto the primary's side.
        marker = tickline.get_marker()
        tick_marker = cast("mmarkers.MarkerStyle", tickline._marker)  # pyright: ignore[reportAttributeAccessIssue]
        if marker in (mmarkers.TICKLEFT, mmarkers.TICKRIGHT):
            transform = Affine2D().rotate(marker_angle)
        elif marker == "_":
            transform = Affine2D().rotate(marker_angle + np.pi / 2)
        else:
            transform = tick_marker._transform  # pyright: ignore[reportAttributeAccessIssue]
        tick_marker._transform = transform  # pyright: ignore[reportAttributeAccessIssue]

        # A constant theta offset fans labels farther from the spoke as the
        # radius grows. Keep every label on the spoke and apply its padding
        # in display space so their edges remain aligned.
        mode, _ = self._labelrotation  # pyright: ignore[reportAttributeAccessIssue]
        angle = spoke_angle - 90
        start = (self._tick_side * direction) < 0
        ha, va = self._determine_anchor(mode, angle, start)  # pyright: ignore[reportAttributeAccessIssue]
        # self._pad includes the tick length and the gap between
        # the tick and text.
        shift = self._pad  # pyright: ignore[reportAttributeAccessIssue]
        text_transform = (
            # Place the text flush with the spoke. For a full circle,
            # matplotlib ignores the pad passed to this method.
            text1_transform
            # Move the text by a fixed physical distance independent of the
            # data radius.
            + ScaledTranslation(
                np.cos(marker_angle) * shift / 72,
                np.sin(marker_angle) * shift / 72,
                axes.figure.dpi_scale_trans,
            )
        )
        label.set_x(0)
        label.set_transform(text_transform)
        label.set_horizontalalignment(ha)
        label.set_verticalalignment(va)


class p9SecondaryRadialTick(p9RadialTick):
    """
    Full-circle secondary r-axis tick mirrored across the shared spoke

    The secondary r-axis shares the primary's single full-circle spoke, so
    it sits on the opposite side of it. That side draws the end tick/label
    pair — the same pair theming resolves for the `r_end` side — keeping its
    mark and label clear of the primary's.
    """

    _tick_side = 1


class p9RadialAxis(RadialAxis):
    """
    Radial axis whose ticks follow plotnine's start-spoke geometry
    """

    _tick_class = p9RadialTick

    def _copy_tick_props(self, src: p9RadialTick, dest: p9RadialTick) -> None:
        super()._copy_tick_props(src, dest)  # pyright: ignore[reportAttributeAccessIssue]
        dest.update_position(dest.get_loc())


class p9SecondaryRadialAxis(p9RadialAxis):
    """
    Secondary radial axis mirrored across the primary's full-circle spoke
    """

    _tick_class = p9SecondaryRadialTick
