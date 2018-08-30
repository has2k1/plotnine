"""
Kernel Density Functions

These functions make it easy to integrate stats that compute
kernel densities with the wider scientific python ecosystem.

Credit: Jake VanderPlas for the original kde_* functions
https://jakevdp.github.io/blog/2013/12/01/kernel-density-estimation/
"""
from contextlib import suppress

import numpy as np
import pandas.api.types as pdtypes
from scipy.stats import gaussian_kde
from statsmodels.nonparametric.kde import KDEUnivariate
from statsmodels.nonparametric.kernel_density import KDEMultivariate

# Not core dependency
with suppress(ImportError):
    from sklearn.neighbors import KernelDensity


def kde_scipy(data, grid, **kwargs):
    """
    Kernel Density Estimation with Scipy

    Parameters
    ----------
    data : numpy.array
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid : numpy.array
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    kde = gaussian_kde(data.T, **kwargs)
    return kde.evaluate(grid.T)


def kde_statsmodels_u(data, grid, **kwargs):
    """
    Univariate Kernel Density Estimation with Statsmodels

    Parameters
    ----------
    data : numpy.array
        Data points used to compute a density estimator. It
        has `n x 1` dimensions, representing n points and p
        variables.
    grid : numpy.array
        Data points at which the desity will be estimated. It
        has `m x 1` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    kde = KDEUnivariate(data)
    kde.fit(**kwargs)
    return kde.evaluate(grid)


def kde_statsmodels_m(data, grid, **kwargs):
    """
    Multivariate Kernel Density Estimation with Statsmodels

    Parameters
    ----------
    data : numpy.array
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid : numpy.array
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    kde = KDEMultivariate(data, **kwargs)
    return kde.pdf(grid)


def kde_sklearn(data, grid, **kwargs):
    """
    Kernel Density Estimation with Scikit-learn

    Parameters
    ----------
    data : numpy.array
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid : numpy.array
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    kde_skl = KernelDensity(**kwargs)
    kde_skl.fit(data)
    # score_samples() returns the log-likelihood of the samples
    log_pdf = kde_skl.score_samples(grid)
    return np.exp(log_pdf)


KDE_FUNCS = {
    'statsmodels-u': kde_statsmodels_u,
    'statsmodels-m': kde_statsmodels_m,
    'scipy': kde_scipy,
    'scikit-learn': kde_sklearn,
    'sklearn': kde_sklearn
}


def kde(data, grid, package, **kwargs):
    """
    Kernel Density Estimation

    Parameters
    ----------
    package : str
        Package whose kernel density estimation to use.
        Should be one of
        `['statsmodels-u', 'statsmodels-m', 'scipy', 'sklearn']`.
    data : numpy.array
        Data points used to compute a density estimator. It
        has `n x p` dimensions, representing n points and p
        variables.
    grid : numpy.array
        Data points at which the desity will be estimated. It
        has `m x p` dimensions, representing m points and p
        variables.

    Returns
    -------
    out : numpy.array
        Density estimate. Has `m x 1` dimensions
    """
    if package == 'statsmodels':
        package = 'statsmodels-m'
    func = KDE_FUNCS[package]
    return func(data, grid, **kwargs)


def get_var_type(col):
    """
    Return var_type (for KDEMultivariate) of the column

    Parameters
    ----------
    col : pandas.Series
        A dataframe column.

    Returns
    -------
    out : str
        One of ['c', 'o', 'u'].

    See Also
    --------
    The origin of the character codes is
    :class:`statsmodels.nonparametric.kernel_density.KDEMultivariate`.
    """
    if pdtypes.is_numeric_dtype(col):
        # continuous
        return 'c'
    elif pdtypes.is_categorical_dtype(col):
        # ordered or unordered
        return 'o' if col.cat.ordered else 'u'
    else:
        # unordered if unsure, e.g string columns that
        # are not categorical
        return 'u'
