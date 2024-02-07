from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

import numpy as np
import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineWarning
from .stat import stat

if TYPE_CHECKING:
    from typing import Any, Optional

    from plotnine.typing import FloatArray, FloatArrayLike


@document
class stat_ellipse(stat):
    """
    Calculate normal confidence interval ellipse

    {usage}

    Parameters
    ----------
    {common_parameters}
    type : Literal["t", "norm", "euclid"], default="t"
        The type of ellipse.
        `t` assumes a multivariate t-distribution.
        `norm` assumes a multivariate normal distribution.
        `euclid` draws a circle with the radius equal to
        `level`, representing the euclidean distance from the center.

    level : float, default=0.95
        The confidence level at which to draw the ellipse.
    segments : int, default=51
        Number of segments to be used in drawing the ellipse.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "path",
        "position": "identity",
        "na_rm": False,
        "type": "t",
        "level": 0.95,
        "segments": 51,
    }

    @classmethod
    def compute_group(cls, data, scales, **params):
        import scipy.stats as stats
        from scipy import linalg

        level = params["level"]
        segments = params["segments"]
        type_ = params["type"]

        dfn = 2
        dfd = len(data) - 1

        if dfd < 3:
            warn("Too few points to calculate an ellipse", PlotnineWarning)
            return pd.DataFrame({"x": [], "y": []})

        m: FloatArray = np.asarray(data[["x", "y"]])

        # The stats used to create the ellipse
        if type_ == "t":
            res = cov_trob(m)
            cov = res["cov"]
            center = res["center"]
        elif type_ == "norm":
            cov = np.cov(m, rowvar=False)
            center = np.mean(m, axis=0)
        elif type_ == "euclid":
            cov = np.cov(m, rowvar=False)
            cov = np.diag(np.repeat(np.diag(cov).min(), 2))
            center = np.mean(m, axis=0)
        else:
            raise ValueError(f"Unknown value for type={type_}")

        # numpy's cholesky function does not gaurantee upper/lower
        # triangular factorization.
        chol_decomp = linalg.cholesky(cov, lower=False)

        # Parameters of the ellipse
        if type_ == "euclid":
            radius = level / chol_decomp.max()
        else:
            radius = np.sqrt(dfn * stats.f.ppf(level, dfn, dfd))

        space = np.linspace(0, 2 * np.pi, segments)

        # Catesian coordinates
        unit_circle = np.column_stack([np.cos(space), np.sin(space)])
        res = center + radius * np.dot(unit_circle, chol_decomp)

        return pd.DataFrame({"x": res[:, 0], "y": res[:, 1]})


def cov_trob(
    x,
    wt: Optional[FloatArrayLike] = None,
    cor=False,
    center: FloatArrayLike | bool = True,
    nu=5,
    maxit=25,
    tol=0.01,
):
    """
    Covariance Estimation for Multivariate t Distribution

    Estimates a covariance or correlation matrix assuming the
    data came from a multivariate t distribution: this provides
    some degree of robustness to outlier without giving a high
    breakdown point.

    **credit**: This function a port of the R function
    `MASS::cov.trob`.

    Parameters
    ----------
    x : array
        data matrix. Missing values (NaNs) are not allowed.
    wt : array
        A vector of weights for each case: these are treated as
        if the case i actually occurred `wt[i]` times.
    cor : bool
        Flag to choose between returning the correlation
        (`cor=True`) or covariance (`cor=False`) matrix.
    center : array | bool
        A logical value or a numeric vector providing the location
        about which the covariance is to be taken.
        If `center=False`, no centering is done; if
        `center=True` the MLE of the location vector is used.
    nu : int
        'degrees of freedom' for the multivariate t distribution.
        Must exceed 2 (so that the covariance matrix is finite).
    maxit : int
        Maximum number of iterations in fitting.
    tol : float
        Convergence tolerance for fitting.

    Returns
    -------
    out : dict
        A dictionary with with the following key-value

        - `cov` : the fitted covarince matrix.
        - `center` : the estimated or specified location vector.
        - `wt` : the specified weights: only returned if the
           wt argument was given.
        - `n_obs` : the number of cases used in the fitting.
        - `cor` : the fitted correlation matrix: only returned
          if `cor=True`.
        - `call` : The matched call.
        - `iter` : The number of iterations used.

    References
    ----------
    - J. T. Kent, D. E. Tyler and Y. Vardi (1994) A curious likelihood
      identity for the multivariate t-distribution. *Communications in
      Statistics-Simulation and Computation* **23**, 441-453.

    - Venables, W. N. and Ripley, B. D. (1999) *Modern Applied
      Statistics with S-PLUS*. Third Edition. Springer.

    """
    from scipy import linalg

    def test_values(x):
        if pd.isna(x).any() or np.isinf(x).any():
            raise ValueError("Missing or infinite values in 'x'")

    def scale_simp(x: FloatArray, center: FloatArray, n: int, p: int):
        return x - np.repeat([center], n, axis=0)

    x = np.asarray(x)
    n, p = x.shape
    test_values(x)
    ans: dict[str, Any] = {}

    # wt
    if wt is None:
        wt = np.ones(n)
    else:
        wt = np.asarray(wt)
        ans["wt0"] = wt

        if len(wt) != n:
            raise ValueError(
                "length of 'wt' must equal number of observations."
            )
        if any(wt < 0):
            raise ValueError("Negative weights not allowed.")
        if not np.sum(wt):
            raise ValueError("No positive weights.")

        x = x[wt > 0, :]
        wt = wt[wt > 0]
        n, _ = x.shape

    wt = wt[:, np.newaxis]

    # loc
    use_loc = False
    if isinstance(center, bool):
        if center:
            loc = np.sum(wt * x, axis=0) / wt.sum()
            use_loc = True
        else:
            loc = np.zeros(p)
    else:
        if len(center) != p:
            raise ValueError("'center' is not the right length")
        loc = np.asarray(center)

    # Default values for the typechecker
    iteration = 0
    X = np.array([], ndmin=x.ndim)

    w = wt * (1 + p / nu)
    for iteration in range(maxit):
        w0 = w
        X = scale_simp(x, loc, n, p)
        _, s, v = linalg.svd(np.sqrt(w / np.sum(w)) * X)
        wX = X @ v.T @ np.diag(np.full(p, 1 / s))
        Q = np.squeeze((wX**2) @ np.ones(p))
        w = (wt * (nu + p)) / (nu + Q)[:, np.newaxis]
        if use_loc:
            loc = np.sum(w * x, axis=0) / w.sum()
        if all(np.abs(w - w0) < tol):
            break
    else:  # nobreak
        _c1 = np.mean(w) - np.mean(wt) > tol
        _c2 = np.abs(np.mean(w * Q) / p - 1) > tol  # pyright: ignore
        if _c1 and _c2:
            warn("Convergence probably failed.", PlotnineWarning)

    _a = np.sqrt(w) * X
    cov = (_a.T @ _a) / np.sum(wt)

    if cor:
        sd = np.sqrt(np.diag(cov))
        ans["cor"] = (cov / sd) / np.repeat([sd], p, axis=0).T

    ans.update(
        cov=cov,
        center=loc,
        n_obs=n,
        iter=iteration,
    )
    return ans
