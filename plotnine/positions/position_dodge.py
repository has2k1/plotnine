from __future__ import annotations

import typing
from copy import copy

import narwhals as nw
import numpy as np

from .._utils import frame, is_list_like, match
from ..exceptions import PlotnineError
from .position import position

# Column with the row number of each row in the layer data
ROW_ID = "__plotnine_row_id__"

if typing.TYPE_CHECKING:
    from typing import Literal, Optional

    from plotnine._utils.frame import DataFrame


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
        if "x" in data.columns and "xend" in data.columns:
            if "xmin" not in data.columns:
                data = data.with_columns(xmin=nw.col("x")).drop("x")
            if "xmax" not in data.columns:
                data = data.with_columns(xmax=nw.col("xend"))

        columns = data.columns
        if "x" not in columns and "xmin" in columns and "xmax" in columns:
            data = data.with_columns(x=(nw.col("xmin") + nw.col("xmax")) / 2)
        return super().setup_data(data, params)

    def setup_params(self, data):
        if (
            ("xmin" not in data.columns)
            and ("xmax" not in data.columns)
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
            col = "xmin" if "xmin" in data.columns else "x"
            params["n"] = max_count(data, ["PANEL", col])
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
        if ROW_ID in data.columns:
            width = np.asarray(width)[frame.to_numpy(data[ROW_ID])]

        udata_group = data["group"].unique(maintain_order=True)

        n = params.get("n", None)
        if n is None:
            n = len(udata_group)
        if n == 1:
            return data

        if not all(col in data.columns for col in ["xmin", "xmax"]):
            data = data.with_columns(xmin=nw.col("x"), xmax=nw.col("x"))

        d_width = np.max(frame.to_numpy(data["xmax"] - data["xmin"]))

        # Have a new group index from 1 to number of groups.
        # This might be needed if the group numbers in this set don't
        # include all of 1:n
        groupidx = match(data["group"], sorted(udata_group.to_list()))
        groupidx = np.asarray(groupidx) + 1

        # Find the center for each group, then use that to
        # calculate xmin and xmax
        x = frame.to_numpy(data["x"]) + width * ((groupidx - 0.5) / n - 0.5)
        xmin = x - (d_width / n) / 2
        xmax = x + (d_width / n) / 2
        data = frame.assign(data, x=x, xmin=xmin, xmax=xmax)

        if "x" in data.columns and "xend" in data.columns:
            data = frame.assign(data, x=xmin, xend=xmax)
        return data

    @classmethod
    def compute_layer(cls, data, params, layout):
        # A width for each row of the data
        if is_list_like(params["width"]):
            data = data.with_row_index(ROW_ID)
            return super().compute_layer(data, params, layout).drop(ROW_ID)
        return super().compute_layer(data, params, layout)


def max_count(data: DataFrame, by: list[str]) -> int:
    """
    The highest number of rows with the same values in the columns
    """
    counts = data.group_by(by, drop_null_keys=True).agg(nw.len().alias("n"))
    return int(counts["n"].max()) if len(counts) else 0
