import numpy as np
import pandas as pd

from ..doctools import document
from ..mapping.evaluation import after_stat
from .stat import stat


@document
class stat_ecdf(stat):
    """
    Emperical Cumulative Density Function

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
    plotnine.geom_step
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
    DEFAULT_PARAMS = {
        "geom": "step",
        "position": "identity",
        "na_rm": False,
        "n": None,
        "pad": True,
    }
    DEFAULT_AES = {"y": after_stat("ecdf")}
    CREATES = {"ecdf"}

    @classmethod
    def compute_group(cls, data, scales, **params):
        from statsmodels.distributions.empirical_distribution import ECDF

        # If n is None, use raw values; otherwise interpolate
        if params["n"] is None:
            x = np.unique(data["x"])
        else:
            x = np.linspace(data["x"].min(), data["x"].max(), params["n"])

        if params["pad"]:
            x = np.hstack([-np.inf, x, np.inf])

        ecdf = ECDF(data["x"])(x)
        res = pd.DataFrame({"x": x, "ecdf": ecdf})
        return res
