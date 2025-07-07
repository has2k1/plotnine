import numpy as np
import pandas as pd

from .._utils import array_kind, jitter, resolution
from ..doctools import document
from ..exceptions import PlotnineError
from ..mapping.aes import has_groups
from .binning import breaks_from_bins, breaks_from_binwidth
from .stat import stat
from .stat_density import compute_density


@document
class stat_sina(stat):
    """
    Compute Sina plot values

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
        Seed or Random number generator to use. If `None`, then
        numpy global generator [](`numpy.random`) is used.
    scale : Literal["area", "count", "width"], default="area"
        How to scale the sina groups.

        - `area` - Scale by the largest density/bin among the different sinas
        - `count` - areas are scaled proportionally to the number of points
        - `width` - Only scale according to the maxwidth parameter.
    style :
        Type of sina plot to draw. The options are
        ```python
        'full'        # Regular (2 sided)
        'left'        # Left-sided half
        'right'       # Right-sided half
        'left-right'  # Alternate (left first) half by the group
        'right-left'  # Alternate (right first) half by the group
        ```

    See Also
    --------
    plotnine.geom_sina : The default `geom` for this `stat`.
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
        "geom": "sina",
        "position": "dodge",
        "na_rm": False,
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
        if (
            array_kind.continuous(data["x"])
            and not has_groups(data)
            and (data["x"] != data["x"].iloc[0]).any()
        ):
            raise TypeError(
                "Continuous x aesthetic -- did you forget aes(group=...)?"
            )
        return data

    def setup_params(self, data):
        params = self.params
        random_state = params["random_state"]

        if params["maxwidth"] is None:
            params["maxwidth"] = resolution(data["x"], False) * 0.9

        if params["binwidth"] is None and self.params["bins"] is None:
            params["bins"] = 50

        if random_state is None:
            params["random_state"] = np.random
        elif isinstance(random_state, int):
            params["random_state"] = np.random.RandomState(random_state)

        # Required by compute_density
        params["kernel"] = "gau"  # It has to be a gaussian kernel
        params["cut"] = 0
        params["gridsize"] = None
        params["clip"] = (-np.inf, np.inf)
        params["bounds"] = (-np.inf, np.inf)
        params["n"] = 512

    def compute_panel(self, data, scales):
        params = self.params
        maxwidth = params["maxwidth"]
        random_state = params["random_state"]
        fuzz = 1e-8
        y_dim = scales.y.dimension()
        y_dim_fuzzed = (y_dim[0] - fuzz, y_dim[1] + fuzz)

        if params["binwidth"] is not None:
            params["bins"] = breaks_from_binwidth(
                y_dim_fuzzed, params["binwidth"]
            )
        else:
            params["bins"] = breaks_from_bins(y_dim_fuzzed, params["bins"])

        data = super().compute_panel(data, scales)

        if not len(data):
            return data

        if params["scale"] == "area":
            data["sinawidth"] = data["density"] / data["density"].max()
        elif params["scale"] == "count":
            data["sinawidth"] = (
                data["density"]
                / data["density"].max()
                * data["n"]
                / data["n"].max()
            )
        elif params["scale"] == "width":
            data["sinawidth"] = data["scaled"]
        else:
            msg = "Unknown scale value '{}'"
            raise PlotnineError(msg.format(params["scale"]))

        is_infinite = ~np.isfinite(data["sinawidth"])
        if is_infinite.any():
            data.loc[is_infinite, "sinawidth"] = 0

        data["xmin"] = data["x"] - maxwidth / 2
        data["xmax"] = data["x"] + maxwidth / 2
        data["x_diff"] = (
            random_state.uniform(-1, 1, len(data))
            * maxwidth
            * data["sinawidth"]
            / 2
        )
        data["width"] = maxwidth

        # jitter y values if the input is integer,
        # but not if it is the same value
        y = data["y"].to_numpy()
        all_integers = (y == np.floor(y)).all()
        some_are_unique = len(np.unique(y)) > 1
        if all_integers and some_are_unique:
            data["y"] = jitter(y, random_state=random_state)

        return data

    def compute_group(self, data, scales):
        maxwidth = self.params["maxwidth"]
        bins = self.params["bins"]
        bin_limit = self.params["bin_limit"]
        weight = None
        y = data["y"]

        if len(data) == 0:
            return pd.DataFrame()

        elif len(data) < 3:
            data["density"] = 0
            data["scaled"] = 1
        elif len(np.unique(y)) < 2:
            data["density"] = 1
            data["scaled"] = 1
        elif self.params["method"] == "density":
            from scipy.interpolate import interp1d

            # density kernel estimation
            range_y = y.min(), y.max()
            dens = compute_density(y, weight, range_y, self.params)
            densf = interp1d(
                dens["x"],
                dens["density"],
                bounds_error=False,
                fill_value="extrapolate",  # pyright: ignore
            )
            data["density"] = densf(y)
            data["scaled"] = data["density"] / dens["density"].max()
        else:
            # bin based estimation
            bin_index = pd.cut(y, bins, include_lowest=True, labels=False)
            data["density"] = (
                pd.Series(bin_index)
                .groupby(bin_index)
                .apply(len)[bin_index]
                .to_numpy()
            )
            data.loc[data["density"] <= bin_limit, "density"] = 0
            data["scaled"] = data["density"] / data["density"].max()

        # Compute width if x has multiple values
        if len(data["x"].unique()) > 1:
            width = np.ptp(data["x"]) * maxwidth
        else:
            width = maxwidth

        data["width"] = width
        data["n"] = len(data)
        data["x"] = np.mean([data["x"].max(), data["x"].min()])

        return data

    def finish_layer(self, data):
        # Rescale x in case positions have been adjusted
        style = self.params["style"]
        x_mean = data["x"].to_numpy()
        x_mod = (data["xmax"] - data["xmin"]) / data["width"]
        data["x"] = data["x"] + data["x_diff"] * x_mod
        x = data["x"].to_numpy()
        even = data["group"].to_numpy() % 2 == 0

        def mirror_x(bool_idx):
            """
            Mirror x locations along the mean value
            """
            data.loc[bool_idx, "x"] = (
                2 * x_mean[bool_idx] - data.loc[bool_idx, "x"]
            )

        match style:
            case "left":
                mirror_x(x_mean < x)
            case "right":
                mirror_x(x < x_mean)
            case "left-right":
                mirror_x(even & (x < x_mean) | ~even & (x_mean < x))
            case "right-left":
                mirror_x(even & (x_mean < x) | ~even & (x < x_mean))

        return data
