from __future__ import annotations

import typing
from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import frame, groupby_apply
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

    from plotnine._utils.frame import DataFrame, Implementation
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
    DROPPED_AES = ["weight", "bin", "bincenter"]

    def setup_params(self, data):
        params = self.params

        if (
            params["breaks"] is None
            and params["binwidth"] is None
            and params["bins"] is None
        ):
            bins = freedman_diaconis_bins(data["x"])
            params["bins"] = bins
            warn(
                f"'stat_bindot' is using '{bins=}'. "
                "Pick better value with 'binwidth'",
                PlotnineWarning,
            )

    def compute_panel(self, data, scales):
        params = self.params
        if (
            params["method"] == "dotdensity"
            and params["binpositions"] == "all"
        ):
            binaxis = params["binaxis"]
            if binaxis not in ("x", "y"):
                raise ValueError(f"Unknown value {binaxis=}")

            newdata = densitybin(
                x=data[binaxis],
                weight=data["weight"] if "weight" in data.columns else None,
                binwidth=params["binwidth"],
                bins=params["bins"],
            )
            data = frame.sort(data, binaxis)
            newdata = frame.sort(newdata, "x")
            data = data.with_columns(
                newdata[col]
                for col in ("bin", "binwidth", "weight", "bincenter")
            )
        return super().compute_panel(data, scales)

    def compute_group(self, data, scales):
        params = self.params
        backend = data.implementation
        # Check that weights are whole numbers
        # (for dots, weights must be whole)
        weight = data["weight"] if "weight" in data.columns else None
        if weight is not None:
            int_status = [
                (w * 1.0).is_integer() for w in frame.to_numpy(weight)
            ]
            if not all(int_status):
                raise PlotnineError(
                    "Weights for stat_bindot must be nonnegative integers."
                )

        if params["binaxis"] == "x":
            rangee = scales.x.dimension((0, 0))
            values = frame.to_numpy(data["x"])
            midline = 0  # Make pyright happy
        else:
            rangee = scales.y.dimension((0, 0))
            values = frame.to_numpy(data["y"])
            # The middle of each group, on the stack axis
            x = frame.to_numpy(data["x"])
            midline = np.mean([x.min(), x.max()])

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
                values,
                breaks,
                weight,
                pad=False,
                closed=closed,
                backend=backend,
            )
            # for consistency
            data = data.rename({"width": "binwidth", "x": "bincenter"})
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
                    backend=backend,
                )

            # Collapse each bin and get a count
            def func(df):
                return frame.frame_like(
                    df,
                    {
                        "binwidth": [df["binwidth"].item(0)],
                        "bincenter": [df["bincenter"].item(0)],
                        "count": [int(df["weight"].sum())],
                    },
                )

            # plyr::ddply + plyr::summarize
            data = groupby_apply(data, "bincenter", func)

            if data["count"].sum() != 0:
                count = nw.col("count").fill_null(0)
                data = data.with_columns(count=count).with_columns(
                    ncount=nw.col("count") / nw.col("count").abs().max()
                )
                if params["drop"]:
                    data = data.filter(nw.col("count") > 0)

        if params["binaxis"] == "x":
            # For x binning, the width of the geoms
            # is same as the width of the bin
            data = data.with_columns(x=nw.col("bincenter")).drop("bincenter")
            data = data.with_columns(width=nw.col("binwidth"))
        else:
            # For y binning, set the x midline.
            # This is needed for continuous x axis
            data = data.with_columns(y=nw.col("bincenter")).drop("bincenter")
            data = frame.assign(data, x=midline)

        return data


def densitybin(
    x,
    weight: FloatArrayLike | None,
    binwidth: float | None,
    bins: int = 30,
    rangee: Optional[tuple[float, float]] = None,
    *,
    backend: Implementation | None = None,
) -> DataFrame:
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
    backend :
        Library of the returned dataframe. If None, it is that of `x`
        if `x` is a series.

    Returns
    -------
    data : DataFrame
    """
    if backend is None:
        backend = frame.backend_of(x)

    x = frame.as_numpy(x)
    if all(frame.isna(x)):
        return frame.frame(backend=backend)

    if weight is None:
        weight = np.ones(len(x))
    else:
        weight = np.array(frame.as_numpy(weight), dtype=float)
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

    results = frame.frame(
        {
            "x": x,
            "bin": bin_ids,
            "binwidth": binwidth,
            "weight": weight,
        },
        backend=backend,
    )
    # This is a plyr::ddply
    _x = nw.col("x")
    return results.with_columns(
        bincenter=(_x.min().over("bin") + _x.max().over("bin")) / 2
    )
