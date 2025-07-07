from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np
import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.evaluation import after_stat
from .stat import stat

if TYPE_CHECKING:
    from plotnine.typing import FloatArray, FloatArrayLike


# NOTE: Parameter descriptions are in
# statsmodels/nonparametric/kde.py
@document
class stat_density(stat):
    """
    Compute density estimate

    {usage}

    Parameters
    ----------
    {common_parameters}
    kernel : str, default="gaussian"
        Kernel used for density estimation. One of:
        ```python
        "biweight"
        "cosine"
        "cosine2"
        "epanechnikov"
        "gaussian"
        "triangular"
        "triweight"
        "uniform"
        ```
    adjust : float, default=1
        An adjustment factor for the `bw`. Bandwidth becomes
        `bw * adjust`{.py}.
        Adjustment of the bandwidth.
    trim : bool, default=False
        This parameter only matters if you are displaying multiple
        densities in one plot. If `False`{.py}, the default, each
        density is computed on the full range of the data. If
        `True`{.py}, each density is computed over the range of that
        group; this typically means the estimated x values will not
        line-up, and hence you won't be able to stack density values.
    n : int, default=1024
        Number of equally spaced points at which the density is to
        be estimated. For efficient computation, it should be a power
        of two.
    gridsize : int, default=None
        If gridsize is `None`{.py}, `max(len(x), 50)`{.py} is used.
    bw : str | float, default="nrd0"
        The bandwidth to use, If a float is given, it is the bandwidth.
        The options are:

        ```python
        "nrd0"
        "normal_reference"
        "scott"
        "silverman"
        ```

        `nrd0` is a port of `stats::bw.nrd0` in R; it is eqiuvalent
        to `silverman` when there is more than 1 value in a group.
    cut : float, default=3
        Defines the length of the grid past the lowest and highest
        values of `x` so that the kernel goes to zero. The end points
        are `-/+ cut*bw*{min(x) or max(x)}`.
    clip : tuple[float, float], default=(-inf, inf)
        Values in `x` that are outside of the range given by clip are
        dropped. The number of values in `x` is then shortened.
    bounds: tuple[float, float], default=(-inf, inf)
        The domain boundaries of the data. When the domain is finite the
        estimated density will be corrected to remove asymptotic boundary
        effects that are usually biased away from the probability density
        function being estimated.

    See Also
    --------
    plotnine.geom_density : The default `geom` for this `stat`.
    statsmodels.nonparametric.kde.KDEUnivariate
    statsmodels.nonparametric.kde.KDEUnivariate.fit
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    'density'   # density estimate

    'count'     # density * number of points,
                # useful for stacked density plots

    'scaled'    # density estimate, scaled to maximum of 1
    'n'         # Number of observations at a position
    ```


    """
    REQUIRED_AES = {"x"}
    DEFAULT_PARAMS = {
        "geom": "density",
        "position": "stack",
        "na_rm": False,
        "kernel": "gaussian",
        "adjust": 1,
        "trim": False,
        "n": 1024,
        "gridsize": None,
        "bw": "nrd0",
        "cut": 3,
        "clip": (-np.inf, np.inf),
        "bounds": (-np.inf, np.inf),
    }
    DEFAULT_AES = {"y": after_stat("density")}
    CREATES = {"density", "count", "scaled", "n"}

    def setup_params(self, data):
        params = self.params
        lookup = {
            "biweight": "biw",
            "cosine": "cos",
            "cosine2": "cos2",
            "epanechnikov": "epa",
            "gaussian": "gau",
            "triangular": "tri",
            "triweight": "triw",
            "uniform": "uni",
        }

        with suppress(KeyError):
            params["kernel"] = lookup[params["kernel"].lower()]

        if params["kernel"] not in lookup.values():
            msg = (
                f"kernel should be one of {lookup.keys()}. "
                f"You may use the abbreviations {lookup.values()}"
            )
            raise PlotnineError(msg)

    def compute_group(self, data, scales):
        weight = data.get("weight")

        if self.params["trim"]:
            range_x = data["x"].min(), data["x"].max()
        else:
            range_x = scales.x.dimension()

        return compute_density(data["x"], weight, range_x, self.params)


