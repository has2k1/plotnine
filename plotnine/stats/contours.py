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

    from plotnine.typing import FloatArray, FloatArrayLike, IntArray


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
    break has a distinct label. Raise when equal floating-point values
    remain indistinguishable at the maximum round-trip precision.
    """
    # Seventeen significant digits round-trip any float64. Values that
    # still share a label are equal at the available precision.
    max_precision = 17
    while True:
        edges = [f"{b:.{precision}g}" for b in breaks]
        if len(set(edges)) == len(edges):
            break
        if precision >= max_precision:
            raise PlotnineError(
                "Duplicate contour breaks cannot be labelled as distinct "
                "bands."
            )
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
        return pd.DataFrame(
            {
                "x": pd.Series(dtype=float),
                "y": pd.Series(dtype=float),
                "level": pd.Series(dtype=float),
                "nlevel": pd.Series(dtype=float),
                "piece": pd.Series(dtype=int),
                "group": pd.Series(dtype=object),
            }
        )

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

    labels = band_labels(breaks)
    cgen = _contour_generator(x, y, Z)

    # `FillType.OuterOffset` returns parallel lists containing one point
    # array and one offset array per piece.
    filled = cast(
        "list[tuple[list[FloatArray], list[IntArray]]]",
        cgen.multi_filled(list(breaks)),
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
        return pd.DataFrame(
            {
                "x": pd.Series(dtype=float),
                "y": pd.Series(dtype=float),
                "level": pd.Categorical([], categories=labels, ordered=True),
                "level_low": pd.Series(dtype=float),
                "level_high": pd.Series(dtype=float),
                "level_mid": pd.Series(dtype=float),
                "nlevel": pd.Series(dtype=float),
                "piece": pd.Series(dtype=int),
                "subgroup": pd.Series(dtype=int),
                "group": pd.Series(dtype=object),
            }
        )

    xy = np.concatenate(vertices)
    band = np.repeat(bands, counts)
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


def drop_duplicate_xy(data: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate coordinates and report how many were dropped

    A grid contains one `z` value per coordinate. Keep the last duplicate,
    matching the order in which the grid cells are populated.
    """
    columns = [c for c in ("x", "y", "group", "PANEL") if c in data]
    if not columns:
        return data

    duplicated = data.duplicated(subset=columns, keep="last")
    if not duplicated.any():
        return data

    warn(
        "Contour data contains duplicate x and y coordinates. "
        f"Duplicate coordinates were removed from {duplicated.sum()} rows.",
        PlotnineWarning,
    )
    return data.loc[~duplicated]


def estimate_grid_angle(x: FloatArrayLike, y: FloatArrayLike) -> float:
    """
    Estimate a grid's rotation from the coordinate axes

    Use raw, unrounded coordinates. Prior rounding can split one neighbour
    angle into several floating-point values and hide the dominant grid
    direction. Return zero for an axis-aligned grid.
    """
    x, y = np.asarray(x), np.asarray(y)
    if len(x) < 3:
        return 0.0

    # The most common angle between neighbouring points follows a grid
    # row. Round only while finding that mode. Return the full-precision
    # mean so the inverse rotation keeps distant points aligned.
    raw_angles = np.arctan2(np.diff(y[:20]), np.diff(x[:20]))
    rounded = np.round(raw_angles, 9)
    values, counts = np.unique(rounded, return_counts=True)
    i = counts.argmax()

    if counts[i] / counts.sum() < 0.5:
        # No angle dominates, so the points are not in grid order. Fall
        # back to the longest edge of the convex hull.
        angle = _longest_hull_edge_angle(x, y)
    else:
        angle = float(np.mean(raw_angles[rounded == values[i]]))

    quarter_turns = np.array([-1, -0.5, 0, 0.5, 1]) * np.pi
    if (np.abs(angle - quarter_turns) < np.sqrt(np.finfo(float).eps)).any():
        return 0.0
    return angle


def rotate_xy(
    x: FloatArrayLike, y: FloatArrayLike, angle: float
) -> tuple[FloatArray, FloatArray]:
    """
    Rotate coordinates about the origin
    """
    x, y = np.asarray(x), np.asarray(y)
    if angle == 0:
        return x, y

    cos, sin = np.cos(angle), np.sin(angle)
    # Round away the rounding error, so that points on one grid line
    # still share a value once rotated. `angle` is often
    # `estimate_grid_angle`'s output rather than an exact value: it is
    # off by several dozen of its own representable steps, growing
    # larger still, roughly by float64 epsilon times the grid's
    # distance from the origin over its own spacing, for a grid that
    # sits far from the origin relative to that spacing. The budget
    # below has to absorb that angle error times the grid's extent,
    # the distance between its farthest-apart points, not how far any
    # single point sits from the origin, which is why it is wider than
    # a single rotation's own noise needs.
    return (
        _zapsmall(cos * x - sin * y),
        _zapsmall(sin * x + cos * y),
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


def _longest_hull_edge_angle(x: FloatArray, y: FloatArray) -> float:
    """
    Measure the angle of the longest convex-hull edge
    """
    from scipy.spatial import ConvexHull, QhullError

    try:
        hull = ConvexHull(np.column_stack([x, y]))
    except QhullError:
        # The points are collinear or degenerate; there is nothing to rotate
        return 0.0

    vertices = np.append(hull.vertices, hull.vertices[0])
    dx = np.diff(x[vertices])
    dy = np.diff(y[vertices])
    i = np.argmax(np.hypot(dx, dy))
    return float(np.arctan2(dy[i], dx[i]))


# 11 is tight, not cautious. At 12, `rotate_xy`'s own re-alignment
# error already exceeds the rounding step on over half of a sample of
# 300 `faithfuld` grids rotated to random angles. At 10, every one of
# those rotations still re-grids cleanly, but only by discarding
# precision that 11 does not need to give up.
def _zapsmall(value: FloatArray, digits: int = 11) -> FloatArray:
    """
    Round values relative to their largest magnitude

    Return an empty array unchanged because the magnitude reduction has no
    identity for empty input.
    """
    if value.size == 0:
        return value
    largest = np.max(np.abs(value))
    if largest == 0 or not np.isfinite(largest):
        return np.round(value, digits)
    return np.round(value, max(0, int(digits - np.ceil(np.log10(largest)))))
