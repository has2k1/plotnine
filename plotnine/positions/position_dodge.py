from __future__ import annotations

import typing
from contextlib import suppress
from copy import copy

import numpy as np
import pandas as pd

from .._utils import groupby_apply, match
from ..exceptions import PlotnineError
from .position import position

if typing.TYPE_CHECKING:
    from typing import Literal, Optional


class position_dodge(position):
    """
    Dodge overlaps and place objects side-by-side

    Parameters
    ----------
    width :
        Dodging width, when different to the width of the
        individual elements. This is useful when you want
        to align narrow geoms with wider geoms
    preserve :
        Should dodging preserve the total width of all elements
        at a position, or the width of a single element?
    """

    REQUIRED_AES = {"x"}

    def __init__(
        self,
        width: Optional[float] = None,
        preserve: Literal["total", "single"] = "total",
    ):
        self.params = {
            "width": width,
            "preserve": preserve,
        }

    def setup_data(self, data, params):
        # # e.g. geom_segment should be dodgeable
        if "x" in data and "xend" in data:
            if "xmin" not in data:
                data["xmin"] = data.pop("x")
            if "xmax" not in data:
                data["xmax"] = data["xend"]

        if "x" not in data and "xmin" in data and "xmax" in data:
            data["x"] = (data["xmin"] + data["xmax"]) / 2

        return super().setup_data(data, params)

    def setup_params(self, data):
        if (
            ("xmin" not in data)
            and ("xmax" not in data)
            and (self.params["width"] is None)
        ):
            msg = "Width not defined. Set with `position_dodge(width = ?)`"
            raise PlotnineError(msg)

        params = copy(self.params)

        if params["preserve"] == "total":
            params["n"] = None
        else:
            # Count at the xmin values per panel and find the highest
            # overall count
            def max_xmin_values(gdf):
                try:
                    n = gdf["xmin"].value_counts().max()
                except KeyError:
                    n = gdf["x"].value_counts().max()
                return pd.DataFrame({"n": [n]})

            res = groupby_apply(data, "PANEL", max_xmin_values)
            params["n"] = res["n"].max()
        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        return cls.collide(data, params=params)

    @staticmethod
    def strategy(data, params):
        """
        Dodge overlapping interval

        Assumes that each set has the same horizontal position.
        """
        width = params["width"]
        with suppress(TypeError):
            iter(width)
            width = np.asarray(width)
            width = width[data.index]

        udata_group = data["group"].drop_duplicates()

        n = params.get("n", None)
        if n is None:
            n = len(udata_group)
        if n == 1:
            return data

        if not all(col in data.columns for col in ["xmin", "xmax"]):
            data["xmin"] = data["x"]
            data["xmax"] = data["x"]

        d_width = np.max(data["xmax"] - data["xmin"])

        # Have a new group index from 1 to number of groups.
        # This might be needed if the group numbers in this set don't
        # include all of 1:n
        udata_group = udata_group.sort_values()
        groupidx = match(data["group"], udata_group)
        groupidx = np.asarray(groupidx) + 1

        # Find the center for each group, then use that to
        # calculate xmin and xmax
        data["x"] = data["x"] + width * ((groupidx - 0.5) / n - 0.5)
        data["xmin"] = data["x"] - (d_width / n) / 2
        data["xmax"] = data["x"] + (d_width / n) / 2

        if "x" in data and "xend" in data:
            data["x"] = data["xmin"]
            data["xend"] = data["xmax"]

        return data
