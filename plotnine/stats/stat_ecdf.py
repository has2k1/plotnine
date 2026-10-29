from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .._utils import frame
from ..doctools import document
from ..mapping.evaluation import after_stat
from .stat import stat

if TYPE_CHECKING:
    from plotnine.typing import FloatArray, FloatArrayLike


@document
class stat_ecdf(stat):
    """
    Empirical Cumulative Density Function

    {usage}

    Parameters
    ----------
    {common_parameters}
    n  : int, default=None
        This is the number of points to interpolate with.
        If `None`{.py}, do not interpolate.
    pad : bool, default=True
        If True, pad the domain with `-inf` and `+inf` so that
        ECDF does not have discontinuities at the extremes.

    See Also
    --------
    plotnine.geom_step : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "x"     # x in the data
    "ecdf"  # cumulative density corresponding to x
    ```
    """

    REQUIRED_AES = {"x"}
    DEFAULT_PARAMS = {"geom": "step", "n": None, "pad": True}
    DEFAULT_AES = {"y": after_stat("ecdf")}
    CREATES = {"ecdf"}
    DROPPED_AES = ["weight"]

    def compute_group(self, data, scales):
        n, pad = self.params["n"], self.params["pad"]
        values = frame.to_numpy(data["x"])

        if n is None:
            x = np.unique(values)
        else:
            x = np.linspace(values.min(), values.max(), n)

        if pad:
            x = np.hstack([-np.inf, x, np.inf])

        return frame.frame_like(data, {"x": x, "ecdf": ecdf(values, x)})


def ecdf(values: FloatArrayLike, x: FloatArrayLike) -> FloatArray:
    """
    Evaluate the empirical cumulative distribution function

    Parameters
    ----------
    values :
        Values from which the distribution is created.
    x :
        Points at which to evaluate the distribution.

    Notes
    -----
    This gives the same results as
    `statsmodels.distributions.empirical_distribution.ECDF`.
    """
    values = np.sort(np.asarray(values))
    n = len(values)
    y = np.hstack([0, np.linspace(1.0 / n, 1, n)])
    return y[np.searchsorted(values, x, side="right")]
