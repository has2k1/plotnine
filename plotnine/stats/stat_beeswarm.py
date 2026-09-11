import numpy as np

from .._utils import jitter
from ..doctools import document
from ._swarm import (
    check_x_is_discrete,
    estimate_group_density,
    finish_swarm_layer,
    quasirandom_offset,
    setup_swarm_params,
    swarm_widths,
)
from .stat import stat


@document
class stat_beeswarm(stat):
    """
    Compute beeswarm plot values

    {usage}

    Parameters
    ----------
    {common_parameters}
    binwidth : float, default=None
        The width of the bins. The default is to use bins that
        cover the range of the data. You should always override this
        value, exploring multiple widths to find the best to
        illustrate the stories in your data.
    bins : int, default=50
        Number of bins. Overridden by binwidth.
    method : Literal["density", "counts"], default="density"
        Choose the method to spread the samples within the same bin
        along the x-axis. Available methods: "density", "counts"
        (can be abbreviated, e.g. "d"). See Details.
    maxwidth : float, default=None
        Control the maximum width the points can spread into.
        Values should be in the range (0, 1).
    adjust : float, default=1
        Adjusts the bandwidth of the density kernel when
        `method="density"`. see [](`~plotnine.stats.stat_density`).
    bw : str | float, default="nrd0"
        The bandwidth to use, If a float is given, it is the bandwidth.
        The `str`{.py} choices are:
        `"nrd0", "normal_reference", "scott", "silverman"`{.py}

        `nrd0` is a port of `stats::bw.nrd0` in R; it is eqiuvalent
        to `silverman` when there is more than 1 value in a group.
    bin_limit : int, default=1
        If the samples within the same y-axis bin are more
        than `bin_limit`, the samples's X coordinates will be adjusted.
        This parameter is effective only when `method="counts"`{.py}
    random_state : int | ~numpy.random.RandomState, default=None
        Seed or random number generator for jittering integer `y`
        values. If `None`, use NumPy's global random state.
    scale : Literal["area", "count", "width"], default="area"
        How to scale the beeswarm groups.

        - `area` - Scale by the largest density/bin among the
          different beeswarms.
        - `count` - areas are scaled proportionally to the number of points
        - `width` - Only scale according to the maxwidth parameter.
    style :
        Type of beeswarm plot to draw. The options are
        ```python
        'full'        # Regular (2 sided)
        'left'        # Left-sided half
        'right'       # Right-sided half
        'left-right'  # Alternate (left first) half by the group
        'right-left'  # Alternate (right first) half by the group
        ```

    See Also
    --------
    plotnine.geom_beeswarm : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "quantile"  # quantile
    "group"     # group identifier
    ```

    Calculated aesthetics are accessed using the `after_stat` function.
    e.g. `after_stat('quantile')`{.py}.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "beeswarm",
        "position": "dodge",
        "binwidth": None,
        "bins": None,
        "method": "density",
        "bw": "nrd0",
        "maxwidth": None,
        "adjust": 1,
        "bin_limit": 1,
        "random_state": None,
        "scale": "area",
        "style": "full",
    }
    CREATES = {"scaled"}

    def setup_data(self, data):
        return check_x_is_discrete(data)

    def setup_params(self, data):
        setup_swarm_params(self.params, data)

    def compute_panel(self, data, scales):
        params = self.params
        maxwidth = params["maxwidth"]
        data = super().compute_panel(data, scales)

        if not len(data):
            return data

        swarm_widths(data, params["scale"], "width_fraction")
        data["xmin"] = data["x"] - maxwidth / 2
        data["xmax"] = data["x"] + maxwidth / 2
        data["x_diff"] = quasirandom_offset(
            data, maxwidth, "width_fraction", params
        )
        data["width"] = maxwidth

        # jitter y values if the input is integer,
        # but not if it is the same value
        y = data["y"].to_numpy()
        all_integers = (y == np.floor(y)).all()
        some_are_unique = len(np.unique(y)) > 1
        if all_integers and some_are_unique:
            data["y"] = jitter(y, random_state=params["random_state"])

        return data

    def compute_group(self, data, scales):
        return estimate_group_density(
            data, scales, self.params, few_rows_density=1
        )

    def finish_layer(self, data):
        return finish_swarm_layer(data, self.params["style"])
