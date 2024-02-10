from __future__ import annotations

import typing
from typing import Sized
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import order_as_data_mapping
from ..doctools import document
from ..exceptions import PlotnineWarning
from ..mapping import aes
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

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
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "inherit_aes": False,
    }
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

            data = pd.DataFrame(
                {"intercept": np.repeat(intercept, 1), "slope": slope}
            )

            mapping = aes(intercept="intercept", slope="slope")
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
        data["x"] = ranges.x[0]
        data["xend"] = ranges.x[1]
        data["y"] = ranges.x[0] * data["slope"] + data["intercept"]
        data["yend"] = ranges.x[1] * data["slope"] + data["intercept"]
        data = data.drop_duplicates()

        for _, gdata in data.groupby("group"):
            gdata.reset_index(inplace=True)
            geom_segment.draw_group(gdata, panel_params, coord, ax, **params)
