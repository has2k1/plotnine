from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd

from ..scales.scale_binned import _BinIntervals, scale_binned
from .guide_legend import guide_legend

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.artist import Artist
    from matplotlib.offsetbox import PackerBase

    from ..scales.scale import scale
    from ..typing import FloatArray, Side


@dataclass
class guide_bins(guide_legend):
    """A legend with adjacent geom keys separated by bin boundaries"""

    show_limits: bool | None = None
    """Whether to label both scale limits"""

    _intervals: _BinIntervals = field(init=False, repr=False)
    _boundary_values: FloatArray = field(init=False, repr=False)
    _boundary_labels: Sequence[str] = field(init=False, repr=False)

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

    def draw(self) -> PackerBase:
        """Draw adjacent geom keys and label their boundaries"""
        from matplotlib.collections import LineCollection
        from matplotlib.offsetbox import (
            DrawingArea,
            HPacker,
            TextArea,
            VPacker,
        )
        from matplotlib.patches import Rectangle
        from matplotlib.text import Text

        from .._mpl.offsetbox import FixedSizePacker

        elements = self.elements
        drawings = self._draw_keys(elements)
        targets = self.theme.targets
        font_size = self.theme.getp(("legend_text_legend", "size"))
        text_margin = 6

        if elements.is_vertical:
            key_width = max(d.width for d in drawings)
            heights = [d.height for d in drawings]
            total_height = sum(heights)
            label_width = max(30, font_size * 4)
            canvas = DrawingArea(
                key_width + text_margin + label_width,
                total_height,
                clip=False,
            )
            order = drawings if self.reverse else drawings[::-1]
            y = 0.0
            for drawing in order:
                drawing.set_offset((0, y))
                canvas.add_artist(drawing)
                y += drawing.height
            locations = self._boundary_locations(heights, total_height)
            texts = []
            for label, y in zip(self._boundary_labels, locations):
                text = Text(
                    key_width + text_margin,
                    y,
                    label,
                    fontsize=font_size,
                    ha="left",
                    va="center",
                )
                canvas.add_artist(text)
                texts.append(text)
            tick_segments = [((0, y), (key_width, y)) for y in locations]
            frame = Rectangle(
                (0, 0), key_width, total_height, facecolor="none"
            )
        else:
            widths = [d.width for d in drawings]
            key_height = max(d.height for d in drawings)
            total_width = sum(widths)
            label_height = max(14, font_size * 1.5)
            canvas = DrawingArea(
                total_width,
                key_height + text_margin + label_height,
                clip=False,
            )
            order = drawings[::-1] if self.reverse else drawings
            x = 0.0
            for drawing in order:
                drawing.set_offset((x, label_height + text_margin))
                canvas.add_artist(drawing)
                x += drawing.width
            locations = self._boundary_locations(widths, total_width)
            texts = []
            for label, x in zip(self._boundary_labels, locations):
                text = Text(
                    x,
                    0,
                    label,
                    fontsize=font_size,
                    ha="center",
                    va="bottom",
                )
                canvas.add_artist(text)
                texts.append(text)
            key_bottom = label_height + text_margin
            tick_segments = [
                ((x, key_bottom), (x, key_bottom + key_height))
                for x in locations
            ]
            frame = Rectangle(
                (0, key_bottom),
                total_width,
                key_height,
                facecolor="none",
            )

        ticks = LineCollection(tick_segments)
        canvas.add_artist(ticks)
        canvas.add_artist(frame)
        targets.legend_text_legend = texts
        targets.legend_ticks = ticks
        targets.legend_frame = frame

        title = cast("str", self.title)
        title_box = TextArea(title)
        targets.legend_title = title_box._text  # type: ignore
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
            [canvas] if elements.title.is_blank else [title_box, canvas][slc]
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
