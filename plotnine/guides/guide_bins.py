from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd

from ..exceptions import PlotnineError
from ..scales.scale_binned import _BinIntervals, scale_binned
from ..themes.elements import element_line
from ..themes.theme import theme
from .guide_legend import GuideElementsLegend, guide_legend

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.artist import Artist
    from matplotlib.offsetbox import PackerBase

    from .._mpl.offsetbox import ColoredDrawingArea
    from ..scales.scale import scale
    from ..typing import FloatArray, Side
    from .guides import LegendOwner


@dataclass
class guide_bins(guide_legend):
    """A legend with adjacent geom keys separated by bin boundaries"""

    show_limits: bool | None = None
    """Whether to label both scale limits"""

    _intervals: _BinIntervals = field(init=False, repr=False)
    _boundary_values: FloatArray = field(init=False, repr=False)
    _boundary_labels: Sequence[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._elements_cls = GuideElementsBins
        self.elements: GuideElementsBins  # pyright: ignore[reportIncompatibleVariableOverride]

    def _resolve_theme(self, owner: LegendOwner) -> theme:
        """
        Return the resolved binned-guide theme with default tick styling
        """
        resolved = super()._resolve_theme(owner)
        if resolved.T.get("legend_ticks") is None:
            resolved += theme(legend_ticks=element_line(color="black", size=1))
        return resolved

    def train(self, scale: scale, aesthetic: str | None = None):
        """Create one geom key per bin and label selected boundaries"""
        if isinstance(scale, scale_binned) and scale.breaks in (None, False):
            return None
        if aesthetic is None:
            aesthetic = scale.aesthetics[0]

        self._intervals = _BinIntervals.make(scale)
        show_limits = self.show_limits
        if show_limits is None:
            show_limits = bool(getattr(scale, "show_limits", False))
        self._boundary_values = self._intervals.get_breaks(show_limits)
        if isinstance(scale, scale_binned):
            self._boundary_labels = scale.get_labels(
                self._boundary_values.tolist()
            )
        else:
            self._boundary_labels = [str(x) for x in self._boundary_values]

        mapped = scale.map(self._intervals.source_values)
        self.key = pd.DataFrame(
            {
                aesthetic: mapped,
                "label": self._interval_labels(scale),
            }
        )
        info = "\n".join(
            [
                str(self.title),
                " ".join(str(x) for x in self._boundary_labels),
                str(self.direction),
                self.__class__.__name__,
            ]
        )
        self.hash = hashlib.sha256(info.encode("utf-8")).hexdigest()
        return self

    def _interval_labels(self, scale: scale) -> list[str]:
        if not isinstance(scale, scale_binned):
            return [str(x) for x in self._intervals.source_values]

        left, right = ("(", "]") if scale.right else ("[", ")")
        return [
            f"{left}{low:g}, {high:g}{right}"
            for low, high in zip(
                self._intervals.boundaries[:-1],
                self._intervals.boundaries[1:],
            )
        ]

    def _order_keys(
        self, drawings: list[ColoredDrawingArea]
    ) -> list[ColoredDrawingArea]:
        """
        Order key drawings for their display coordinates
        """
        if self.elements.is_vertical:
            return drawings if self.reverse else drawings[::-1]
        return drawings[::-1] if self.reverse else drawings

    def draw(self) -> PackerBase:
        """Draw adjacent geom keys and label their boundaries"""
        from matplotlib.collections import LineCollection
        from matplotlib.offsetbox import (
            DrawingArea,
            HPacker,
            TextArea,
            VPacker,
        )

        from .._mpl.offsetbox import OffsetPacker

        targets = self.theme.targets
        elements = self.elements
        drawings = self._order_keys(self._draw_keys(elements))
        labels: list[TextArea] = []

        if elements.is_vertical:
            # axis line and axis ticks coordinates
            key_width = elements.key_widths[0]
            heights = [da.height for da in drawings]
            total_height = sum(heights)
            y = 0.0
            offsets: list[tuple[float, float]] = []
            for da in drawings:
                offsets.append((0, y))
                y += da.height

            locations = self._boundary_locations(heights, total_height)
            axis_x = 0 if elements.text_position == "left" else key_width
            tick_x = axis_x + (
                key_width * elements.ticks_length
                if elements.text_position == "left"
                else -key_width * elements.ticks_length
            )
            axis_segment = ((axis_x, 0), (axis_x, total_height))
            tick_segments = [((axis_x, y), (tick_x, y)) for y in locations]

            # axis line and axis ticks artists
            axis_canvas = DrawingArea(key_width, total_height, clip=False)
            axis_line = LineCollection([axis_segment])
            ticks = LineCollection(tick_segments)
            axis_canvas.add_artist(axis_line)
            axis_canvas.add_artist(ticks)
            key_box = OffsetPacker(
                key_width,
                total_height,
                [*drawings, axis_canvas],
                [*offsets, (0, 0)],
            )
            content = key_box
            if not elements.text.is_blank:
                ha = "right" if elements.text_position == "left" else "left"
                labels = [
                    TextArea(label, textprops={"ha": ha, "va": "center"})
                    for label in self._boundary_labels
                ]
                label_box = OffsetPacker(
                    None,
                    total_height,
                    labels,
                    [(0, y) for y in locations],
                )
                children = (
                    [label_box, key_box]
                    if elements.text_position == "left"
                    else [key_box, label_box]
                )
                content = HPacker(
                    children=children,
                    sep=elements.text.margins[0],
                    align="baseline",
                    pad=0,
                )
        else:
            # axis line and axis ticks coordinates
            widths = [d.width for d in drawings]
            key_height = elements.key_heights[0]
            total_width = sum(widths)
            x = 0.0
            offsets: list[tuple[float, float]] = []
            for da in drawings:
                offsets.append((x, 0))
                x += da.width

            locations = self._boundary_locations(widths, total_width)
            axis_y = key_height if elements.text_position == "top" else 0
            tick_y = axis_y + (
                -key_height * elements.ticks_length
                if elements.text_position == "top"
                else key_height * elements.ticks_length
            )
            axis_segment = ((0, axis_y), (total_width, axis_y))
            tick_segments = [((x, axis_y), (x, tick_y)) for x in locations]

            # axis line and axis ticks artists
            axis_canvas = DrawingArea(total_width, key_height, clip=False)
            axis_line = LineCollection([axis_segment])
            ticks = LineCollection(tick_segments)
            axis_canvas.add_artist(axis_line)
            axis_canvas.add_artist(ticks)
            key_box = OffsetPacker(
                total_width,
                key_height,
                [*drawings, axis_canvas],
                [*offsets, (0, 0)],
            )
            content = key_box
            if not elements.text.is_blank:
                labels = [
                    TextArea(label, textprops={"ha": "center"})
                    for label in self._boundary_labels
                ]
                label_box = OffsetPacker(
                    total_width,
                    None,
                    labels,
                    [(x, 0) for x in locations],
                )
                children = (
                    [label_box, key_box]
                    if elements.text_position == "top"
                    else [key_box, label_box]
                )
                content = VPacker(
                    children=children,
                    sep=elements.text.margins[0],
                    align="baseline",
                    pad=0,
                )

        targets.legend_axis_line = axis_line
        targets.legend_ticks = ticks
        targets.legend_text_legend = [box._text for box in labels]  # pyright: ignore[reportAttributeAccessIssue]

        title = cast("str", self.title)
        title_box = TextArea(title)
        targets.legend_title = title_box._text  # pyright: ignore[reportAttributeAccessIssue]
        obverse = slice(0, None)
        reverse = slice(None, None, -1)
        lookup: dict[Side, tuple[type[PackerBase], slice]] = {
            "right": (HPacker, reverse),
            "left": (HPacker, obverse),
            "bottom": (VPacker, reverse),
            "top": (VPacker, obverse),
        }
        packer, slc = lookup[elements.title_position]
        children: list[Artist] = (
            [content] if elements.title.is_blank else [title_box, content][slc]
        )
        return packer(
            children=children,
            sep=elements.title.margin,
            align=elements.title.align,
            pad=elements.margin,
        )

    def _boundary_locations(
        self,
        sizes: Sequence[float],
        total: float,
    ) -> list[float]:
        cumulative = np.concatenate(([0.0], np.cumsum(sizes)))
        indexes = np.searchsorted(
            self._intervals.boundaries,
            self._boundary_values,
        )
        if self.reverse:
            indexes = len(sizes) - indexes
        locations = cumulative[indexes]
        if self.elements.is_vertical:
            locations = total - locations
        return locations.tolist()


class GuideElementsBins(GuideElementsLegend):
    """Theme properties and dimensions for adjacent binned keys"""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.guide_kind = "legend"

    @cached_property
    def text_position(self) -> Side:
        valid = ("left", "right") if self.is_vertical else ("top", "bottom")
        position = self.theme.getp("legend_text_position") or valid[1]
        if position not in valid:
            raise PlotnineError(
                f"For a {self.direction} guide, legend_text_position must be "
                f"one of {set(valid)!r}, not {position!r}."
            )
        return cast("Side", position)

    @cached_property
    def text_positions(self) -> Sequence[Side]:
        return (self.text_position,) * self.guide.num_breaks

    @cached_property
    def ticks_length(self) -> float:
        return self.theme.getp("legend_ticks_length")

    @cached_property
    def key_widths(self) -> list[float]:
        widths = [width for width, _ in self._key_dimensions]
        return [max(widths)] * len(widths)

    @cached_property
    def key_heights(self) -> list[float]:
        heights = [height for _, height in self._key_dimensions]
        return [max(heights)] * len(heights)
