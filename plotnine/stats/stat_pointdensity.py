import numpy as np
import pandas as pd

from ..doctools import document
from ..mapping.evaluation import after_stat
from .density import get_var_type, kde
from .stat import stat


@document
class stat_pointdensity(stat):
    """
    Compute density estimation for each point

    {usage}

    Parameters
    ----------
    {common_parameters}
    package : Literal["statsmodels", "scipy", "sklearn"], default="statsmodels"
        Package whose kernel density estimation to use.
    kde_params : dict, default=None
        Keyword arguments to pass on to the kde class.

    See Also
    --------
    statsmodels.nonparametric.kde.KDEMultivariate
    scipy.stats.gaussian_kde
    sklearn.neighbors.KernelDensity
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "density"   # Computed density at a point
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"color": after_stat("density")}
    DEFAULT_PARAMS = {
        "geom": "density_2d",
        "position": "identity",
        "na_rm": False,
        "package": "statsmodels",
        "kde_params": None,
    }
    CREATES = {"density"}

    def setup_params(self, data):
        params = self.params.copy()
        if params["kde_params"] is None:
            params["kde_params"] = {}

        kde_params = params["kde_params"]
        if params["package"] == "statsmodels":
            params["package"] = "statsmodels-m"
            if "var_type" not in kde_params:
                x_type = get_var_type(data["x"])
                y_type = get_var_type(data["y"])
                kde_params["var_type"] = f"{x_type}{y_type}"

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        package = params["package"]
        kde_params = params["kde_params"]

        var_data = np.array([data["x"].to_numpy(), data["y"].to_numpy()]).T
        density = kde(var_data, var_data, package, **kde_params)

        data = pd.DataFrame(
            {
                "x": data["x"],
                "y": data["y"],
                "density": density.flatten(),
            }
        )

        return data
