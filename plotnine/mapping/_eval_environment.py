"""
These are functions that can be called by the user inside the aes()
mapping. This is meant to make it easy to transform column-variables
as easily as is possible in ggplot2.

We only implement the most common functions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from typing import Any, Sequence

__all__ = (
    "factor",
    "reorder",
)


def factor(
    values: Sequence[Any],
    categories: Sequence[Any] | None = None,
    ordered: bool | None = None,
) -> pd.Categorical:
    """
    Turn x in to a categorical (factor) variable

    It is just an alias to `pandas.Categorical`

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
    """
    return pd.Categorical(values, categories=categories, ordered=None)  # pyright: ignore[reportArgumentType]


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
    if len(x) != len(y):
        raise ValueError(f"Lengths are not equal. {len(x)=}, {len(x)=}")
    summary = (
        pd.Series(y)
        .groupby(x, observed=True)
        .apply(fun)
        .sort_values(ascending=ascending)
    )
    cats = summary.index.to_list()
    return pd.Categorical(x, categories=cats)
