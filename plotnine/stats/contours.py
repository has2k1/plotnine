"""
Utilities for contouring gridded surfaces
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np
import pandas as pd

from ..exceptions import PlotnineError, PlotnineWarning

if TYPE_CHECKING:
    from typing import Any, Callable

    from contourpy import ContourGenerator
    from contourpy._contourpy import FillReturn_OuterOffset

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
        if bins < 1:
            raise PlotnineError("`bins` must be at least 1.")

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
    binwidth = cast("float", binwidth)
    if binwidth <= 0:
        raise PlotnineError("`binwidth` must be greater than 0.")

    return np.asarray(breaks_width(binwidth)(z_range), dtype=float)


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


def band_labels(breaks: FloatArray, precision: int = 3) -> list[str]:
    """
    Label each contour band with its interval

    Use right-closed interval notation and increase precision until every
    break has a distinct label.
    """
    while True:
        edges = [f"{b:.{precision}g}" for b in breaks]
        if len(set(edges)) == len(edges):
            break
        precision += 1

    return [f"({low}, {high}]" for low, high in zip(edges[:-1], edges[1:])]


def contour_lines(
    x: FloatArray,
    y: FloatArray,
    Z: FloatArray,
    breaks: FloatArray,
    group: Any,
) -> pd.DataFrame:
    """
    Trace the contour line at each break

    Assign each disconnected line its own `piece` and `group`, so geoms
    draw separate paths.
    """
    from mizani.bounds import rescale_max

    cgen = _contour_generator(x, y, Z)

    vertices, levels, counts = [], [], []
    for value, lines in zip(breaks, cgen.multi_lines(list(breaks))):
        for line in lines:
            vertices.append(line)
            levels.append(value)
            counts.append(len(line))

    if not vertices:
        warn("No contours were generated.", PlotnineWarning)
        return pd.DataFrame()

    xy = np.concatenate(vertices)
    level = np.repeat(levels, counts)
    return pd.DataFrame(
        {
            "x": xy[:, 0],
            "y": xy[:, 1],
            "level": level,
            "nlevel": rescale_max(level),
            "piece": np.repeat(np.arange(1, len(counts) + 1), counts),
            "group": np.repeat(_group_ids(group, len(counts)), counts),
        }
    )


def contour_bands(
    x: FloatArray,
    y: FloatArray,
    Z: FloatArray,
    breaks: FloatArray,
    group: Any,
) -> pd.DataFrame:
    """
    Trace the boundary of each contour band

    Assign each disconnected region its own `piece` and `group`. Number
    its rings with `subgroup`, starting with the exterior boundary.
    """
    from mizani.bounds import rescale_max

    cgen = _contour_generator(x, y, Z)

    # `FillType.OuterOffset` returns each band as point and offset arrays
    # instead of one of the other supported fill representations.
    filled = cast(
        "list[FillReturn_OuterOffset]", cgen.multi_filled(list(breaks))
    )

    vertices, bands, subgroups, pieces, counts = [], [], [], [], []
    npieces = 0
    for i, (points, offsets) in enumerate(filled):
        for piece_points, piece_offsets in zip(points, offsets):
            npieces += 1
            for ring, (start, end) in enumerate(
                zip(piece_offsets[:-1], piece_offsets[1:])
            ):
                vertices.append(piece_points[start:end])
                bands.append(i)
                subgroups.append(ring)
                pieces.append(npieces)
                counts.append(end - start)

    if not vertices:
        warn("No contour bands were generated.", PlotnineWarning)
        return pd.DataFrame()

    xy = np.concatenate(vertices)
    band = np.repeat(bands, counts)
    labels = band_labels(breaks)
    level_low = breaks[:-1][band]
    level_high = breaks[1:][band]
    ids = _group_ids(group, npieces)

    return pd.DataFrame(
        {
            "x": xy[:, 0],
            "y": xy[:, 1],
            "level": pd.Categorical(
                [labels[i] for i in band], categories=labels, ordered=True
            ),
            "level_low": level_low,
            "level_high": level_high,
            "level_mid": (level_low + level_high) / 2,
            "nlevel": rescale_max(level_high),
            "piece": np.repeat(pieces, counts),
            "subgroup": np.repeat(subgroups, counts),
            "group": np.repeat([ids[p - 1] for p in pieces], counts),
        }
    )


def _contour_generator(
    x: FloatArray, y: FloatArray, Z: FloatArray
) -> ContourGenerator:
    """
    Configure a generator for separate lines and outer offsets
    """
    from contourpy import FillType, LineType, contour_generator

    return contour_generator(
        x,
        y,
        Z,
        name="serial",
        corner_mask=True,
        line_type=LineType.Separate,
        fill_type=FillType.OuterOffset,
    )


def _group_ids(group: Any, n: int) -> list[str]:
    """
    Create one sortable group ID per contour piece

    Zero-pad each piece number so lexical order matches generation order.
    """
    width = len(str(n))
    return [f"{group}-{i:0{width}d}" for i in range(1, n + 1)]


def _signif(value: float) -> float:
    """
    Round to one significant digit
    """
    if value == 0:
        return 1.0
    return round(value, -int(np.floor(np.log10(abs(value)))))
