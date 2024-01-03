import itertools
import types

import numpy as np
import pandas as pd

from .._utils import is_scalar
from ..doctools import document
from ..mapping.evaluation import after_stat
from .binning import fuzzybreaks
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
        Bin boundaries. This supercedes the `binwidth`, `bins`,
        `center` and `boundary`. It can be an array_like or
        a list of two array_likes to provide distinct breaks for
        the `x` and `y` axes.
    binwidth : float, default=None
        The width of the bins. The default is to use bins bins that
        cover the range of the data. You should always override this
        value, exploring multiple widths to find the best to illustrate
        the stories in your data.
    drop : bool, default=False
        If `True`{.py}, removes all cells with zero counts.
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
        "position": "identity",
        "na_rm": False,
        "bins": 30,
        "breaks": None,
        "binwidth": None,
        "drop": True,
    }
    DEFAULT_AES = {"fill": after_stat("count"), "weight": None}
    CREATES = {"xmin", "xmax", "ymin", "ymax", "count", "density"}

    def setup_params(self, data):
        params = self.params.copy()
        params["bins"] = dual_param(params["bins"])
        params["breaks"] = dual_param(params["breaks"])
        params["binwidth"] = dual_param(params["binwidth"])
        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        bins = params["bins"]
        breaks = params["breaks"]
        binwidth = params["binwidth"]
        drop = params["drop"]
        weight = data.get("weight")

        if weight is None:
            weight = np.ones(len(data["x"]))

        # The bins will be over the dimension(full size) of the
        # trained x and y scales
        range_x = scales.x.dimension()
        range_y = scales.y.dimension()

        # Trick pd.cut into creating cuts over the range of
        # the scale
        x = np.append(data["x"], range_x)
        y = np.append(data["y"], range_y)

        # create the cutting parameters
        xbreaks = fuzzybreaks(
            scales.x, breaks=breaks.x, binwidth=binwidth.x, bins=bins.x
        )
        ybreaks = fuzzybreaks(
            scales.y, breaks.y, binwidth=binwidth.y, bins=bins.y
        )

        xbins = pd.cut(
            x,
            bins=xbreaks,  # pyright: ignore
            labels=False,
            right=True,
        )
        ybins = pd.cut(
            y,
            bins=ybreaks,  # pyright: ignore
            labels=False,
            right=True,
        )

        # Remove the spurious points
        xbins = xbins[:-2]
        ybins = ybins[:-2]

        # Because we are graphing, we want to see equal breaks
        # The original breaks have an extra room to the left
        ybreaks[0] -= np.diff(np.diff(ybreaks))[0]
        xbreaks[0] -= np.diff(np.diff(xbreaks))[0]

        bins_grid_long = pd.DataFrame(
            {
                "xbins": xbins,
                "ybins": ybins,
                "weight": weight,
            }
        )
        table = bins_grid_long.pivot_table(
            "weight", index=["xbins", "ybins"], aggfunc="sum"
        )["weight"]

        # create rectangles
        rects = []
        keys = itertools.product(
            range(len(ybreaks) - 1), range(len(xbreaks) - 1)
        )
        for j, i in keys:
            try:
                cval = table[(i, j)]
            except KeyError:
                if drop:
                    continue
                cval = 0
            # xmin, xmax, ymin, ymax, count
            row = [
                xbreaks[i],
                xbreaks[i + 1],
                ybreaks[j],
                ybreaks[j + 1],
                cval,
            ]
            rects.append(row)

        new_data = pd.DataFrame(
            rects, columns=["xmin", "xmax", "ymin", "ymax", "count"]
        )
        new_data["density"] = new_data["count"] / new_data["count"].sum()
        return new_data


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
