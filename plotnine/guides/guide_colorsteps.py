from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from mizani.bounds import rescale

from ..scales.scale_binned import _BinIntervals, scale_binned
from .guide_colorbar import (
    GuideElementsColorbar,
    add_segmented_colorbar,
    guide_colorbar,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.offsetbox import AuxTransformBox

    from ..scales.scale import scale


@dataclass
class guide_colorsteps(guide_colorbar):
    """A colour bar with one constant-colour segment per bin"""

    even_steps: bool = True
    """Whether to give every colour segment the same physical size"""

    show_limits: bool | None = None
    """Whether to label both scale limits"""

    # The parameters are only used by guide_colorbar
    nbin: int = field(default=300, init=False, repr=False)
    draw_ulim: bool = field(default=True, init=False, repr=False)
    draw_llim: bool = field(default=True, init=False, repr=False)

    _intervals: _BinIntervals = field(init=False, repr=False)

    @property
    def _elements_cls(self) -> type[GuideElementsColorsteps]:
        return GuideElementsColorsteps

    def train(self, scale: scale, aesthetic: str | None = None):
        """Create segment colours and label the selected bin boundaries"""
        if isinstance(scale, scale_binned) and scale.breaks in (None, False):
            return None

        if aesthetic is None:
            aesthetic = scale.aesthetics[0]

        self._intervals = _BinIntervals.make(scale)
        colors = list(scale.map(self._intervals.source_values))
        ticks = self._tick_values(scale)
        if isinstance(scale, scale_binned):
            labels = scale.get_labels(ticks.tolist())
        else:
            labels = [str(x) for x in ticks]

        color_indexes = np.searchsorted(
            self._intervals.boundaries,
            ticks,
            side="left",
        )
        color_indexes = np.clip(color_indexes, 1, len(colors)) - 1
        self.key = pd.DataFrame(
            {
                aesthetic: np.asarray(colors, dtype=object)[color_indexes],
                "label": labels,
                "value": ticks,
            }
        )
        self.bar = pd.DataFrame(
            {
                "color": colors,
                "value": self._intervals.midpoints,
            }
        )

        info = "\n".join(
            [
                str(self.title),
                " ".join(str(x) for x in labels),
                " ".join(str(x) for x in colors),
                self.__class__.__name__,
            ]
        )
        self.hash = hashlib.sha256(info.encode("utf-8")).hexdigest()
        return self

    def _tick_values(self, scale: scale) -> np.ndarray:
        show_limits = self.show_limits
        if show_limits is None:
            show_limits = bool(getattr(scale, "show_limits", False))

        return self._intervals.get_breaks(show_limits)

    def _tick_locations(self, elements: GuideElementsColorbar) -> np.ndarray:
        values = self.key["value"].to_numpy()
        if self.even_steps:
            indexes = np.searchsorted(self._intervals.boundaries, values)
            locations = indexes / (len(self._intervals.boundaries) - 1)
        else:
            locations = rescale(
                values,
                _from=(
                    self._intervals.boundaries[0],
                    self._intervals.boundaries[-1],
                ),
            )
        return np.asarray(locations) * elements.key_height

    def _draw_bar(
        self,
        auxbox: AuxTransformBox,
        colors: Sequence[str],
        alpha: float | None,
        elements: GuideElementsColorbar,
        display: str,
        raster: bool,
    ) -> None:
        # Divide the bar equally by bin count, or preserve each interval's
        # share of the numeric scale range.
        if self.even_steps:
            boundaries = np.linspace(0, 1, len(colors) + 1)
        else:
            boundaries = rescale(
                self._intervals.boundaries,
                _from=(
                    self._intervals.boundaries[0],
                    self._intervals.boundaries[-1],
                ),
            )
        if self.reverse:
            boundaries = 1 - boundaries[::-1]
        add_segmented_colorbar(
            auxbox,
            colors,
            alpha,
            elements,
            boundaries=boundaries,
        )


guide_coloursteps = guide_colorsteps


class GuideElementsColorsteps(GuideElementsColorbar):
    """Theme properties for a stepped-colour guide"""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.guide_kind = "colorbar"
