from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd

from .._utils import groupby_apply, interleave, resolution
from ..doctools import document
from .geom import geom
from .geom_path import geom_path
from .geom_polygon import geom_polygon

if TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine import aes
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.typing import DataLike, FloatArray


@document
class geom_violin(geom):
    """
    Violin Plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    draw_quantiles : float | list[float], default=None
        draw horizontal lines at the given quantiles (0..1)
        of the density estimate.
    style : str, default="full"
        The type of violin plot to draw. The options are:

        ```python
        'full'        # Regular (2 sided violins)
        'left'        # Left-sided half violins
        'right'       # Right-sided half violins
        'left-right'  # Alternate (left first) half violins by the group
        'right-left'  # Alternate (right first) half violins by the group
        ```

    See Also
    --------
    plotnine.stat_ydensity : The default `stat` for this `geom`.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "#333333",
        "fill": "white",
        "linetype": "solid",
        "size": 0.5,
        "weight": 1,
    }
    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "stat": "ydensity",
        "position": "dodge",
        "draw_quantiles": None,
        "style": "full",
        "scale": "area",
        "trim": True,
        "width": None,
        "na_rm": False,
    }
    draw_legend = staticmethod(geom_polygon.draw_legend)

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        if "draw_quantiles" in kwargs:
            kwargs["draw_quantiles"] = np.repeat(kwargs["draw_quantiles"], 1)
            if not all(0 < q < 1 for q in kwargs["draw_quantiles"]):
                raise ValueError(
                    "draw_quantiles must be a float or "
                    "an iterable of floats (>0.0; < 1.0)"
                )

        if "style" in kwargs:
            allowed = ("full", "left", "right", "left-right", "right-left")
            if kwargs["style"] not in allowed:
                raise ValueError(f"style must be either {allowed}")

        super().__init__(mapping, data, **kwargs)

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if "width" not in data:
            if self.params["width"]:
                data["width"] = self.params["width"]
            else:
                data["width"] = resolution(data["x"], False) * 0.9

        def func(df: pd.DataFrame) -> pd.DataFrame:
            df["ymin"] = df["y"].min()
            df["ymax"] = df["y"].max()
            df["xmin"] = df["x"] - df["width"] / 2
            df["xmax"] = df["x"] + df["width"] / 2
            return df

        # This is a plyr::ddply
        data = groupby_apply(data, ["group", "PANEL"], func)
        return data

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        params = self.params.copy()
        quantiles = params.pop("draw_quantiles")
        style = params.pop("style")
        zorder = params.pop("zorder")

        for i, (group, df) in enumerate(data.groupby("group")):
            # Place the violins with the smalleer group number on top
            # of those with larger numbers. The group_zorder values should be
            # in the range [zorder, zorder + 1) to stay within the layer.
            group = cast("int", group)
            group_zorder = zorder + 0.9 / group
            params["zorder"] = group_zorder

            # Find the points for the line to go all the way around
            df["xminv"] = df["x"] - df["violinwidth"] * (df["x"] - df["xmin"])
            df["xmaxv"] = df["x"] + df["violinwidth"] * (df["xmax"] - df["x"])
            even = i % 2 == 0
            if (
                style == "left"
                or (style == "left-right" and even)
                or (style == "right-left" and not even)
            ):
                df["xmaxv"] = df["x"]
            elif (
                style == "right"
                or (style == "right-left" and even)
                or (style == "left-right" and not even)
            ):
                df["xminv"] = df["x"]

            # Make sure it's sorted properly to draw the outline
            # i.e violin = kde + mirror kde,
            # bottom to top then top to bottom
            n = len(df)
            polygon_df = pd.concat(
                [df.sort_values("y"), df.sort_values("y", ascending=False)],
                axis=0,
                ignore_index=True,
            )

            _df = polygon_df.iloc
            _loc = polygon_df.columns.get_loc
            _df[:n, _loc("x")] = _df[:n, _loc("xminv")]  # type: ignore
            _df[n:, _loc("x")] = _df[n:, _loc("xmaxv")]  # type: ignore

            # Close the polygon: set first and last point the same
            polygon_df.loc[-1, :] = polygon_df.loc[0, :]

            # plot violin polygon
            geom_polygon.draw_group(
                polygon_df,
                panel_params,
                coord,
                ax,
                params,
            )

            if quantiles is not None:
                # Get dataframe with quantile segments and that
                # with aesthetics then put them together
                # Each quantile segment is defined by 2 points and
                # they all get similar aesthetics
                aes_df = df.drop(["x", "y", "group"], axis=1)
                aes_df.reset_index(inplace=True)
                idx = [0] * 2 * len(quantiles)
                aes_df = aes_df.iloc[idx, :].reset_index(drop=True)
                segment_df = pd.concat(
                    [make_quantile_df(df, quantiles), aes_df], axis=1
                )

                # plot quantile segments
                geom_path.draw_group(
                    segment_df,
                    panel_params,
                    coord,
                    ax,
                    params,
                )


def make_quantile_df(
    data: pd.DataFrame, draw_quantiles: FloatArray
) -> pd.DataFrame:
    """
    Return a dataframe with info needed to draw quantile segments
    """
    from scipy.interpolate import interp1d

    dens = data["density"].cumsum() / data["density"].sum()
    ecdf = interp1d(dens, data["y"], assume_sorted=True)
    ys = ecdf(draw_quantiles)

    # Get the violin bounds for the requested quantiles
    violin_xminvs = interp1d(data["y"], data["xminv"])(ys)
    violin_xmaxvs = interp1d(data["y"], data["xmaxv"])(ys)

    data = pd.DataFrame(
        {
            "x": interleave(violin_xminvs, violin_xmaxvs),
            "y": np.repeat(ys, 2),
            "group": np.repeat(np.arange(1, len(ys) + 1), 2),
        }
    )

    return data
