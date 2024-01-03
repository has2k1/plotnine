from __future__ import annotations

import typing

from mizani.scale import scale_continuous, scale_discrete

if typing.TYPE_CHECKING:
    from typing import Any, Sequence

    from plotnine.typing import AnyArrayLike, FloatArrayLike, TupleFloat2


class Range:
    """
    Base class for all ranges
    """

    # Holds the range information after training
    range: Any

    def reset(self):
        """
        Reset range
        """
        del self.range

    def train(self, x: Sequence[Any]):
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

    range: TupleFloat2

    def train(self, x: FloatArrayLike):
        """
        Train continuous range
        """
        rng = None if self.is_empty() else self.range
        self.range = scale_continuous.train(x, rng)


class RangeDiscrete(Range):
    """
    Discrete Range
    """

    range: Sequence[Any]

    def train(self, x: AnyArrayLike, drop: bool = False, na_rm: bool = False):
        """
        Train discrete range
        """
        rng = None if self.is_empty() else self.range
        self.range = scale_discrete.train(x, rng, drop, na_rm=na_rm)
