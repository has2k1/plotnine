"""
These are functions that can be called by the user inside the aes()
mapping. This is meant to make it easy to transform column-variables
as easily as is possible in ggplot2.

We only implement the most common functions.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import narwhals as nw
import numpy as np

from .._utils import frame

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

__all__ = (
    "factor",
    "reorder",
)


def factor(
    values: Sequence[Any] | float | str,
    categories: Sequence[Any] | None = None,
    ordered: bool | None = None,
) -> nw.Series[Any]:
    """
    Turn x in to a categorical (factor) variable

    Parameters
    ----------
    values :
        The values of the categorical. If categories are given, values not in
        categories will be replaced with NaN.
    categories :
        The unique categories for this categorical. If not given, the
        categories are assumed to be the unique values of `values`
        (sorted, if possible, otherwise in the order in which they appear).
    ordered :
        Whether or not this categorical is treated as a ordered categorical.
        If True, the resulting categorical will be ordered.
        An ordered categorical respects, when sorted, the order of its
        `categories` attribute (which in turn is the `categories` argument, if
        provided).

    Notes
    -----
    With pandas, the result holds a pandas categorical. With other
    dataframe libraries, the result is an Enum of strings. An Enum
    created with `ordered=False` is treated as unordered (nominal)
    when choosing a scale.
    """
    if isinstance(values, nw.Expr):
        raise TypeError("factor() needs the values, not an expression")

    if isinstance(values, (int, float, str)):
        values = [values]

    return frame.categorical(
        values,
        categories,
        ordered=bool(ordered),
        backend=frame.backend_of(values),
    )


def reorder(x, y, fun=np.median, ascending=True):
    """
    Reorder categorical by sorting along another variable

    It is the order of the categories that changes. Values in x
    are grouped by categories and summarised to determine the
    new order.

    Credit: Copied from plydata

    Parameters
    ----------
    x : list-like
        Values that will make up the categorical.
    y : list-like
        Values by which `c` will be ordered.
    fun : callable
        Summarising function to `x` for each category in `c`.
        Default is the *median*.
    ascending : bool
        If `True`, the `c` is ordered in ascending order of `x`.
    """
    if isinstance(x, nw.Expr) or isinstance(y, nw.Expr):
        raise TypeError("reorder() needs the values, not expressions")

    if len(x) != len(y):
        raise ValueError(f"Lengths are not equal. {len(x)=}, {len(x)=}")

    backend = frame.backend_of(x)
    s = frame.as_series(x)
    xs = s.to_list() if s is not None else list(x)
    # An ordered categorical stays ordered
    ordered = s is not None and frame.is_ordinal(s)
    ys = frame.as_numpy(y)

    groups: dict[Any, list[int]] = defaultdict(list)
    for i, value in enumerate(xs):
        if value is not None and value == value:
            groups[value].append(i)

    summary = {key: fun(ys[idx]) for key, idx in groups.items()}
    # Sort by the categories first so that ties are resolved by them
    keys = sorted(summary, key=frame._sort_key)
    cats = sorted(keys, key=lambda k: summary[k], reverse=not ascending)
    return frame.categorical(x, cats, ordered=ordered, backend=backend)
