"""
Kernel density estimation

These are ports of the kernel density estimators in statsmodels that
plotnine uses by default, so that they do not require statsmodels
(which requires pandas). They give the same results as
`statsmodels.nonparametric.kde.KDEUnivariate` and
`statsmodels.nonparametric.kernel_density.KDEMultivariate` (for
continuous variables and the normal reference bandwidth).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from plotnine.typing import FloatArray, FloatArrayLike


__all__ = ("KDEUnivariate", "kde_multivariate", "KERNELS")


@dataclass(frozen=True)
class Kernel:
    """
    A univariate kernel
    """

    # Function of the kernel
    shape: Callable[[FloatArray], FloatArray]

    # Support of the kernel. None if it has infinite support.
    domain: tuple[float, float] | None

    # Constant for the normal reference bandwidth
    normal_reference_constant: float


KERNELS: dict[str, Kernel] = {
    "gau": Kernel(
        lambda x: 0.3989422804014327 * np.exp(-(x**2) / 2.0),
        None,
        1.0592238410488122,
    ),
    "epa": Kernel(
        lambda x: 0.75 * (1 - x * x),
        (-1.0, 1.0),
        2.344914356323711,
    ),
    "uni": Kernel(
        lambda x: 0.5 * np.ones(x.shape),
        (-1.0, 1.0),
        1.8431099195302554,
    ),
    "tri": Kernel(
        lambda x: 1 - abs(x),
        (-1.0, 1.0),
        2.5760303892892913,
    ),
    "biw": Kernel(
        lambda x: 0.9375 * (1 - x * x) ** 2,
        (-1.0, 1.0),
        2.777936682192678,
    ),
    "triw": Kernel(
        lambda x: 1.09375 * (1 - x * x) ** 3,
        (-1.0, 1.0),
        3.154480796737293,
    ),
    "cos": Kernel(
        lambda x: 0.7853981633974483 * np.cos(np.pi / 2.0 * x),
        (-1.0, 1.0),
        2.409709532853482,
    ),
    "cos2": Kernel(
        lambda x: 1 + np.cos(2.0 * np.pi * x),
        (-0.5, 0.5),
        5.8137018384962165,
    ),
}


def _select_sigma(x: FloatArray) -> float:
    """
    Robust estimate of the spread of x
    """
    from scipy.stats import scoreatpercentile

    normalize = 1.349
    iqr = scoreatpercentile(x, 75) - scoreatpercentile(x, 25)
    IQR = iqr / normalize
    std_dev = np.std(x, axis=0, ddof=1)
    if IQR > 0:
        return float(np.minimum(std_dev, IQR))
    else:
        return float(std_dev)


def _select_bandwidth(x: FloatArray, bw: str, kernel: Kernel) -> float:
    """
    Bandwidth computed with a rule
    """
    constants = {
        "scott": 1.059,
        "silverman": 0.9,
        "normal_reference": kernel.normal_reference_constant,
    }
    try:
        C = constants[bw.lower()]
    except KeyError as err:
        raise ValueError(f"Bandwidth {bw} not understood") from err

    bandwidth = C * _select_sigma(x) * len(x) ** (-0.2)
    if bandwidth == 0:
        raise RuntimeError(
            "Selected KDE bandwidth is 0. Cannot estimate density. "
            "Either provide the bandwidth during initialization or use "
            "an alternative method."
        )
    return bandwidth


class KDEUnivariate:
    """
    Univariate kernel density estimator

    Parameters
    ----------
    endog :
        The values for which the density estimate is desired.
    """

    # Bandwidth
    bw: float

    # The first and last points of the grid that the kernel is
    # defined over
    support: tuple[float, float]

    def __init__(self, endog: FloatArrayLike):
        self.endog = np.asarray(endog, dtype=float)

    def fit(
        self,
        kernel: str = "gau",
        bw: str | float | Callable[..., float] = "normal_reference",
        fft: bool = True,
        weights: FloatArrayLike | None = None,
        gridsize: int | None = None,
        adjust: float = 1,
        cut: float = 3,
        clip: tuple[float, float] = (-np.inf, np.inf),
    ) -> KDEUnivariate:
        """
        Fit the density estimate

        The parameters are those of
        `statsmodels.nonparametric.kde.KDEUnivariate.fit`. The density
        is evaluated directly (with the kernel), so `fft` and
        `gridsize` do not affect the estimate.
        """
        try:
            self.kernel = KERNELS[kernel]
        except KeyError as err:
            raise ValueError(f"Unknown kernel {kernel!r}") from err

        if fft and kernel != "gau":
            msg = "Only gaussian kernel is available for fft"
            raise NotImplementedError(msg)
        if fft and weights is not None:
            msg = "Weights are not implemented for fft"
            raise NotImplementedError(msg)

        x = self.endog
        x = x[np.logical_and(x > clip[0], x < clip[1])]

        if callable(bw):
            bw = float(bw(x, self.kernel))
        elif isinstance(bw, str):
            bw = _select_bandwidth(x, bw, self.kernel)
        else:
            bw = float(bw)

        bw *= adjust
        self.bw = bw
        self.support = (np.min(x) - cut * bw, np.max(x) + cut * bw)

        if weights is not None:
            weights = np.asarray(weights, dtype=float)
            weights = weights / weights.sum()
        self.weights = weights
        return self

    def evaluate(self, points: FloatArrayLike) -> FloatArray:
        """
        Evaluate the density at the points

        The density at a point that is not within the support of the
        kernel of any of the values is NaN.
        """
        points = np.atleast_1d(np.asarray(points, dtype=float))

        # Evaluate in chunks to limit the memory used
        chunk_size = max(1, 2**22 // max(1, len(self.endog)))
        return np.hstack(
            [
                self._evaluate(points[start : start + chunk_size])
                for start in range(0, len(points), chunk_size)
            ]
            or [np.array([])]
        )

    def _evaluate(self, points: FloatArray) -> FloatArray:
        xs = self.endog
        h = self.bw
        u = (xs[:, None] - points[None, :]) / h

        if self.kernel.domain is None:
            in_domain = None
            k = self.kernel.shape(u)
        else:
            lo, hi = self.kernel.domain
            in_domain = (u >= lo) & (u <= hi)
            k = np.where(in_domain, self.kernel.shape(u), 0)

        if self.weights is not None:
            dens = 1 / h * np.sum(k.T * self.weights, axis=1)
        else:
            dens = 1.0 / (h * len(xs)) * np.sum(k, axis=0)

        if in_domain is not None:
            dens[~in_domain.any(axis=0)] = np.nan
        return dens


def kde_multivariate(
    data: FloatArray,
    data_predict: FloatArray,
    bw: str | FloatArrayLike = "normal_reference",
    var_type: str | None = None,
) -> FloatArray:
    """
    Multivariate kernel density estimate for continuous variables

    Parameters
    ----------
    data :
        Data points used to compute a density estimator. It has
        `n x p` dimensions, representing n points and p variables.
    data_predict :
        Data points at which the density will be estimated. It has
        `m x p` dimensions, representing m points and p variables.
    bw :
        Bandwidth for each variable, or "normal_reference" for the
        normal reference rule of thumb.
    var_type :
        The type of each variable. Only continuous ("c") variables
        are supported.

    Returns
    -------
    :
        Density estimate. It has `m x 1` dimensions.
    """
    data = np.asarray(data, dtype=float)
    data_predict = np.asarray(data_predict, dtype=float)
    nobs, k_vars = data.shape

    if var_type is not None and set(var_type) - {"c"}:
        raise ValueError("Only continuous variables are supported.")

    if isinstance(bw, str):
        if bw != "normal_reference":
            raise ValueError(f"Bandwidth {bw!r} is not supported.")
        bw = 1.06 * np.std(data, axis=0) * nobs ** (-1.0 / (4 + k_vars))
    bw = np.asarray(bw, dtype=float)

    # Evaluate in chunks to limit the memory used
    chunk_size = max(1, 2**22 // max(1, nobs * k_vars))
    result = np.empty(len(data_predict))
    for start in range(0, len(data_predict), chunk_size):
        points = data_predict[start : start + chunk_size]
        kval = (1.0 / np.sqrt(2 * np.pi)) * np.exp(
            -((data[None, :, :] - points[:, None, :]) ** 2) / (bw**2 * 2.0)
        )
        dens = kval.prod(axis=2) / np.prod(bw)
        result[start : start + chunk_size] = dens.sum(axis=1) / nobs
    return result


def can_use_multivariate(kwargs: dict[str, Any]) -> bool:
    """
    Whether kde_multivariate can do what KDEMultivariate is asked to do
    """
    var_type = kwargs.get("var_type", "")
    bw = kwargs.get("bw", "normal_reference")
    other = set(kwargs) - {"var_type", "bw"}
    return (
        not other
        and set(var_type) <= {"c"}
        and (not isinstance(bw, str) or bw == "normal_reference")
    )
