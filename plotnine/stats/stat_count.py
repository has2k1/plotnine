import numpy as np
import pandas as pd

from .._utils import resolution
from ..doctools import document
from ..exceptions import PlotnineError
from ..mapping.evaluation import after_stat
from .stat import stat


@document
class stat_count(stat):
    """
    Counts the number of cases at each x position

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, default=None
        Bar width. If None, set to 90% of the resolution of the data.

    See Also
    --------
    plotnine.stat_bin
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "count"  # Number of observations at a position
    "prop"   # Ratio of points in the panel at a position
    ```

    """

    REQUIRED_AES = {"x"}
    DEFAULT_PARAMS = {
        "geom": "histogram",
        "position": "stack",
        "na_rm": False,
        "width": None,
    }
    DEFAULT_AES = {"y": after_stat("count")}
    CREATES = {"count", "prop"}

    def setup_params(self, data):
        params = self.params.copy()
        if params["width"] is None:
            params["width"] = resolution(data["x"], False) * 0.9

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        x = data["x"]
        if ("y" in data) or ("y" in params):
            msg = "stat_count() must not be used with a y aesthetic"
            raise PlotnineError(msg)

        weight = data.get("weight", [1] * len(x))
        width = params["width"]
        xdata_long = pd.DataFrame({"x": x, "weight": weight})
        # weighted frequency count
        count = xdata_long.pivot_table("weight", index=["x"], aggfunc="sum")[
            "weight"
        ]
        x = count.index
        count = count.to_numpy()
        return pd.DataFrame(
            {
                "count": count,
                "prop": count / np.abs(count).sum(),
                "x": x,
                "width": width,
            }
        )
