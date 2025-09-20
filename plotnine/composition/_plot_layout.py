from __future__ import annotations

from dataclasses import dataclass
from itertools import cycle
from typing import TYPE_CHECKING, Sequence, cast

from ..composition._types import ComposeAddable

if TYPE_CHECKING:
    from ._compose import Compose


@dataclass(kw_only=True)
class plot_layout(ComposeAddable):
    """
    Customise the layout of plots in a composition
    """

    widths: Sequence[float] | None = None
    """
    Relative widths of each column
    """

    heights: Sequence[float] | None = None
    """
    Relative heights of each column
    """

    nrow: int | None = None
    """
    Number of rows
    """

    ncol: int | None = None
    """
    Number of columns
    """

    def __radd__(self, cmp: Compose) -> Compose:
        """
        Add plot layout to composition
        """
        cmp.layout = self
        return cmp

    def _setup(self):
        """
        Setup default parameters as they are expected by the layout manager

        - Ensure that the widths and heights are set and normalised to unit sum
        """
        nrow = cast("int", self.nrow)
        ncol = cast("int", self.ncol)
        ws, hs = self.widths, self.heights
        if ws is None:
            ws = (1 / ncol,) * ncol
        elif len(ws) != ncol:
            ws = repeat(ws, ncol)

        if hs is None:
            hs = (1 / nrow,) * nrow
        elif len(hs) != nrow:
            hs = repeat(hs, nrow)

        self.widths = normalise(ws)
        self.heights = normalise(hs)

    def update(self, other: plot_layout):
        """
        Update this layout with the contents of other
        """
        if other.widths:
            self.widths = other.widths
        if other.heights:
            self.heights = other.heights
        if other.ncol:
            self.ncol = other.ncol
        if other.nrow:
            self.nrow = other.nrow


def repeat(seq: Sequence[float], n: int) -> list[float]:
    """
    Ensure returned sequence has n values, repeat as necessary
    """
    return [val for _, val in zip(range(n), cycle(seq))]


def normalise(seq: Sequence[float]) -> list[float]:
    """
    Normalise seq so that the mean is 1
    """
    mean = sum(seq) / len(seq)
    if mean == 0:
        raise ValueError("Cannot rescale: mean is zero")
    return [x / mean for x in seq]
