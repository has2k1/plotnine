"""
Shared swarm layout calculations

Estimate density, scale widths, position points, and mirror swarm styles
for `stat_sina` and `stat_beeswarm`.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Callable, cast

import numpy as np
import pandas as pd

from .._utils import (
    array_kind,
    nextafter_range,
    normalise_random_state,
    resolution,
)
from ..exceptions import PlotnineError
from ..mapping.aes import has_groups
from .binning import breaks_from_bins, breaks_from_binwidth
from .stat_density import compute_density

if TYPE_CHECKING:
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


def check_x_is_discrete(data: pd.DataFrame) -> pd.DataFrame:
    """
    Reject ungrouped continuous `x` values
    """
    if (
        array_kind.continuous(data["x"])
        and not has_groups(data)
        and (data["x"] != data["x"].iloc[0]).any()
    ):
        raise TypeError(
            "Continuous x aesthetic -- did you forget aes(group=...)?"
        )
    return data


def setup_swarm_params(params: dict[str, Any], data: pd.DataFrame):
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
    data: pd.DataFrame,
    scales: pos_scales,
    params: dict[str, Any],
    few_rows_density: float,
) -> pd.DataFrame:
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
    y = data["y"]

    if len(data) == 0:
        return pd.DataFrame()
    elif len(data) < 3:
        data["density"] = few_rows_density
        data["scaled"] = 1
    elif len(np.unique(y)) < 2:
        data["density"] = 1
        data["scaled"] = 1
    elif params["method"] == "density":
        from scipy.interpolate import interp1d

        # Interpolate the density estimate at each observed `y` value.
        range_y = y.min(), y.max()
        dens = compute_density(y, weight, range_y, params)
        densf = interp1d(
            dens["x"],
            dens["density"],
            bounds_error=False,
            fill_value="extrapolate",  # pyright: ignore
        )
        data["density"] = densf(y)
        data["scaled"] = data["density"] / dens["density"].max()
    else:
        expanded_y_range = nextafter_range(scales.y.dimension())
        if binwidth is not None:
            bins = breaks_from_binwidth(expanded_y_range, binwidth)
        else:
            bins = breaks_from_bins(expanded_y_range, params["bins"])

        # Count observations within each `y` bin.
        bin_index = pd.cut(y, bins, include_lowest=True, labels=False)  # pyright: ignore[reportCallIssue,reportArgumentType]
        data["density"] = (
            pd.Series(bin_index)
            .groupby(bin_index)
            .apply(len)[bin_index]
            .to_numpy()
        )
        data.loc[data["density"] <= bin_limit, "density"] = 0
        data["scaled"] = data["density"] / data["density"].max()

    # Preserve the relative span of groups with multiple `x` values.
    if len(data["x"].unique()) > 1:
        width = np.ptp(data["x"]) * maxwidth
    else:
        width = maxwidth

    data["width"] = width
    data["n"] = len(data)
    data["x"] = np.mean([data["x"].max(), data["x"].min()])

    return data


def swarm_widths(data: pd.DataFrame, scale: str, width_col: str):
    """
    Scale each row's density to a fraction of `maxwidth`

    Parameters
    ----------
    width_col :
        Column that receives the scaled width fraction.
    """
    if scale == "area":
        data[width_col] = data["density"] / data["density"].max()
    elif scale == "count":
        data[width_col] = (
            data["density"]
            / data["density"].max()
            * data["n"]
            / data["n"].max()
        )
    elif scale == "width":
        data[width_col] = data["scaled"]
    else:
        msg = "Unknown scale value '{}'"
        raise PlotnineError(msg.format(scale))

    is_infinite = ~np.isfinite(data[width_col])
    if is_infinite.any():
        data.loc[is_infinite, width_col] = 0


def pseudorandom_offset(
    data: pd.DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> pd.Series:
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
    # Lead with the indexed widths so multiplication preserves a Series.
    return (
        data[width_col] * random_state.uniform(-1, 1, len(data)) * maxwidth / 2
    )


def quasirandom_offset(
    data: pd.DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> pd.Series:
    """
    Derive each row's `x` offset from its rank

    Rank each group's points by `y`, then assign the corresponding
    `van_der_corput` values. Points close in `y` therefore remain close
    in `x`, unlike `pseudorandom_offset`'s independent random offsets.
    The shared offset signature requires `params`, but this calculation
    does not use it.
    """
    x_diff = pd.Series(0.0, index=data.index)
    for _, grp in data.groupby("group", sort=False):
        y_rank = np.argsort(np.argsort(grp["y"].to_numpy()))
        seq = van_der_corput(len(grp))
        x_diff.loc[grp.index] = (
            (seq[y_rank] - 0.5) * maxwidth * grp[width_col].to_numpy()
        )
    return x_diff


def _extremes_bin_index(y: pd.Series, params: dict[str, Any]) -> np.ndarray:
    """
    Assign points to `y` neighbourhoods for extreme-value ranking

    Use a dedicated density estimate sized to the group. The stat's
    `method`, `bins`, and `binwidth` parameters affect width scaling but
    not these neighbourhoods.
    """
    n = len(y)
    if n < 3 or len(np.unique(y)) < 2:
        return np.zeros(n, dtype=int)
    density_params = {**params, "n": max(2, math.ceil(n / 5))}
    dens = compute_density(y, None, (y.min(), y.max()), density_params)
    return pd.cut(y, dens["x"], include_lowest=True, labels=False).to_numpy()


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
    data: pd.DataFrame,
    maxwidth: float,
    width_col: str,
    params: dict[str, Any],
    ascending: bool,
) -> pd.Series:
    x_diff = pd.Series(0.0, index=data.index)
    for _, grp in data.groupby("group", sort=False):
        bin_index = _extremes_bin_index(grp["y"], params)
        prop = pd.Series(0.5, index=grp.index)
        for _, cell in grp.groupby(bin_index):
            prop.loc[cell.index] = _alternate_extremes(
                cell["y"].to_numpy(), ascending
            )
        x_diff.loc[grp.index] = (
            (prop - 0.5) * maxwidth * grp[width_col].to_numpy()
        )
    return x_diff


def smiley_offset(
    data: pd.DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> pd.Series:
    """
    Place each `y` neighbourhood's most extreme points at the edges
    """
    return _extremes_offset(data, maxwidth, width_col, params, ascending=True)


def frowney_offset(
    data: pd.DataFrame, maxwidth: float, width_col: str, params
) -> pd.Series:
    """
    Place each `y` neighbourhood's most extreme points near the centre
    """
    return _extremes_offset(data, maxwidth, width_col, params, ascending=False)


_SPREAD_OFFSETS: dict[str, Callable[..., pd.Series]] = {
    "pseudorandom": pseudorandom_offset,
    "quasirandom": quasirandom_offset,
    "smiley": smiley_offset,
    "frowney": frowney_offset,
}


def spread_offset(
    data: pd.DataFrame, maxwidth: float, width_col: str, params: dict[str, Any]
) -> pd.Series:
    """
    Calculate offsets with the selected spread strategy
    """
    try:
        offset_fn = _SPREAD_OFFSETS[params["spread"]]
    except KeyError:
        msg = "Unknown spread value {!r}"
        raise PlotnineError(msg.format(params["spread"])) from None
    return offset_fn(data, maxwidth, width_col, params)


def finish_swarm_layer(data: pd.DataFrame, style: str) -> pd.DataFrame:
    """
    Rescale `x` after position adjustment, then apply the swarm style

    A position adjustment such as dodging changes the `xmin` to `xmax`
    span after panel computation. Scale `x_diff` by the change before
    adding it to `x`.
    """
    x_mean = cast("FloatArray", data["x"].to_numpy())
    x_mod = (data["xmax"] - data["xmin"]) / data["width"]
    data["x"] = data["x"] + data["x_diff"] * x_mod
    group = cast("IntArray", data["group"].to_numpy())
    x = cast("FloatArray", data["x"].to_numpy())
    even = group % 2 == 0

    def mirror_x(bool_idx):
        """
        Mirror selected `x` positions across their original centres
        """
        data.loc[bool_idx, "x"] = 2 * x_mean[bool_idx] - x[bool_idx]

    match style:
        case "left":
            mirror_x(x_mean < x)
        case "right":
            mirror_x(x < x_mean)
        case "left-right":
            mirror_x(even & (x < x_mean) | ~even & (x_mean < x))
        case "right-left":
            mirror_x(even & (x_mean < x) | ~even & (x < x_mean))

    return data
