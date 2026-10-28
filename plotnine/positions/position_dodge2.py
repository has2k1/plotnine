from __future__ import annotations

import typing
from copy import copy

import narwhals as nw
import numpy as np

from .._utils import frame
from ..exceptions import PlotnineError
from .position_dodge import max_count, position_dodge

if typing.TYPE_CHECKING:
    from typing import Literal, Optional

    from plotnine._utils.frame import DataFrame
    from plotnine.typing import IntArray


class position_dodge2(position_dodge):
    """
    Dodge overlaps and place objects side-by-side

    This is an enhanced version of
    [](`~plotnine.positions.position_dodge`) that can deal
    with rectangular overlaps that do not share a lower x border.

    Parameters
    ----------
    width :
        Dodging width, when different to the width of the
        individual elements. This is useful when you want
        to align narrow geoms with wider geoms
    preserve :
        Should dodging preserve the total width of all elements
        at a position, or the width of a single element?
    padding :
        Padding between elements at the same position.
        Elements are shrunk by this proportion to allow space
        between them.
    reverse :
        Reverse the default ordering of the groups. This is
        useful if you're rotating both the plot and legend.
    """

    REQUIRED_AES = {"x"}

    def __init__(
        self,
        width: Optional[float] = None,
        preserve: Literal["total", "single"] = "total",
        padding: float = 0.1,
        reverse: bool = False,
    ):
        self.params = {
            "width": width,
            "preserve": preserve,
            "padding": padding,
            "reverse": reverse,
        }

    def setup_params(self, data):
        if (
            ("xmin" not in data.columns)
            and ("xmax" not in data.columns)
            and (self.params["width"] is None)
        ):
            msg = "Width not defined. Set with `position_dodge2(width = ?)`"
            raise PlotnineError(msg)

        params = copy(self.params)

        if params["preserve"] == "total":
            params["n"] = None
        elif "x" in data.columns:
            params["n"] = max_count(data, ["PANEL", "x"])
        else:
            # interval geoms
            params["n"] = max(
                find_x_overlaps(gdf).max()
                for _, gdf in frame.group_split(data, "PANEL")
            )
        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        return cls.collide2(data, params=params)

    @staticmethod
    def strategy(data, params):
        padding = params["padding"]
        n = params["n"]

        if not all(col in data.columns for col in ["xmin", "xmax"]):
            data = data.with_columns(xmin=nw.col("x"), xmax=nw.col("x"))

        xmin = frame.to_numpy(data["xmin"]).astype(float)
        xmax = frame.to_numpy(data["xmax"]).astype(float)

        # Groups of boxes that share the same position
        xid = find_x_overlaps(data)
        nxid = xid.max()

        # Find newx using xid, i.e. the center of each group of
        # overlapping elements. for boxes, bars, etc. this should
        # be the same as original x, but for arbitrary rects it
        # may not be
        group_min = np.full(nxid, np.inf)
        group_max = np.full(nxid, -np.inf)
        np.fmin.at(group_min, xid - 1, xmin)
        np.fmax.at(group_max, xid - 1, xmax)
        newx = (group_min + group_max)[xid - 1] / 2

        if n is None:
            # If n is None, preserve total widths of elements at
            # each position by dividing widths by the number of
            # elements at that position
            n = np.bincount(xid)[xid]
        new_width = (xmax - xmin) / n

        # Find the total width of each group of elements
        unique_newx = np.unique(newx[~np.isnan(newx)])
        sizes = np.array([new_width[newx == v].sum() for v in unique_newx])

        # Starting xmin for each group of elements
        starts = unique_newx - (sizes / 2)

        # Set the elements in place
        for i, start in enumerate(starts, start=1):
            bool_idx = xid == i
            divisions = np.cumsum(np.hstack([start, new_width[bool_idx]]))
            xmin[bool_idx] = divisions[:-1]
            xmax[bool_idx] = divisions[1:]

        # x values get moved to between xmin and xmax
        x = (xmin + xmax) / 2

        # Shrink elements to add space between them
        if len(np.unique(xid)) < len(xid):
            pad_width = new_width * (1 - padding)
            xmin = x - pad_width / 2
            xmax = x + pad_width / 2

        data = frame.assign(data, xmin=xmin, xmax=xmax, x=x)
        if "xend" in data.columns:
            data = frame.assign(data, x=xmin, xend=xmax)

        return data


def find_x_overlaps(df: DataFrame) -> IntArray:
    """
    Find overlapping regions along the x axis
    """
    xmin = frame.to_numpy(df["xmin"])
    xmax = frame.to_numpy(df["xmax"])
    n = len(df)
    overlaps = np.zeros(n, dtype=int)
    overlaps[0] = 1
    counter = 1
    for i in range(1, n):
        if xmin[i] >= xmax[i - 1]:
            counter += 1
        overlaps[i] = counter
    return overlaps
