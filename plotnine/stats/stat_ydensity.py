from contextlib import suppress

import numpy as np
import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineError
from .stat import stat
from .stat_density import compute_density, stat_density


@document
class stat_ydensity(stat):
    """
    Density estimate

    {usage}

    Parameters
    ----------
    {common_parameters}
    kernel : str, default='gaussian'
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
    bw : str | float, default="nrd0"
        The bandwidth to use, If a float is given, it is the bandwidth.
        The `str` choices are:

        ```python
        "nrd0"
        "normal_reference"
        "scott"
        "silverman"
        ```

        `nrd0` is a port of `stats::bw.nrd0` in R; it is eqiuvalent
        to `silverman` when there is more than 1 value in a group.
    scale : Literal["area", "count", "width"], default="area"
        How to scale the violins. The options are:
        If `area` all violins have the same area, before trimming the tails.
        If `count` the areas are scaled proportionally to the number of
        observations.
        If `width` all violins have the same maximum width.

    See Also
    --------
    plotnine.geoms.geom_violin
    statsmodels.nonparametric.kde.KDEUnivariate
    statsmodels.nonparametric.kde.KDEUnivariate.fit
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "width"        # Maximum width of density, [0, 1] range.
    "violinwidth"  # Shape of the violin
    ```

    Calculated aesthetics are accessed using the `after_stat` function.
    e.g. `after_stat('width')`{.py}.
    """
    REQUIRED_AES = {"x", "y"}
    NON_MISSING_AES = {"weight"}
    DEFAULT_PARAMS = {
        "geom": "violin",
        "position": "dodge",
        "na_rm": False,
        "adjust": 1,
        "kernel": "gaussian",
        "n": 1024,
        "trim": True,
        "bw": "nrd0",
        "scale": "area",
    }
    DEFAULT_AES = {"weight": None}
    CREATES = {"width", "violinwidth"}

    def setup_data(self, data):
        if "x" not in data:
            data["x"] = 0
        return data

    def setup_params(self, data):
        params = self.params.copy()

        valid_scale = ("area", "count", "width")
        if params["scale"] not in valid_scale:
            msg = "Parameter scale should be one of {}"
            raise PlotnineError(msg.format(valid_scale))

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
                "kernel should be one of {}. "
                "You may use the abbreviations {}"
            )
            raise PlotnineError(msg.format(lookup.keys(), lookup.values()))

        missing_params = stat_density.DEFAULT_PARAMS.keys() - params.keys()
        for key in missing_params:
            params[key] = stat_density.DEFAULT_PARAMS[key]

        return params

    @classmethod
    def compute_panel(cls, data, scales, **params):
        data = super(cls, cls).compute_panel(data, scales, **params)

        if not len(data):
            return data

        if params["scale"] == "area":
            data["violinwidth"] = data["density"] / data["density"].max()
        elif params["scale"] == "count":
            data["violinwidth"] = (
                data["density"]
                / data["density"].max()
                * data["n"]
                / data["n"].max()
            )
        elif params["scale"] == "width":
            data["violinwidth"] = data["scaled"]
        else:
            msg = "Unknown scale value '{}'"
            raise PlotnineError(msg.format(params["scale"]))

        return data

    @classmethod
    def compute_group(cls, data, scales, **params):
        n = len(data)
        if n == 0:
            return pd.DataFrame()

        weight = data.get("weight")

        if params["trim"]:
            range_y = data["y"].min(), data["y"].max()
        else:
            range_y = scales.y.dimension()

        dens = compute_density(data["y"], weight, range_y, **params)

        if not len(dens):
            return dens

        dens["y"] = dens["x"]
        dens["x"] = np.mean([data["x"].min(), data["x"].max()])

        # Compute width if x has multiple values
        if len(np.unique(data["x"])) > 1:
            dens["width"] = np.ptp(data["x"]) * 0.9

        return dens
