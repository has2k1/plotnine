from __future__ import annotations

import typing

import narwhals as nw

from .._utils import frame, to_rgba
from ..doctools import document
from .geom import geom
from .geom_line import geom_line, geom_path
from .geom_ribbon import geom_ribbon

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


@document
class geom_smooth(geom):
    """
    A smoothed conditional mean

    {usage}

    Parameters
    ----------
    {common_parameters}
    legend_fill_ratio : float, default=0.5
        How much (vertically) of the legend box should be filled by
        the color that indicates the confidence intervals. Should be
        in the range [0, 1].

    See Also
    --------
    plotnine.stat_smooth : The default `stat` for this `geom`.
    """

    DEFAULT_AES = {
        "alpha": 0.4,
        "color": "black",
        "fill": "#999999",
        "linetype": "solid",
        "size": 1,
        "ymin": None,
        "ymax": None,
    }
    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {"stat": "smooth", "legend_fill_ratio": 0.5}

    legend_key_size = staticmethod(geom_path.legend_key_size)

    def use_defaults(
        self, data: DataFrame, aes_modifiers: dict[str, Any]
    ) -> DataFrame:
        has_ribbon = "ymin" in data.columns and "ymax" in data.columns
        data = super().use_defaults(data, aes_modifiers)
        # When there is no ribbon, the default values for 'ymin'
        # and 'ymax' are None (not numeric). So we remove those
        # so that this geom does not train the y scale.
        if not has_ribbon:
            data = data.drop("ymin", "ymax")
        return data

    def setup_data(self, data: DataFrame) -> DataFrame:
        return frame.sort(data, ["PANEL", "group", "x"])

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        has_ribbon = "ymin" in data.columns and "ymax" in data.columns
        if has_ribbon:
            data2 = data.with_columns(color=nw.lit("none"))
            params2 = params.copy()
            params2["outline_type"] = "full"
            geom_ribbon.draw_group(data2, panel_params, coord, ax, params2)

        data = data.with_columns(alpha=nw.lit(1))
        geom_line.draw_group(data, panel_params, coord, ax, params)

    @staticmethod
    def draw_legend(
        data: dict[str, Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
            Legend data
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        from matplotlib.patches import Rectangle

        try:
            has_se = lyr.stat.params["se"]
        except KeyError:
            has_se = False

        if has_se:
            fill = to_rgba(data["fill"], data["alpha"])
            r = lyr.geom.params["legend_fill_ratio"]
            bg = Rectangle(
                (0, (1 - r) * da.height / 2),
                width=da.width,
                height=r * da.height,
                facecolor=fill,
                linewidth=0,
            )
            da.add_artist(bg)

        data["alpha"] = 1
        return geom_path.draw_legend(data, da, lyr)
