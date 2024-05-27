from __future__ import annotations

import typing
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import SIZE_FACTOR, order_as_data_mapping, to_rgba
from ..doctools import document
from ..exceptions import PlotnineWarning
from ..mapping import aes
from .geom import geom
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer
    from plotnine.typing import DataLike


@document
class geom_vline(geom):
    """
    Vertical line

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {
        "color": "black",
        "linetype": "solid",
        "size": 0.5,
        "alpha": 1,
    }
    REQUIRED_AES = {"xintercept"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "inherit_aes": False,
    }

    legend_key_size = staticmethod(geom_segment.legend_key_size)

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        data, mapping = order_as_data_mapping(data, mapping)
        xintercept = kwargs.pop("xintercept", None)
        if xintercept is not None:
            if mapping:
                warn(
                    "The 'xintercept' parameter has overridden "
                    "the aes() mapping.",
                    PlotnineWarning,
                )
            data = pd.DataFrame({"xintercept": np.repeat(xintercept, 1)})
            mapping = aes(xintercept="xintercept")
            kwargs["show_legend"] = False

        geom.__init__(self, mapping, data, **kwargs)

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        """
        Plot all groups
        """
        ranges = coord.backtransform_range(panel_params)
        data["x"] = data["xintercept"]
        data["xend"] = data["xintercept"]
        data["y"] = ranges.y[0]
        data["yend"] = ranges.y[1]
        data = data.drop_duplicates()

        for _, gdata in data.groupby("group"):
            gdata.reset_index(inplace=True)
            geom_segment.draw_group(gdata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a vertical line in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        from matplotlib.lines import Line2D

        x = [0.5 * da.width] * 2
        y = [0, da.height]
        linewidth = data["size"] * SIZE_FACTOR
        color = to_rgba(data["color"], data["alpha"])
        key = Line2D(
            x,
            y,
            linestyle=data["linetype"],
            linewidth=linewidth,
            color=color,
            solid_capstyle="butt",
            antialiased=False,
        )
        da.add_artist(key)
        return da