def compute_density(x, weight, range, params):
    """
    Compute density
    """
    import statsmodels.api as sm

    x = np.asarray(x, dtype=float)
    not_nan = ~np.isnan(x)
    x = x[not_nan]
    bw = cast("str | float", params["bw"])
    kernel = params["kernel"]
    bounds = params["bounds"]
    has_bounds = not (np.isneginf(bounds[0]) and np.isposinf(bounds[1]))
    n = len(x)

    if n == 0 or (n == 1 and isinstance(bw, str)):
        if n == 1:
            warn(
                "To compute the density of a group with only one "
                "value set the bandwidth manually. e.g `bw=0.1`",
                PlotnineWarning,
            )
        warn(
            "Groups with fewer than 2 data points have been removed.",
            PlotnineWarning,
        )
        return pd.DataFrame()

    # kde is computed efficiently using fft. But the fft does
    # not support weights and is only available with the
    # gaussian kernel. When weights are relevant we
    # turn off the fft.
    if weight is None:
        if kernel != "gau":
            weight = np.ones(n) / n
    else:
        weight = np.asarray(weight, dtype=float)

    fft = kernel == "gau" and weight is None

    if bw == "nrd0":
        bw = nrd0(x)

    kde = sm.nonparametric.KDEUnivariate(x)
    kde.fit(
        kernel=kernel,
        bw=bw,  # type: ignore
        fft=fft,
        weights=weight,
        adjust=params["adjust"],
        cut=params["cut"],
        gridsize=params["gridsize"],
        clip=params["clip"],
    )

    if has_bounds:
        # kde.support is the grid over which the kernel function is
        # defined and the first and last values of this grid are:
        #
        #     [min(x)-cut*bw, max(x)+cut*bw]
        #
        # i.e. the grid is wider than the ptp range of x.
        # Evaluating values beyond the ptp range helps us calculate a
        # boundary corrections. So we widen the range over which we will
        # evaluate, so that it contains all points supported by the grid.
        x2 = np.linspace(
            kde.support[0],  # pyright: ignore
            kde.support[-1],  # pyright: ignore
            params["n"],
        )
    else:
        x2 = np.linspace(range[0], range[1], params["n"])

    try:
        y = kde.evaluate(x2)
        if np.isscalar(y) and np.isnan(y):
            raise ValueError("kde.evaluate returned nan")
    except ValueError:
        y = []
        for _x in x2:
            result = kde.evaluate(_x)
            if isinstance(result, (float, int)):
                y.append(result)
            else:
                y.append(result[0])

    y = np.asarray(y)

    # Evaluations outside the kernel domain return np.nan,
    # these values and corresponding x2s are dropped.
    # The kernel domain is defined by the values in x, but
    # the evaluated values in x2 could have a much wider range.
    not_nan = ~np.isnan(y)
    x2 = x2[not_nan]
    y = y[not_nan]

    if has_bounds:
        x2, y = fit_density_to_bounds(x2, y, range, bounds)

    return pd.DataFrame(
        {
            "x": x2,
            "density": y,
            "scaled": y / np.max(y) if len(y) else [],
            "count": y * n,
            "n": n,
        }
    )


def nrd0(x: FloatArrayLike) -> float:
    """
    Port of R stats::bw.nrd0

    This is equivalent to statsmodels silverman when x has more than
    1 unique value. It can never give a zero bandwidth.

    Parameters
    ----------
    x : array_like
        Values whose density is to be estimated

    Returns
    -------
    out : float
        Bandwidth of x
    """
    from scipy.stats import iqr

    n = len(x)
    if n < 1:
        raise ValueError(
            "Need at least 2 data points to compute the nrd0 bandwidth."
        )

    std: float = np.std(x, ddof=1)  # pyright: ignore
    std_estimate: float = iqr(x) / 1.349
    low_std = min(std, std_estimate)
    if low_std == 0:
        low_std = std_estimate or np.abs(np.asarray(x)[0]) or 1
    return 0.9 * low_std * (n**-0.2)


def fit_density_to_bounds(
    x: FloatArray,
    y: FloatArray,
    range: tuple[float, float],
    bounds: tuple[float, float],
) -> tuple[FloatArray, FloatArray]:
    """
    Fit calculated density to the given bounds

    Parameters
    ----------
    x :
        Points at which the density is estimated. `x` is expected to
        to include all values of the density grid.
    y :
        Estimated density.
    range :
    bounds :
        Valid boundary (domain) of the x values.

    Returns
    -------
    x_bound :
        Points that fall within the bounds at which the density is
        estimated.
    y_bound :
        Estimated densities at points within the bounds.
    """

    def interpolate(x2: FloatArray) -> FloatArray:
        # Interpolate (linearly) along the density function
        # The values at points beyond (left or right) the original
        # grid (x) are zero.
        return np.interp(x2, x, y, left=0, right=0)

    # The boundary corrections work by:
    # 1. reflecting values outside the bounds so that they fall within
    #    the bounds to give a correction values
    # 2. adding the correction values to the original density
    new_range = max(range[0], bounds[0]), min(range[1], bounds[1])
    x_bound = np.linspace(new_range[0], new_range[1], len(x))
    y_bound = (
        interpolate(x_bound)
        + interpolate(2 * bounds[0] - x_bound)
        + interpolate(2 * bounds[1] - x_bound)
    )
    return x_bound, y_bound
