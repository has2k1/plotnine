import itertools
import types

import narwhals as nw
import numpy as np

from .._utils import frame, is_scalar
from ..doctools import document
from ..mapping.evaluation import after_stat
from .binning import cut, fuzzybreaks
from .stat import stat


@document
class stat_bin_2d(stat):
    """
    2 Dimensional bin counts

    {usage}

    Parameters
    ----------
    {common_parameters}
    bins : int, default=30
        Number of bins. Overridden by binwidth.
    breaks : array_like | tuple[array_like, array_like] , default=None
        Bin boundaries. This supersedes the `binwidth`, `bins`,
        `center` and `boundary`. It can be an array_like or
        a list of two array_likes to provide distinct breaks for
        the `x` and `y` axes.
    binwidth : float, default=None
        The width of the bins. The default is to use bins that
        cover the range of the data. You should always override this
        value, exploring multiple widths to find the best to illustrate
        the stories in your data.
    drop : bool, default=False
        If `True`{.py}, removes all cells with zero counts.

    See Also
    --------
    plotnine.geom_rect : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "xmin"    # x lower bound for the bin
    "xmax"    # x upper bound for the bin
    "ymin"    # y lower bound for the bin
    "ymax"    # y upper bound for the bin
    "count"   # number of points in bin
    "density" # density of points in bin, scaled to integrate to 1
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "rect",
        "bins": 30,
        "breaks": None,
        "binwidth": None,
        "drop": True,
    }
    DEFAULT_AES = {"fill": after_stat("count"), "weight": None}
    CREATES = {"xmin", "xmax", "ymin", "ymax", "count", "density"}
    DROPPED_AES = ["weight"]

    def setup_params(self, data):
        params = self.params
        params["bins"] = dual_param(params["bins"])
        params["breaks"] = dual_param(params["breaks"])
        params["binwidth"] = dual_param(params["binwidth"])

    def compute_group(self, data, scales):
        bins = self.params["bins"]
        breaks = self.params["breaks"]
        binwidth = self.params["binwidth"]
        drop = self.params["drop"]

        if "weight" in data.columns:
            weight = np.nan_to_num(frame.to_numpy(data["weight"]))
        else:
            weight = np.ones(len(data))

        # The bins will be over the dimension(full size) of the
        # trained x and y scales
        range_x = scales.x.dimension()
        range_y = scales.y.dimension()

        # Trick cut into creating cuts over the range of the scale
        x = np.append(frame.to_numpy(data["x"]), range_x)
        y = np.append(frame.to_numpy(data["y"]), range_y)

        # create the cutting parameters
        xbreaks = fuzzybreaks(
            scales.x, breaks=breaks.x, binwidth=binwidth.x, bins=bins.x
        )
        ybreaks = fuzzybreaks(
            scales.y, breaks.y, binwidth=binwidth.y, bins=bins.y
        )

        # Remove the spurious points
        xbins = cut(x, xbreaks, right=True)[:-2]
        ybins = cut(y, ybreaks, right=True)[:-2]

        # Because we are graphing, we want to see equal breaks
        # The original breaks have an extra room to the left
        ybreaks[0] -= np.diff(np.diff(ybreaks))[0]
        xbreaks[0] -= np.diff(np.diff(xbreaks))[0]

        # A weighted frequency table, with a cell for every bin
        shape = (len(xbreaks) - 1, len(ybreaks) - 1)
        valid = ~(np.isnan(xbins) | np.isnan(ybins))
        cells = (xbins[valid].astype(int), ybins[valid].astype(int))
        table = np.zeros(shape)
        np.add.at(table, cells, weight[valid])
        occupied = np.zeros(shape, dtype=bool)
        occupied[cells] = True

        # create rectangles
        rects = []
        keys = itertools.product(
            range(len(ybreaks) - 1), range(len(xbreaks) - 1)
        )
        for j, i in keys:
            if occupied[i, j]:
                cval = table[i, j]
            elif drop:
                continue
            else:
                cval = 0
            # xmin, xmax, ymin, ymax, count
            rects.append(
                [xbreaks[i], xbreaks[i + 1], ybreaks[j], ybreaks[j + 1], cval]
            )

        columns = ["xmin", "xmax", "ymin", "ymax", "count"]
        arr = np.array(rects, dtype=float).reshape(-1, len(columns))
        new_data = frame.frame_like(
            data, {name: arr[:, i] for i, name in enumerate(columns)}
        )
        return new_data.with_columns(
            density=nw.col("count") / nw.col("count").sum()
        )


stat_bin2d = stat_bin_2d


def dual_param(value):
    """
    Return duplicate of parameter value

    Used to apply same value to x & y axes if only one
    value is given.
    """
    if is_scalar(value):
        return types.SimpleNamespace(x=value, y=value)

    if hasattr(value, "x") and hasattr(value, "y"):
        return value

    if len(value) == 2:
        return types.SimpleNamespace(x=value[0], y=value[1])
    else:
        return types.SimpleNamespace(x=value, y=value)
