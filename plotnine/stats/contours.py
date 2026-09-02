"""
Utilities for contouring gridded surfaces
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np

from ..exceptions import PlotnineError

if TYPE_CHECKING:
    from typing import Any, Callable

    import pandas as pd

    from plotnine.typing import FloatArray, FloatArrayLike


def contour_breaks(
    z_range: tuple[float, float],
    bins: int | None = None,
    binwidth: float | None = None,
    breaks: FloatArrayLike | Callable[..., FloatArrayLike] | None = None,
) -> FloatArray:
    """
    Select contour values for a surface

    Parameters
    ----------
    z_range :
        Minimum and maximum surface values.
    bins :
        Number of contour bands. Takes precedence over `binwidth`.
    binwidth :
        Distance between adjacent contour values.
    breaks :
        Explicit contour values, or a function that receives the range and
        distance between contours. Explicit values override `bins` and
        `binwidth`. A function uses the distance selected by `bins` or
        `binwidth`.
    """
    from mizani.breaks import breaks_extended, breaks_width

    if callable(breaks):
        return np.asarray(breaks(z_range, binwidth), dtype=float)

    if breaks is not None:
        return np.asarray(breaks, dtype=float)

    if bins is None and binwidth is None:
        return np.asarray(breaks_extended(n=10)(z_range), dtype=float)

    if bins is not None:
        # Expand the limits to coarse multiples so every band spans the
        # surface range without clipping it.
        accuracy = _signif(z_range[1] - z_range[0]) / 10
        low = np.floor(z_range[0] / accuracy) * accuracy
        high = np.ceil(z_range[1] / accuracy) * accuracy

        if bins == 1:
            return np.array([low, high])

        _breaks = breaks_width((high - low) / (bins - 1))((low, high))
        # Retry with `bins` intervals if the first spacing yields too few.
        if len(_breaks) < bins + 1:
            _breaks = breaks_width((high - low) / bins)((low, high))
        return np.asarray(_breaks, dtype=float)

    # Reached only when binwidth is set and bins is not
    return np.asarray(
        breaks_width(cast("float", binwidth))(z_range), dtype=float
    )


def xyz_to_grid(
    data: pd.DataFrame,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """
    Arrange tidy x, y, and z values on a grid

    Return sorted x and y coordinates with a matrix containing one `z`
    value per grid cell. Cells absent from the data contain `nan` and are
    not contoured.
    """
    x = np.sort(data["x"].unique())
    y = np.sort(data["y"].unique())
    Z = np.full((len(y), len(x)), np.nan)
    Z[np.searchsorted(y, data["y"]), np.searchsorted(x, data["x"])] = data["z"]
    return x, y, Z


def _signif(value: float) -> float:
    """
    Round to one significant digit
    """
    if value == 0:
        return 1.0
    return round(value, -int(np.floor(np.log10(abs(value)))))
