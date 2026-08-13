from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np
from matplotlib import artist as martist
from matplotlib import markers as mmarkers
from matplotlib.projections.polar import (
    RadialAxis,
    RadialTick,
    ThetaAxis,
    ThetaTick,
)
from matplotlib.transforms import Affine2D, Bbox, ScaledTranslation

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase
    from matplotlib.lines import Line2D
    from matplotlib.text import Text
    from matplotlib.transforms import Transform
    from numpy.typing import NDArray

    from plotnine.typing import PolarSide

    from ._radial_axes import p9RadialAxes


_NON_DESCENDING_NUMERIC_CHARS = frozenset("0123456789.+-\N{MINUS SIGN}eE")


def label_bounds(label: Text, renderer: RendererBase) -> Bbox:
    """
    Return label bounds with unused numeric descent removed

    Matplotlib reserves the font's full descent even when a numeric label
    has no descenders. Excluding that space keeps the visible gap between
    labels and ticks consistent around the panel.
    """
    bbox, parts, _ = label._get_layout(renderer)  # pyright: ignore[reportAttributeAccessIssue]
    descent = parts[-1][1][2]
    x, y = label.get_unitless_position()
    x, y = label.get_transform().transform((x, y))
    bbox = bbox.translated(x, y)

    text = label.get_text()
    _, ismath = label._preprocess_math(text)  # pyright: ignore[reportAttributeAccessIssue]
    # Exclude the unused font descent from simple numeric labels without
    # measuring rendered glyphs.
    if (
        text
        and "\n" not in text
        and ismath is False
        and set(text) <= _NON_DESCENDING_NUMERIC_CHARS
    ):
        bbox = Bbox.from_extents(bbox.x0, bbox.y0 + descent, bbox.x1, bbox.y1)

    return bbox


