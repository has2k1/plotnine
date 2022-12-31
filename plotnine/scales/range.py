from __future__ import annotations

import typing

from mizani.scale import scale_continuous, scale_discrete

if typing.TYPE_CHECKING:
    from typing import Any, Sequence


class Range:
    """
    Base class for all ranges
    """
    #: Holds the range information after training
    range: tuple[float, float]

    def reset(self) -> None:
        """
        Reset range
        """
        del self.range

    def train(self, x: Sequence[Any]) -> None:
        """
        Train range
        """
        raise NotImplementedError("Not Implemented.")

    def is_empty(self) -> bool:
        """
        Whether there is range information
        """
        return not hasattr(self, "range")


class RangeContinuous(Range):
    """
    Continuous Range
    """

    def train(self, x: Sequence[Any]) -> None:
        """
        Train continuous range
        """
        rng = None if self.is_empty() else self.range
        self.range = scale_continuous.train(x, rng)


class RangeDiscrete(Range):
    """
    Discrete Range
    """

    def train(
        self,
        x: Sequence[Any],
        drop: bool = False,
        na_rm: bool = False
    ) -> None:
        """
        Train discrete range
        """
        rng = None if self.is_empty() else self.range
        self.range = scale_discrete.train(x, rng, drop, na_rm=na_rm)
