"""
Kernel Density Functions

These functions make it easy to integrate stats that compute
kernel densities with the wider scientific python ecosystem.

Credit: Jake VanderPlas for the original kde_* functions
https://jakevdp.github.io/blog/2013/12/01/kernel-density-estimation/
"""

from __future__ import annotations

import typing

import numpy as np

from .._utils import array_kind

if typing.TYPE_CHECKING:
    from typing import Any, Literal

    import pandas as pd

    from plotnine.typing import FloatArray


def kde_scipy(data: FloatArray, grid: FloatArray, **kwargs: Any) -> FloatArray:
    """
    Kernel Density Estimation with Scipy

    Parameters
    ----------
    data :
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid :
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    from scipy.stats import gaussian_kde

    kde = gaussian_kde(data.T, **kwargs)
    return kde.evaluate(grid.T)


def kde_statsmodels_u(
    data: FloatArray, grid: FloatArray, **kwargs: Any
) -> FloatArray:
    """
    Univariate Kernel Density Estimation with Statsmodels

    Parameters
    ----------
    data :
        Data points used to compute a density estimator. It
        has `n x 1` dimensions, representing n points and p
        variables.
    grid :
        Data points at which the desity will be estimated. It
        has `m x 1` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    from statsmodels.nonparametric.kde import KDEUnivariate

    kde = KDEUnivariate(data)
    kde.fit(**kwargs)
    return kde.evaluate(grid)  # type: ignore


def kde_statsmodels_m(
    data: FloatArray, grid: FloatArray, **kwargs: Any
) -> FloatArray:
    """
    Multivariate Kernel Density Estimation with Statsmodels

    Parameters
    ----------
    data :
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid :
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out :
        Density estimate. Has `m x 1` dimensions
    """
    from statsmodels.nonparametric.kernel_density import KDEMultivariate

    kde = KDEMultivariate(data, **kwargs)
    return kde.pdf(grid)


def kde_sklearn(
    data: FloatArray, grid: FloatArray, **kwargs: Any
) -> FloatArray:
    """
    Kernel Density Estimation with Scikit-learn

    Parameters
    ----------
    data :
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid :
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out :
        Density estimate. Has `m x 1` dimensions
    """
    # Not core dependency
    try:
        from sklearn.neighbors import KernelDensity
    except ImportError as err:
        raise ImportError("scikit-learn is not installed") from err
    kde_skl = KernelDensity(**kwargs)
    kde_skl.fit(data)
    # score_samples() returns the log-likelihood of the samples
    log_pdf = kde_skl.score_samples(grid)
    return np.exp(log_pdf)


def kde_count(data: FloatArray, grid: FloatArray, **kwargs: Any) -> FloatArray:
    """
    Kernel Density Estimation via count within radius

    Parameters
    ----------
    data :
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid :
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out :
        Density estimate. Has `m x 1` dimensions
    """
    r = kwargs.get("radius", np.ptp(data) / 10)

    # Get the number of data points within the radius r of each grid point
    iter = (np.sum(np.linalg.norm(data - g, axis=1) < r) for g in grid)
    count = np.fromiter(iter, float, count=data.shape[0])

    # Get fraction of data within radius
    density = count / data.shape[0]

    return density


KDE_FUNCS = {
    "statsmodels-u": kde_statsmodels_u,
    "statsmodels-m": kde_statsmodels_m,
    "scipy": kde_scipy,
    "scikit-learn": kde_sklearn,
    "sklearn": kde_sklearn,
    "count": kde_count,
}


def kde(
    data: FloatArray, grid: FloatArray, package: str, **kwargs: Any
) -> FloatArray:
    """
    Kernel Density Estimation

    Parameters
    ----------
    package :
        Package whose kernel density estimation to use.
        Should be one of
        `['statsmodels-u', 'statsmodels-m', 'scipy', 'sklearn']`.
    data :
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid :
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    if package == "statsmodels":
        package = "statsmodels-m"
    func = KDE_FUNCS[package]
    return func(data, grid, **kwargs)


def get_var_type(col: pd.Series) -> Literal["c", "o", "u"]:
    """
    Return var_type (for KDEMultivariate) of the column

    Parameters
    ----------
    col :
        A dataframe column.

    Returns
    -------
    out :
        Character that denotes the type of column.
        `c` for continuous, `o` for ordered categorical and
        `u` for unordered categorical or if not sure.

    See Also
    --------
    statsmodels.nonparametric.kernel_density.KDEMultivariate : For the origin
        of the character codes.
    """
    if array_kind.continuous(col):
        return "c"
    elif array_kind.discrete(col):
        return "o" if array_kind.ordinal else "u"
    else:
        # unordered if unsure
        return "u"
