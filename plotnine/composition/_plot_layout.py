from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from itertools import cycle
from typing import TYPE_CHECKING, Sequence

from plotnine.composition._types import ComposeAddable

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

    def __radd__(self, cmp: Compose) -> Compose:
        """
        Add plot layout to composition
        """
        cmp._plot_layout = copy(self)
        return cmp

    def _setup(self, nrow: int, ncol: int):
        """
        Setup default parameters as they are expected by the layout manager

        - Ensure that the widths and heights are set and normalised to unit sum
        """
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


def repeat(seq: Sequence[float], n: int) -> list[float]:
    """
    Ensure returned sequence has n values, repeat as necessary
    """
    return [val for _, val in zip(range(n), cycle(seq))]


def normalise(seq) -> list[float]:
    total = sum(seq)
    return [x / total for x in seq]
