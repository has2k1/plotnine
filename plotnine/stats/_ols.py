"""
Ordinary and weighted least squares

This is a port of the least squares fit in statsmodels, so that
`stat_smooth` does not require statsmodels (which requires pandas)
for linear models. It gives the same results as
`statsmodels.api.OLS` and `statsmodels.api.WLS`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from plotnine.typing import FloatArray, FloatArrayLike


__all__ = ("fit_least_squares", "add_constant")


def add_constant(x: FloatArrayLike) -> FloatArray:
    """
    Add a column of ones before the column(s) of x
    """
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    return np.column_stack([np.ones(len(x)), x])


def _pinv_extended(x: FloatArray, rcond: float = 1e-15):
    """
    Pseudo-inverse of x and the singular values of x
    """
    u, s, vt = np.linalg.svd(x, False)
    s_orig = np.copy(s)
    cutoff = rcond * np.maximum.reduce(s)
    for i in range(min(vt.shape[1], u.shape[0])):
        s[i] = 1.0 / s[i] if s[i] > cutoff else 0.0
    res = np.dot(np.transpose(vt), np.multiply(s[:, np.newaxis], u.T))
    return res, s_orig


@dataclass
class LeastSquaresResults:
    """
    Results of a least squares fit
    """

    params: FloatArray
    normalized_cov_params: FloatArray
    df_resid: float
    ssr: float

    @property
    def model(self) -> LeastSquaresResults:
        return self

    @property
    def mse_resid(self) -> float:
        """
        Mean squared error of the residuals
        """
        if self.df_resid == 0:
            return np.nan
        return self.ssr / self.df_resid

    def cov_params(self) -> FloatArray:
        """
        Covariance matrix of the parameters
        """
        return self.normalized_cov_params * self.mse_resid

    def predict(
        self, params: FloatArray, exog: FloatArrayLike | None = None
    ) -> FloatArray:
        """
        Predict the response for the exogenous values
        """
        if exog is None:
            params, exog = self.params, params
        return np.dot(np.asarray(exog), params)


def fit_least_squares(
    y: FloatArrayLike,
    X: FloatArrayLike,
    weights: FloatArrayLike | None = None,
) -> LeastSquaresResults:
    """
    Fit a linear model with ordinary or weighted least squares

    Parameters
    ----------
    y :
        Response
    X :
        Design matrix
    weights :
        Weights of the observations. If given, the fit is a weighted
        least squares.
    """
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    if weights is not None:
        sqrt_weights = np.sqrt(np.asarray(weights, dtype=float))
        wexog = sqrt_weights[:, None] * X
        wendog = sqrt_weights * y
    else:
        wexog, wendog = X, y

    pinv_wexog, singular_values = _pinv_extended(wexog)
    normalized_cov_params = np.dot(pinv_wexog, np.transpose(pinv_wexog))
    rank = np.linalg.matrix_rank(np.diag(singular_values))
    params = np.dot(pinv_wexog, wendog)
    wresid = wendog - np.dot(wexog, params)
    return LeastSquaresResults(
        params=params,
        normalized_cov_params=normalized_cov_params,
        df_resid=len(wexog) - rank,
        ssr=np.dot(wresid, wresid),
    )
