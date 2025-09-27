"""
Routines to adjust subplot params so that subplots are
nicely fit in the figure. In doing so, only axis labels, tick labels, axes
titles and offsetboxes that are anchored to axes are currently considered.

Internally, this module assumes that the margins (left margin, etc.) which are
differences between `Axes.get_tightbbox` and `Axes.bbox` are independent of
Axes position. This may fail if `Axes.adjustable` is `datalim` as well as
such cases as when left or right margin are affected by xlabel.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from functools import cached_property
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Generator

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.typing import Side


# Note
# Margins around the plot are specified in figure coordinates
# We interpret that value to be a fraction of the width. So along
# the vertical direction we multiply by W/H to get equal space
# in both directions


@dataclass
class GridSpecParams:
    """
    Gridspec Parameters
    """

    left: float
    right: float
    top: float
    bottom: float
    wspace: float
    hspace: float

    @property
    def valid(self) -> bool:
        """
        Return True if the params will create a non-empty area
        """
        return self.top - self.bottom > 0 and self.right - self.left > 0


@dataclass
class _side_space(ABC):
    """
    Base class to for spaces

    A *_space class does the book keeping for all the artists that may
    fall on that side of the panels. The same name may appear in multiple
    side classes (e.g. legend).

    The amount of space for each artist is computed in figure coordinates.
    """

    def __post_init__(self):
        self.side: Side = cast("Side", self.__class__.__name__.split("_")[0])
        """
        Side of the panel(s) that this class applies to
        """
        self._calculate()

    def _calculate(self):
        """
        Calculate the space taken up by each artist
        """

    @property
    def total(self) -> float:
        """
        Total space
        """
        return sum(getattr(self, f.name) for f in fields(self)[1:])

    def sum_upto(self, item: str) -> float:
        """
        Sum of space upto but not including item

        Sums from the edge of the figure i.e. the "plot_margin".
        """

        def _fields_upto(item: str) -> Generator[Field, None, None]:
            for f in fields(self)[1:]:
                if f.name == item:
                    break
                yield f

        return sum(getattr(self, f.name) for f in _fields_upto(item))

    def sum_incl(self, item: str) -> float:
        """
        Sum of space upto and including the item

        Sums from the edge of the figure i.e. the "plot_margin".
        """

        def _fields_upto(item: str) -> Generator[Field, None, None]:
            for f in fields(self)[1:]:
                yield f
                if f.name == item:
                    break

        return sum(getattr(self, f.name) for f in _fields_upto(item))

    @cached_property
    @abstractmethod
    def gs(self) -> p9GridSpec:
        """
        The gridspec of the plot or composition
        """

    @property
    def offset(self) -> float:
        """
        Distance in figure dimensions from the edge of the figure

        Derived classes should override this method

        The space/margin and size consumed by artists is in figure dimensions
        but the exact position is relative to the position of the GridSpec
        within the figure. The offset accounts for the position of the
        GridSpec and allows us to accurately place artists using figure
        coordinates.

        Example of an offset

         Figure
         ----------------------------------------
        |                                        |
        |          Plot GridSpec                 |
        |          --------------------------    |
        | offset  |                          |   |
        |<------->| X                        |   |
        |         |   Panels GridSpec        |   |
        |         |   --------------------   |   |
        |         |  |                    |  |   |
        |         |  |                    |  |   |
        |         |  |                    |  |   |
        |         |  |                    |  |   |
        |         |   --------------------   |   |
        |         |                          |   |
        |          --------------------------    |
        |                                        |
         ----------------------------------------
        """
        return 0

    def to_figure_space(self, rel_value: float) -> float:
        """
        Convert value relative to the gridspec to one in figure space

        The result is meant to be used with transFigure transforms.

        Parameters
        ----------
        rel_value :
            Position relative to the position of the gridspec
        """
        return self.offset + rel_value
