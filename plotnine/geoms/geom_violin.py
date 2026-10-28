from __future__ import annotations

from typing import TYPE_CHECKING, cast

import narwhals as nw
import numpy as np

from .._utils import frame, interleave, resolution
from ..doctools import document
from .geom import geom
from .geom_path import geom_path
from .geom_polygon import geom_polygon

if TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine import aes
    from plotnine._utils.frame import DataFrame
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
    quantile_color : str | tuple, default=None
        Color of the quantile lines.
    quantile_size : str, default="o"
        The linewidth of the quantile lines.
    quantile_linetype : float, default=1.5
        The linetype of the quantile lines.

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
        "quantile_color": None,
        "quantile_colour": None,
        "quantile_size": None,
        "quantile_linetype": None,
        "style": "full",
        "scale": "area",
        "trim": True,
        "width": None,
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

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "width" not in data.columns:
            if self.params["width"]:
                width = self.params["width"]
            else:
                width = resolution(data["x"], False) * 0.9
            data = frame.assign(data, width=width)

        by = ["group", "PANEL"]
        x, y, half_width = nw.col("x"), nw.col("y"), nw.col("width") / 2
        return frame.sort(data, by).with_columns(
            ymin=y.min().over(*by),
            ymax=y.max().over(*by),
            xmin=x - half_width,
            xmax=x + half_width,
        )

    def draw_panel(
        self,
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        """
        Plot all groups
        """
        params = self.params.copy()
        quantiles = params.pop("draw_quantiles")
        style = params.pop("style")
        zorder = params.pop("zorder")

        for i, ((group,), df) in enumerate(frame.group_split(data, "group")):
            # Place the violins with the smalleer group number on top
            # of those with larger numbers. The group_zorder values should
            # be in the range [zorder, zorder + 1) to stay within the layer.
            group = cast("int", group)
            group_zorder = zorder + 0.9 / group
            params["zorder"] = group_zorder

            # Find the points for the line to go all the way around
            x = frame.to_numpy(df["x"])
            violinwidth = frame.to_numpy(df["violinwidth"])
            xminv = x - violinwidth * (x - frame.to_numpy(df["xmin"]))
            xmaxv = x + violinwidth * (frame.to_numpy(df["xmax"]) - x)
            even = i % 2 == 0
            if (
                style == "left"
                or (style == "left-right" and even)
                or (style == "right-left" and not even)
            ):
                xmaxv = x
            elif (
                style == "right"
                or (style == "right-left" and even)
                or (style == "left-right" and not even)
            ):
                xminv = x
            df = frame.assign(df, xminv=xminv, xmaxv=xmaxv)

            # Make sure it's sorted properly to draw the outline
            # i.e violin = kde + mirror kde,
            # bottom to top then top to bottom
            up = frame.sort(df, "y")
            down = frame.sort(df, "y", descending=True)
            polygon_df = frame.concat([up, down])
            polygon_df = frame.assign(
                polygon_df,
                x=np.hstack(
                    [
                        frame.to_numpy(up["xminv"]),
                        frame.to_numpy(down["xmaxv"]),
                    ]
                ),
            )

            # Close the polygon: set first and last point the same
            polygon_df = frame.concat([polygon_df, polygon_df.head(1)])

            # plot violin polygon
            geom_polygon.draw_group(
                polygon_df,
                panel_params,
                coord,
                ax,
                params,
            )

            if quantiles is not None:
                from plotnine.mapping._atomic import broadcast_ae_value

                # Get dataframe with quantile segments and that
                # with aesthetics then put them together
                # Each quantile segment is defined by 2 points and
                # they all get similar aesthetics
                aes_df = df.drop("x", "y", "group")
                aes_df = frame.take(aes_df, [0] * 2 * len(quantiles))

                # Create aes_df for quantile segments
                segment_df = nw.concat(
                    [make_quantile_df(df, quantiles), aes_df], how="horizontal"
                )

                color = params["quantile_colour"] or params["quantile_color"]
                n = len(segment_df)
                overrides = {}
                if color:
                    overrides["color"] = broadcast_ae_value(color, "color", n)

                if linetype := params["quantile_linetype"]:
                    overrides["linetype"] = broadcast_ae_value(
                        linetype,
                        "linetype",
                        n,
                    )

                if size := params["quantile_size"]:
                    overrides["size"] = size

                segment_df = frame.assign(segment_df, **overrides)

                # plot quantile segments
                geom_path.draw_group(
                    segment_df,
                    panel_params,
                    coord,
                    ax,
                    params,
                )


def make_quantile_df(data: DataFrame, draw_quantiles: FloatArray) -> DataFrame:
    """
    Return a dataframe with info needed to draw quantile segments
    """
    from scipy.interpolate import interp1d

    density = frame.to_numpy(data["density"])
    y = frame.to_numpy(data["y"])
    dens = density.cumsum() / density.sum()
    ecdf = interp1d(dens, y, assume_sorted=True)
    ys = ecdf(draw_quantiles)

    # Get the violin bounds for the requested quantiles
    violin_xminvs = interp1d(y, frame.to_numpy(data["xminv"]))(ys)
    violin_xmaxvs = interp1d(y, frame.to_numpy(data["xmaxv"]))(ys)

    return frame.frame_like(
        data,
        {
            "x": interleave(violin_xminvs, violin_xmaxvs),
            "y": np.repeat(ys, 2),
            "group": np.repeat(np.arange(1, len(ys) + 1), 2),
        },
    )