def facing_point(box: Bbox, unit: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Return the point on a label's bounds that faces the panel

    `unit` points away from the panel. The opposite point is an edge midpoint
    for an axis-aligned vector and moves towards a corner between axes.
    """
    ux, uy = unit
    return np.array(
        [
            box.x0 + (0.5 - ux / 2) * box.width,
            box.y0 + (0.5 - uy / 2) * box.height,
        ]
    )


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
        # Matplotlib pads theta labels from their centres, so the visible gap
        # varies with the label's angle. Place the point facing the panel at
        # the themed distance beyond its own tick.
        axes = cast("p9RadialAxes", self.axes)
        loc = self.get_loc()

        pairs: tuple[
            tuple[Text, Line2D, ScaledTranslation, PolarSide], ...
        ] = (
            (
                self.label1,
                self.tick1line,
                self._text1_translate,  # pyright: ignore[reportAttributeAccessIssue]
                "theta_inside",
            ),
            (
                self.label2,
                self.tick2line,
                self._text2_translate,  # pyright: ignore[reportAttributeAccessIssue]
                "theta_outside",
            ),
        )

        for label, tickline, translate, side in pairs:
            if not label.get_visible() or not label.get_text():
                continue

            label.set_horizontalalignment("center")
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
            unit = axes.outward_unit(side, loc)

            # Apply the padding at the label's centre, then correct the offset
            # so the point facing the panel reaches the same target.
            padded = unit * base_pad / 72
            translate._t = tuple(padded)
            translate.invalidate()

            target = label.get_transform().transform(label.get_position())
            point = facing_point(label_bounds(label, renderer), unit)
            translate._t = tuple(padded + (target - point) / axes.figure.dpi)
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

    def __init__(self, axes, *args, **kwargs):
        # `RadialTick` has no label translations. Add one to each label
        # transform so `draw` can position the pair from its measured bounds.
        figure = axes.get_figure(root=False)
        self._text1_translate = ScaledTranslation(0, 0, figure.dpi_scale_trans)
        self._text2_translate = ScaledTranslation(0, 0, figure.dpi_scale_trans)
        super().__init__(axes, *args, **kwargs)

    def _placements(
        self,
    ) -> list[tuple[PolarSide, Text, Line2D, ScaledTranslation]]:
        """
        Return the label placement for each active r boundary

        An arc places one pair on each end spoke. A full circle places both
        pairs on one spoke, where this axis draws the pair selected by
        `_tick_side`.
        """
        start: tuple[PolarSide, Text, Line2D, ScaledTranslation] = (
            "r_start",
            self.label1,
            self.tick1line,
            self._text1_translate,
        )
        end: tuple[PolarSide, Text, Line2D, ScaledTranslation] = (
            "r_end",
            self.label2,
            self.tick2line,
            self._text2_translate,
        )
        if not cast("p9RadialAxes", self.axes).is_full_circle:
            return [start, end]
        return [end] if self._tick_side > 0 else [start]

    def _pad_offset(self, unit: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Return the pre-measurement translation from the spoke
        """
        # `self._pad` includes the tick length and the gap beyond the mark.
        return unit * self._pad / 72  # pyright: ignore[reportAttributeAccessIssue]

    def update_position(self, loc: float) -> None:
        # Matplotlib's discrete text alignments make the gap depend on the
        # spoke angle. Centre each label on its spoke and pad it in display
        # space. `draw` then aligns its measured edge with that padded point.

        # On a full circle, Matplotlib hides the second tick and label pair
        # because both pairs occupy one spoke. The secondary r-axis uses that
        # pair on the opposite side, so preserve its visibility across the
        # base position update.
        want_label = self.label2.get_visible()
        want_tick = self.tick2line.get_visible()

        super().update_position(loc)

        axes = cast("p9RadialAxes", self.axes)

        for side, label, tickline, translate in self._placements():
            unit = axes.outward_unit(side, loc)

            if axes.is_full_circle:
                if side == "r_end":
                    label.set_visible(want_label)
                    tickline.set_visible(want_tick)

                # On a full circle, the end tick anchors at `thetamax`
                # (`x = 1`) and diverges from the shared start spoke as the
                # radius grows. Move it to `x = 0`, where the start tick
                # already anchors.
                tickline.set_xdata([0])

                # Replace the marker's base transform so a one-sided tick
                # points outwards. `MarkerStyle.transformed()` would compose
                # with the existing `TICKLEFT` or `TICKRIGHT` transform.
                #
                # The outward angle distinguishes primary and secondary ticks
                # by 180°. `TICKLEFT` and `TICKRIGHT` share the same path, so
                # rotate both directly. Applying `TICKRIGHT`'s horizontal flip
                # would place the secondary mark on the primary side.
                marker_angle = np.arctan2(unit[1], unit[0])
                marker = tickline.get_marker()
                tick_marker = cast("mmarkers.MarkerStyle", tickline._marker)  # pyright: ignore[reportAttributeAccessIssue]
                if marker in (mmarkers.TICKLEFT, mmarkers.TICKRIGHT):
                    transform = Affine2D().rotate(marker_angle)
                elif marker == "_":
                    transform = Affine2D().rotate(marker_angle + np.pi / 2)
                else:
                    transform = tick_marker._transform  # pyright: ignore[reportAttributeAccessIssue]
                tick_marker._transform = transform  # pyright: ignore[reportAttributeAccessIssue]

                # For a full circle, the base transform interprets x as an
                # angle. Set x to the shared spoke. For an arc, it interprets
                # x as a sweep fraction and already places each pair on an
                # end spoke.
                label.set_x(0)

            # Request the base transform without padding, then add a fixed
            # display-space offset. Otherwise Matplotlib derives an arc
            # label's padding direction from the view limits, which can point
            # away from its spoke after the sweep reverses.
            base = (
                axes.get_yaxis_text2_transform(0)[0]
                if side == "r_end"
                else axes.get_yaxis_text1_transform(0)[0]
            )
            label.set_transform(base + translate)
            label.set_horizontalalignment("center")
            label.set_verticalalignment("center")
            translate._t = tuple(self._pad_offset(unit))  # pyright: ignore[reportAttributeAccessIssue]
            translate.invalidate()

    def _position_labels(self, renderer: RendererBase) -> None:
        # Recompute from the initial pad offset on every draw so translations
        # do not accumulate across repeated draws.
        axes = cast("p9RadialAxes", self.axes)
        loc = self.get_loc()

        for side, label, _, translate in self._placements():
            if not label.get_visible() or not label.get_text():
                continue

            unit = axes.outward_unit(side, loc)
            padded = self._pad_offset(unit)
            translate._t = tuple(padded)  # pyright: ignore[reportAttributeAccessIssue]
            translate.invalidate()

            target = label.get_transform().transform(label.get_position())
            point = facing_point(label_bounds(label, renderer), unit)
            translate._t = tuple(padded + (target - point) / axes.figure.dpi)  # pyright: ignore[reportAttributeAccessIssue]
            translate.invalidate()

    @martist.allow_rasterization
    def draw(self, renderer: RendererBase) -> None:
        self._position_labels(renderer)
        super().draw(renderer)


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
