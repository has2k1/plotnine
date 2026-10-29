from __future__ import annotations

import typing
from collections.abc import Sized
from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import frame, order_as_data_mapping
from ..doctools import document
from ..exceptions import PlotnineWarning
from ..mapping import aes
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.typing import DataLike


@document
class geom_abline(geom):
    """
    Lines specified by slope and intercept

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {
        "color": "black",
        "linetype": "solid",
        "alpha": 1,
        "size": 0.5,
    }
    DEFAULT_PARAMS = {"inherit_aes": False}
    REQUIRED_AES = {"slope", "intercept"}
    draw_legend = staticmethod(geom_path.draw_legend)

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        data, mapping = order_as_data_mapping(data, mapping)
        slope = kwargs.pop("slope", None)
        intercept = kwargs.pop("intercept", None)

        # If nothing is set, it defaults to y=x
        if mapping is None and slope is None and intercept is None:
            slope = 1
            intercept = 0

        if slope is not None or intercept is not None:
            if mapping:
                warn(
                    "The 'intercept' and 'slope' when specified override "
                    "the aes() mapping.",
                    PlotnineWarning,
                )
            if isinstance(data, Sized) and len(data):
                warn(
                    "The 'intercept' and 'slope' when specified override "
                    "the data",
                    PlotnineWarning,
                )

            if slope is None:
                slope = 1
            if intercept is None:
                intercept = 0

            data = frame.frame(
                {"intercept": np.repeat(intercept, 1), "slope": slope},
                backend=frame.default_backend(),
            ).to_native()
            mapping = aes(intercept="intercept", slope="slope")
            kwargs["show_legend"] = False

        geom.__init__(self, mapping, data, **kwargs)

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
        ranges = coord.backtransform_range(panel_params)
        slope = nw.col("slope")
        intercept = nw.col("intercept")
        data = data.with_columns(
            x=nw.lit(ranges.x[0]),
            xend=nw.lit(ranges.x[1]),
            y=ranges.x[0] * slope + intercept,
            yend=ranges.x[1] * slope + intercept,
        )
        data = frame.unique_rows(data)

        for _, gdata in frame.group_split(data, "group"):
            geom_segment.draw_group(
                gdata, panel_params, coord, ax, self.params
            )
