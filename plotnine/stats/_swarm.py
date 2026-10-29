"""
Shared swarm layout calculations

Estimate density, scale widths, position points, and mirror swarm styles
for `stat_sina` and `stat_beeswarm`.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from .._utils import (
    array_kind,
    frame,
    nextafter_range,
    normalise_random_state,
    resolution,
)
from ..exceptions import PlotnineError
from ..mapping.aes import has_groups
from .binning import breaks_from_bins, breaks_from_binwidth, cut
from .stat_density import compute_density

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotnine._utils.frame import DataFrame
    from plotnine.iapi import pos_scales
    from plotnine.typing import FloatArray, IntArray

__all__ = (
    "van_der_corput",
    "check_x_is_discrete",
    "setup_swarm_params",
    "estimate_group_density",
    "swarm_widths",
    "pseudorandom_offset",
    "quasirandom_offset",
    "smiley_offset",
    "frowney_offset",
    "spread_offset",
    "finish_swarm_layer",
)


def van_der_corput(n: int) -> np.ndarray:
    """
    Van der Corput low-discrepancy sequence

    Rotate the sequence so the value nearest 0.5 comes first. This
    places the point with the lowest `y` value at the swarm centre.

    Parameters
    ----------
    n :
        Length of the sequence.
    """
    if n <= 0:
        return np.array([])
    indices = np.arange(n, dtype=np.uint32)
    bytes_ = indices.astype(">u4").view(np.uint8).reshape(n, 4)
    vdc = np.unpackbits(bytes_, axis=1) @ np.exp2(-np.arange(32, 0, -1))
    start = int(np.argmin(np.abs(vdc - 0.5)))
    return np.roll(vdc, -start)


def check_x_is_discrete(data: DataFrame) -> DataFrame:
    """
    Reject ungrouped continuous `x` values
    """
    if (
        array_kind.continuous(data["x"])
        and not has_groups(data)
        and data["x"].n_unique() > 1
    ):
        raise TypeError(
            "Continuous x aesthetic -- did you forget aes(group=...)?"
        )
    return data


def setup_swarm_params(params: dict[str, Any], data: DataFrame):
    """
    Resolve swarm parameters and configure density estimation
    """
    if params["maxwidth"] is None:
        params["maxwidth"] = resolution(data["x"], False) * 0.9

    if params["binwidth"] is None and params["bins"] is None:
        params["bins"] = 50

    params["random_state"] = normalise_random_state(params["random_state"])

    # Swarm density estimates require a Gaussian kernel without boundary
    # extension or clipping.
    params["kernel"] = "gau"
    params["cut"] = 0
    params["gridsize"] = None
    params["clip"] = (-np.inf, np.inf)
    params["bounds"] = (-np.inf, np.inf)
    params["n"] = 512


def estimate_group_density(
    data: DataFrame,
    scales: pos_scales,
    params: dict[str, Any],
    few_rows_density: float,
) -> DataFrame:
    """
    Estimate the density or bin count for each row in a group

    Parameters
    ----------
    few_rows_density :
        Density for groups with fewer than three rows, which cannot
        support an estimate. Use `0` for `stat_sina` and `1` for
        `stat_beeswarm`. See kata issue `zbne`.
    """
    binwidth = params["binwidth"]
    maxwidth = params["maxwidth"]
    bin_limit = params["bin_limit"]
    weight = None

    if len(data) == 0:
        return frame.empty_like(data)

    y = frame.to_numpy(data["y"])
    if len(data) < 3:
        density, scaled = few_rows_density, 1
    elif len(np.unique(y)) < 2:
        density, scaled = 1, 1
    elif params["method"] == "density":
        from scipy.interpolate import interp1d

        # Interpolate the density estimate at each observed `y` value.
        range_y = y.min(), y.max()
        dens = compute_density(y, weight, range_y, params)
        dens_y = frame.to_numpy(dens["density"])
        densf = interp1d(
            frame.to_numpy(dens["x"]),
            dens_y,
            bounds_error=False,
            fill_value="extrapolate",  # pyright: ignore
        )
        density = densf(y)
        scaled = density / dens_y.max()
    else:
        expanded_y_range = nextafter_range(scales.y.dimension())
        if binwidth is not None:
            bins = breaks_from_binwidth(expanded_y_range, binwidth)
        else:
            bins = breaks_from_bins(expanded_y_range, params["bins"])

        # Count observations within each `y` bin.
        bin_index = cut(y, bins, include_lowest=True)
        _, inverse, counts = np.unique(
            bin_index, return_inverse=True, return_counts=True
        )
        density = counts[inverse].astype(float)
        density[density <= bin_limit] = 0
        scaled = density / density.max()

    # Preserve the relative span of groups with multiple `x` values.
    x = frame.to_numpy(data["x"])
    multiple_x = len(np.unique(x)) > 1
    width = np.ptp(x) * maxwidth if multiple_x else maxwidth

    return frame.assign(
        data,
        density=density,
        scaled=scaled,
        width=width,
        n=len(data),
        x=np.mean([x.max(), x.min()]),
    )


def swarm_widths(data: DataFrame, scale: str, width_col: str) -> DataFrame:
    """
    Scale each row's density to a fraction of `maxwidth`

    Parameters
    ----------
    width_col :
        Column that receives the scaled width fraction.
    """
    density = frame.to_numpy(data["density"]).astype(float)
    if scale == "area":
        width = density / density.max()
    elif scale == "count":
        n = frame.to_numpy(data["n"])
        width = density / density.max() * n / n.max()
    elif scale == "width":
        width = frame.to_numpy(data["scaled"]).astype(float)
    else:
        msg = "Unknown scale value '{}'"
        raise PlotnineError(msg.format(scale))

    width[~np.isfinite(width)] = 0
    return frame.assign(data, **{width_col: width})


def pseudorandom_offset(
    data: DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> FloatArray:
    """
    Draw each row's `x` offset from uniform noise

    Parameters
    ----------
    params :
        Resolved stat parameters. This function reads only
        `random_state`.
    """
    random_state = params["random_state"]
    if random_state is None:
        random_state = np.random
    return (
        frame.to_numpy(data[width_col])
        * random_state.uniform(-1, 1, len(data))
        * maxwidth
        / 2
    )


def quasirandom_offset(
    data: DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> FloatArray:
    """
    Derive each row's `x` offset from its rank

    Rank each group's points by `y`, then assign the corresponding
    `van_der_corput` values. Points close in `y` therefore remain close
    in `x`, unlike `pseudorandom_offset`'s independent random offsets.
    The shared offset signature requires `params`, but this calculation
    does not use it.
    """
    y = frame.to_numpy(data["y"])
    width = frame.to_numpy(data[width_col])
    x_diff = np.zeros(len(data))
    for idx in _group_rows(data):
        y_rank = np.argsort(np.argsort(y[idx]))
        seq = van_der_corput(len(idx))
        x_diff[idx] = (seq[y_rank] - 0.5) * maxwidth * width[idx]
    return x_diff


def _extremes_bin_index(y: FloatArray, params: dict[str, Any]) -> FloatArray:
    """
    Assign points to `y` neighbourhoods for extreme-value ranking

    Use a dedicated density estimate sized to the group. The stat's
    `method`, `bins`, and `binwidth` parameters affect width scaling but
    not these neighbourhoods. Assign groups with fewer than three
    points or one unique `y` value to a single neighbourhood.
    """
    n = len(y)
    if n < 3 or len(np.unique(y)) < 2:
        return np.zeros(n)
    density_params = {**params, "n": max(2, math.ceil(n / 5))}
    dens = compute_density(y, None, (y.min(), y.max()), density_params)
    return cut(y, frame.to_numpy(dens["x"]), include_lowest=True)


def _alternate_extremes(y: np.ndarray, ascending: bool) -> np.ndarray:
    """
    Map ordered values to alternating positions across a neighbourhood

    Return each point's position in `[0, 1]`. Place the two most extreme
    points, ordered by `y` when `ascending` and by `-y` otherwise, at
    opposite ends and the least extreme point at the centre. Preserve
    input order for ties, so equal values produce the same result in
    either direction.
    """
    n = len(y)
    if n == 1:
        return np.array([0.5])
    order = y if ascending else -y
    rank1 = np.argsort(np.argsort(order, kind="stable")) + 1
    signed = np.where(rank1 % 2 == 1, -rank1, rank1)
    return np.argsort(np.argsort(signed, kind="stable")) / (n - 1)


def _extremes_offset(
    data: DataFrame,
    maxwidth: float,
    width_col: str,
    params: dict[str, Any],
    ascending: bool,
) -> FloatArray:
    """
    Place neighbourhood values towards the swarm's centre or edges

    Divide each group into `y` neighbourhoods, rank values within each
    neighbourhood, and alternate their positions across the swarm.

    Parameters
    ----------
    ascending :
        If `True`, place the most extreme values near the edges. If
        `False`, place them near the centre.
    """
    y = frame.to_numpy(data["y"])
    width = frame.to_numpy(data[width_col])
    x_diff = np.zeros(len(data))
    for idx in _group_rows(data):
        bin_index = _extremes_bin_index(y[idx], params)
        prop = np.full(len(idx), 0.5)
        for b in np.unique(bin_index[~np.isnan(bin_index)]):
            cell = bin_index == b
            prop[cell] = _alternate_extremes(y[idx][cell], ascending)
        x_diff[idx] = (prop - 0.5) * maxwidth * width[idx]
    return x_diff


def smiley_offset(
    data: DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> FloatArray:
    """
    Place each `y` neighbourhood's most extreme points at the edges
    """
    return _extremes_offset(data, maxwidth, width_col, params, ascending=True)


def frowney_offset(
    data: DataFrame, maxwidth: float, width_col: str, params
) -> FloatArray:
    """
    Place each `y` neighbourhood's most extreme points near the centre
    """
    return _extremes_offset(data, maxwidth, width_col, params, ascending=False)


_SPREAD_OFFSETS: dict[str, Callable[..., FloatArray]] = {
    "pseudorandom": pseudorandom_offset,
    "quasirandom": quasirandom_offset,
    "smiley": smiley_offset,
    "frowney": frowney_offset,
}


def spread_offset(
    data: DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> FloatArray:
    """
    Calculate offsets with the selected spread strategy
    """
    spread = params["spread"]
    try:
        offset_fn = _SPREAD_OFFSETS[spread]
    except KeyError:
        msg = "Unknown spread value {!r}. Choose one of {}"
        raise PlotnineError(
            msg.format(spread, sorted(_SPREAD_OFFSETS))
        ) from None
    return offset_fn(data, maxwidth, width_col, params)


def finish_swarm_layer(data: DataFrame, style: str) -> DataFrame:
    """
    Rescale `x` after position adjustment, then apply the swarm style

    A position adjustment such as dodging changes the `xmin` to `xmax`
    span after panel computation. Scale `x_diff` by the change before
    adding it to `x`.
    """
    x_mean = cast("FloatArray", frame.to_numpy(data["x"]))
    x_mod = frame.to_numpy((data["xmax"] - data["xmin"]) / data["width"])
    x = x_mean + frame.to_numpy(data["x_diff"]) * x_mod
    group = cast("IntArray", frame.to_numpy(data["group"]))
    even = group % 2 == 0
    new_x = x.copy()

    def mirror_x(bool_idx):
        """
        Mirror selected `x` positions across their original centres
        """
        new_x[bool_idx] = 2 * x_mean[bool_idx] - x[bool_idx]

    match style:
        case "left":
            mirror_x(x_mean < x)
        case "right":
            mirror_x(x < x_mean)
        case "left-right":
            mirror_x(even & (x < x_mean) | ~even & (x_mean < x))
        case "right-left":
            mirror_x(even & (x_mean < x) | ~even & (x < x_mean))

    return frame.assign(data, x=new_x)


def _group_rows(data: DataFrame) -> list[IntArray]:
    """
    The positions of the rows in each group, in order of appearance
    """
    groups = frame.to_numpy(data["group"])
    _, first = np.unique(groups, return_index=True)
    return [np.flatnonzero(groups == groups[i]) for i in np.sort(first)]
