from __future__ import annotations

from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np
import pandas as pd
from mizani.utils import min_max

from .._utils import groupby_apply, is_scalar
from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from .contours import contour_breaks, contour_lines, xyz_to_grid
from .density import get_var_type, kde
from .stat import restore_constant_columns, stat

if TYPE_CHECKING:
    from plotnine.typing import FloatArray, FloatArrayLike

# Do not restore columns created during density estimation after
# contouring. Most vary within a group and are excluded automatically,
# but `n` is constant and would otherwise leak into contour output.
_DENSITY_PHASE_COLUMNS = frozenset({"z", "density", "ndensity", "count", "n"})


@document
class stat_density_2d(stat):
    """
    A two-dimensional kernel density estimate

    {usage}

    Parameters
    ----------
    {common_parameters}
    contour :
        Whether to contour the two-dimensional density estimate.
    contour_var :
        Computed variable that sets contour heights. Use `density`,
        `ndensity` or `count`.
    n :
        Number of equally spaced points at which the density is to
        be estimated. For efficient computation, it should be a power
        of two.
    bins :
        Number of contour bands. Takes precedence over `binwidth`.
    binwidth :
        Distance between adjacent contour values.
    breaks :
        Explicit contour values, or a function that receives the range of
        `contour_var` and distance between contours. Explicit values
        override `bins` and `binwidth`. A function uses the distance
        selected by `bins` or `binwidth`. By default, values are selected
        for ten bands.
    levels :
        Deprecated. Use `bins` to set the number of bands or `breaks` to
        set contour values directly.
    package :
        Package whose kernel density estimation to use.
    kde_params :
        Keyword arguments to pass on to the kde class.

    See Also
    --------
    plotnine.geom_density_2d : The default `geom` for this `stat`.
    statsmodels.nonparametric.kernel_density.KDEMultivariate
    scipy.stats.gaussian_kde
    sklearn.neighbors.KernelDensity
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "density"   # computed density at a point
    "ndensity"  # density, scaled to a maximum of 1
    "count"     # density scaled by the number of observations
    "n"         # number of observations in the group
    "level"     # height of the contour
    "nlevel"    # height of the contour, scaled to a maximum of 1
    "piece"     # identifier for one disconnected contour
    ```

    Without contouring, the output contains `density`, `ndensity`, `count`
    and `n`. With contouring, it contains `level`, `nlevel` and `piece`.
    """
    REQUIRED_AES = {"x"}
    DEFAULT_PARAMS = {
        "geom": "density_2d",
        "contour": True,
        "contour_var": "density",
        "bins": None,
        "binwidth": None,
        "breaks": None,
        "package": "statsmodels",
        "kde_params": None,
        "n": 64,
        "levels": None,
    }
    CREATES = {"y", "density", "ndensity", "count", "n"}
    DROPPED_AES = ["density", "ndensity", "count"]

    def setup_params(self, data):
        params = self.params

        if params["levels"] is not None:
            warn(
                "stat_density_2d: `levels` is deprecated. Use `bins` for a "
                "number of contour bands, or `breaks` for the contour "
                "values themselves.",
                PlotnineWarning,
            )
            if is_scalar(params["levels"]):
                params["bins"] = params["levels"]
            else:
                params["breaks"] = params["levels"]

        if params["contour_var"] not in ("density", "ndensity", "count"):
            raise PlotnineError(
                "`contour_var` must be one of 'density', 'ndensity' or "
                f"'count'; got {params['contour_var']!r}."
            )

        if params["kde_params"] is None:
            params["kde_params"] = {}

        kde_params = params["kde_params"]
        if params["package"] == "statsmodels":
            params["package"] = "statsmodels-m"
            if "var_type" not in kde_params:
                x_type = get_var_type(data["x"])
                y_type = get_var_type(data["y"])
                kde_params["var_type"] = f"{x_type}{y_type}"

    def compute_group(self, data, scales):
        params = self.params
        package = params["package"]
        kde_params = params["kde_params"]

        group = data["group"].iloc[0]
        range_x = scales.x.dimension()
        range_y = scales.y.dimension()
        _x = np.linspace(range_x[0], range_x[1], params["n"])
        _y = np.linspace(range_y[0], range_y[1], params["n"])

        # The grid must have a "similar" shape (n, p) to the var_data
        X, Y = np.meshgrid(_x, _y)
        x = cast("FloatArrayLike", data["x"].to_numpy())
        y = cast("FloatArrayLike", data["y"].to_numpy())
        var_data = np.array([x, y]).T
        grid = np.array([X.flatten(), Y.flatten()]).T
        density = kde(var_data, grid, package, **kde_params)

        n_obs = len(data)
        return pd.DataFrame(
            {
                "x": X.flatten(),
                "y": Y.flatten(),
                "density": density,
                "ndensity": density / np.nanmax(density),
                "count": n_obs * density,
                "n": n_obs,
                "group": group,
                "level": 1,
                "piece": 1,
            }
        )

    def compute_layer(self, data, layout):
        # Estimate every density before selecting breaks so the complete
        # layer, including all facet panels, shares contour heights.
        params = self.params
        data = super().compute_layer(data, layout)
        if not params["contour"] or not len(data):
            return data

        data["z"] = data[params["contour_var"]]
        breaks = contour_breaks(
            min_max(data["z"], na_rm=True, finite=True),
            params["bins"],
            params["binwidth"],
            params["breaks"],
        )
        return groupby_apply(
            data, ["PANEL", "group"], self._contour_group, breaks
        )

    def _contour_group(
        self, data: pd.DataFrame, breaks: FloatArray
    ) -> pd.DataFrame:
        """
        Contour one panel group and restore its original constant columns
        """
        res = self.compute_contours(
            *xyz_to_grid(data), breaks, data["group"].iloc[0]
        )

        # Contouring follows panel computation. Restore original constant
        # columns, but exclude columns created during density estimation.
        return restore_constant_columns(
            res, data.drop(columns=list(_DENSITY_PHASE_COLUMNS))
        )

    def compute_contours(self, x, y, Z, breaks, group):
        """
        Trace one contour line at every break on an axis-aligned grid
        """
        return contour_lines(x, y, Z, breaks, group)
