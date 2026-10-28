from __future__ import annotations

import typing

import numpy as np
from mizani.scale import scale_continuous

from .._utils import frame, multitype_sort

if typing.TYPE_CHECKING:
    from typing import Any, Sequence

    from plotnine.typing import AnyArrayLike, FloatArrayLike


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

    range: tuple[float, float]

    def train(self, x: FloatArrayLike):
        """
        Train continuous range
        """
        rng = None if self.is_empty() else self.range
        self.range = scale_continuous.train(frame.as_numpy(x), rng)


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
        self.range = train_discrete(x, rng, drop, na_rm=na_rm)


def train_discrete(
    new_data: Any,
    old: Sequence[Any] | None = None,
    drop: bool = False,
    na_rm: bool = False,
) -> list[Any]:
    """
    Train a discrete scale

    Parameters
    ----------
    new_data : array_like | series
        New values
    old : array_like
        Old range. List of values known to the scale.
    drop : bool
        Whether to drop(not include) unused categories
    na_rm : bool
        If ``True``, remove missing values. Missing values
        are either ``NaN`` or ``None``.

    Returns
    -------
    out : list
        Values covered by the scale
    """
    old = [] if old is None else list(old)

    if not len(new_data):
        return old

    old_set = set(old)
    s = frame.as_series(new_data)

    if s is not None and frame.is_categorical(s):
        categories = frame.levels(s)
        has_na = bool(frame.is_missing(s).any())
        if drop:
            present = set(s.drop_nulls().to_list())
            new = [c for c in categories if c in present]
        else:
            new = categories

        all_set = old_set | set(new)
        cat_set = set(categories)
        ordered_cats = categories + [c for c in old if c not in cat_set]
        limits = [c for c in ordered_cats if c in all_set]
    else:
        values = frame.to_numpy(s) if s is not None else new_data
        if not isinstance(values, np.ndarray):
            arr = np.empty(len(values), dtype=object)
            arr[:] = list(values)
            values = arr

        if values.dtype.kind not in "ObUS":
            raise TypeError("Continuous value supplied to discrete scale")

        nan_bool_idx = frame.isna(values)
        has_na = bool(nan_bool_idx.any())
        values = values[~nan_bool_idx]

        try:
            new = list(np.unique(values))
        except TypeError:
            new = multitype_sort(set(values))

        limits = old + [i for i in new if (i not in old_set)]

    # Add nan if required
    has_na_limits = bool(frame.isna(limits).any()) if limits else False
    if not has_na_limits and not na_rm and has_na:
        limits.append(np.nan)
    return limits
