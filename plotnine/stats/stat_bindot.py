from __future__ import annotations

import typing
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import groupby_apply
from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.evaluation import after_stat
from .binning import (
    assign_bins,
    breaks_from_bins,
    breaks_from_binwidth,
    freedman_diaconis_bins,
)
from .stat import stat

if typing.TYPE_CHECKING:
    from typing import Optional

    from plotnine.typing import FloatArrayLike


@document
class stat_bindot(stat):
    """
    Binning for a dot plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    bins : int, default=None
        Number of bins. Overridden by binwidth. If `None`{.py},
        a number is computed using the freedman-diaconis method.
    binwidth : float, default=None
        When `method="dotdensity"`{.py}, this specifies the maximum
        binwidth. When `method="histodot"`{.py}, this specifies the
        binwidth. This supersedes the `bins`.
    origin : float, default=None
        When `method="histodot"`{.py}, origin of the first bin.
    width : float, default=0.9
        When `binaxis="y"`{.py}, the spacing of the dotstacks for
        dodging.
    binaxis : Literal["x", "y"], default="x"
        Axis to bin along.
    method : Literal["dotdensity", "histodot"], default="dotdensity"
        Whether to do dot-density binning or fixed widths binning.
    binpositions : Literal["all", "bygroup"], default="bygroup"
        Position of the bins when `method="dotdensity"`{.py}. The value
        - `bygroup` -  positions of the bins for each group are
        determined separately.
        - `all` - positions of the bins are determined with all
        data taken together. This aligns the dots
        stacks across multiple groups.
    drop : bool, default=False
        If `True`{.py}, remove all bins with zero counts.
    right : bool, default=True
        When `method="histodot"`{.py}, `True`{.py} means include right
        edge of the bins and if `False`{.py} the left edge is included.
    breaks : FloatArray, default=None
        Bin boundaries for `method="histodot"`{.py}. This supersedes the
        `binwidth` and `bins`.

    See Also
    --------
    plotnine.geom_dotplot : The default `geom` for this `stat`.
    plotnine.stat_bin
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "count"    # number of points in bin
    "density"  # density of points in bin, scaled to integrate to 1
    "ncount"   # count, scaled to maximum of 1
    "ndensity" # density, scaled to maximum of 1
    ```

    """

    REQUIRED_AES = {"x"}
    NON_MISSING_AES = {"weight"}
    DEFAULT_PARAMS = {
        "geom": "dotplot",
        "position": "identity",
        "na_rm": False,
        "bins": None,
        "binwidth": None,
        "origin": None,
        "width": 0.9,
        "binaxis": "x",
        "method": "dotdensity",
        "binpositions": "bygroup",
        "drop": False,
        "right": True,
        "breaks": None,
    }
    DEFAULT_AES = {"y": after_stat("count")}
    CREATES = {"width", "count", "density", "ncount", "ndensity"}

    def setup_params(self, data):
        params = self.params

        if (
            params["breaks"] is None
            and params["binwidth"] is None
            and params["bins"] is None
        ):
            params["bins"] = freedman_diaconis_bins(data["x"])
            msg = (
                "'stat_bin()' using 'bins = {}'. "
                "Pick better value with 'binwidth'."
            )
            warn(msg.format(params["bins"]), PlotnineWarning)

    def compute_panel(self, data, scales):
        params = self.params
        if (
            params["method"] == "dotdensity"
            and params["binpositions"] == "all"
        ):
            binaxis = params["binaxis"]
            weight = data.get("weight")
            if binaxis == "x":
                newdata = densitybin(
                    x=data["x"],
                    weight=weight,
                    binwidth=params["binwidth"],
                    bins=params["bins"],
                )
                data = data.sort_values("x")
                data.reset_index(inplace=True, drop=True)
                newdata = newdata.sort_values("x")
                newdata.reset_index(inplace=True, drop=True)
            elif binaxis == "y":
                newdata = densitybin(
                    x=data["y"],
                    weight=weight,
                    binwidth=params["binwidth"],
                    bins=params["bins"],
                )
                data = data.sort_values("y")
                data.reset_index(inplace=True, drop=True)
                newdata = newdata.sort_values("x")
                newdata.reset_index(inplace=True, drop=True)
            else:
                raise ValueError(f"Unknown value {binaxis=}")

            data["bin"] = newdata["bin"]
            data["binwidth"] = newdata["binwidth"]
            data["weight"] = newdata["weight"]
            data["bincenter"] = newdata["bincenter"]
        return super().compute_panel(data, scales)

    def compute_group(self, data, scales):
        params = self.params
        # Check that weights are whole numbers
        # (for dots, weights must be whole)
        weight = data.get("weight")
        if weight is not None:
            int_status = [(w * 1.0).is_integer() for w in weight]
            if not all(int_status):
                raise PlotnineError(
                    "Weights for stat_bindot must be nonnegative integers."
                )

        if params["binaxis"] == "x":
            rangee = scales.x.dimension((0, 0))
            values = data["x"].to_numpy()
            midline = 0  # Make pyright happy
        else:
            rangee = scales.y.dimension((0, 0))
            values = data["y"].to_numpy()
            # The middle of each group, on the stack axis
            midline = np.mean([data["x"].min(), data["x"].max()])

        if params["method"] == "histodot":
            if params["binwidth"] is not None:
                breaks = breaks_from_binwidth(
                    rangee, params["binwidth"], boundary=params["origin"]
                )
            else:
                breaks = breaks_from_bins(
                    rangee, params["bins"], boundary=params["origin"]
                )

            closed = "right" if params["right"] else "left"
            data = assign_bins(
                values, breaks, weight, pad=False, closed=closed
            )
            # for consistency
            data.rename(
                columns={"width": "binwidth", "x": "bincenter"}, inplace=True
            )
        elif params["method"] == "dotdensity":
            # If bin centers are found by group instead of by all,
            # find the bin centers (If binpositions=="all", then
            # we'll already have bin centers.)
            if params["binpositions"] == "bygroup":
                data = densitybin(
                    x=values,
                    weight=weight,
                    binwidth=params["binwidth"],
                    bins=params["bins"],
                    rangee=rangee,
                )

            # Collapse each bin and get a count
            def func(df):
                return pd.DataFrame(
                    {
                        "binwidth": [df["binwidth"].iloc[0]],
                        "bincenter": [df["bincenter"].iloc[0]],
                        "count": [int(df["weight"].sum())],
                    }
                )

            # plyr::ddply + plyr::summarize
            data = groupby_apply(data, "bincenter", func)

            if data["count"].sum() != 0:
                data.loc[np.isnan(data["count"]), "count"] = 0
                data["ncount"] = data["count"] / data["count"].abs().max()
                if params["drop"]:
                    data = data[data["count"] > 0]
                    data.reset_index(inplace=True, drop=True)

        if params["binaxis"] == "x":
            data["x"] = data.pop("bincenter")
            # For x binning, the width of the geoms
            # is same as the width of the bin
            data["width"] = data["binwidth"]
        else:
            data["y"] = data.pop("bincenter")
            # For y binning, set the x midline.
            # This is needed for continuous x axis
            data["x"] = midline

        return data


