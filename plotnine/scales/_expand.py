from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from mizani.bounds import expand_range_distinct

from .._utils import ignore_warnings
from ..iapi import range_view

if TYPE_CHECKING:
    from mizani.transforms import trans

    from plotnine.typing import CoordRange


def _expand_range_distinct(
    x: tuple[float, float],
    expand: tuple[float, float] | tuple[float, float, float, float],
) -> tuple[float, float]:
    # Expand ascending and descending order range
    a, b = x
    if a > b:
        b, a = expand_range_distinct((b, a), expand)
    else:
        a, b = expand_range_distinct((a, b), expand)
    return (a, b)


def expand_range(
    x: CoordRange,
    expand: tuple[float, float] | tuple[float, float, float, float],
    trans: trans,
) -> range_view:
    """
    Expand Coordinate Range in coordinate space

    Parameters
    ----------
    x:
        (max, min) in data scale
    expand:
        How to expand
    trans:
        Coordinate transformation
    """
    x_coord_space = tuple(trans.transform(x))
    x_coord = _expand_range_distinct(x_coord_space, expand)  # type: ignore

    with ignore_warnings(RuntimeWarning):
        # Consequences of the runtimewarning (NaNs and infs)
        # are dealt with below
        final_x = trans.inverse(x_coord)

    l0, l1 = x
    f0, f1 = final_x
    final_range = (
        f0 if np.isfinite(f0) else l0,
        f1 if np.isfinite(f1) else l1,
    )

    ranges = range_view(range=final_range, range_coord=x_coord)
    return ranges
