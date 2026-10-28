import narwhals as nw
import numpy as np

from .._utils import frame, resolution
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
    plotnine.geom_histogram : The default `geom` for this `stat`.
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
        "width": None,
    }
    DEFAULT_AES = {"y": after_stat("count")}
    CREATES = {"count", "prop"}
    DROPPED_AES = ["weight"]

    def setup_params(self, data):
        if self.params["width"] is None:
            self.params["width"] = resolution(data["x"], False) * 0.9

    def compute_group(self, data, scales):
        if ("y" in data.columns) or ("y" in self.params):
            msg = "stat_count() must not be used with a y aesthetic"
            raise PlotnineError(msg)

        if "weight" not in data.columns:
            data = data.with_columns(weight=nw.lit(1))

        width = self.params["width"]
        count = frame.sort(
            data.group_by("x").agg(nw.col("weight").sum().alias("count")), "x"
        )
        counts = frame.to_numpy(count["count"])
        return frame.assign(
            count,
            prop=counts / np.abs(counts).sum(),
            width=width,
        ).select("count", "prop", "x", "width")