def densitybin(
    x,
    weight: FloatArrayLike | None,
    binwidth: float | None,
    bins: int = 30,
    rangee: Optional[tuple[float, float]] = None,
):
    """
    Do density binning

    It does not collapse each bin with a count.

    Parameters
    ----------
    x : array_like
        Numbers to bin
    weight : array_like
        Weights
    binwidth : numeric
        Size of the bins
    bins : int
        Number of bins
    rangee : tuple
        Range of x

    Returns
    -------
    data : DataFrame
    """
    if all(pd.isna(x)):
        return pd.DataFrame()

    weight = np.ones(len(x)) if weight is None else np.array(list(weight))
    weight[np.isnan(weight)] = 0

    if rangee is None:
        rangee = np.min(x), np.max(x)
    if bins is None:
        bins = 30
    if binwidth is None:
        binwidth = np.ptp(rangee) / bins

    # Sort weight and x, by x
    order = np.argsort(x)
    weight = weight[order]
    x = x[order]

    cbin = 0  # Current bin ID
    bin_ids = []  # The bin ID for each observation
    # End position of current bin (scan left to right)
    binend = -np.inf

    # Scan list and put dots in bins
    for value in x:
        # If past end of bin, start a new bin at this point
        if value >= binend:
            binend = value + binwidth
            cbin = cbin + 1
        bin_ids.append(cbin)

    def func(series):
        return (series.min() + series.max()) / 2

    results = pd.DataFrame(
        {
            "x": x,
            "bin": bin_ids,
            "binwidth": binwidth,
            "weight": weight,
        }
    )
    # This is a plyr::ddply
    results["bincenter"] = results.groupby("bin")["x"].transform(func)
    return results
