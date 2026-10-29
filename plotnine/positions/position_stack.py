from __future__ import annotations

from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import frame, remove_missing
from ..exceptions import PlotnineWarning
from .position import position


class position_stack(position):
    """
    Stack plotted objects on top of each other

    The objects to stack are those that have
    an overlapping x range.

    Parameters
    ----------
    vjust :
        By what fraction to avoid overlapping the lower object,
        where `0` gives a complete overlap and `1` gives no overlap.
    reverse :
        Reverse the order of the stacked groups if true.
    """

    fill = False

    def __init__(self, vjust: float = 1, reverse: bool = False):
        self.params = {"vjust": vjust, "reverse": reverse}

    def setup_params(self, data):
        """
        Verify, modify & return a copy of the params.
        """
        # Variable for which to do the stacking
        if "ymax" in data.columns:
            ymin = frame.to_numpy(data["ymin"])
            ymax = frame.to_numpy(data["ymax"])
            if any((ymin != 0) & (ymax != 0)):
                warn(
                    "Stacking not well defined when not anchored on the axis.",
                    PlotnineWarning,
                )
            var = "ymax"
        elif "y" in data.columns:
            var = "y"
        else:
            warn(
                "Stacking requires either ymin & ymax or y "
                "aesthetics. Maybe you want position = 'identity'?",
                PlotnineWarning,
            )
            var = None

        params = self.params.copy()
        params["var"] = var
        params["fill"] = self.fill
        return params

    def setup_data(self, data, params):
        if not params["var"]:
            return data

        if params["var"] == "y":
            data = data.with_columns(ymax=nw.col("y"))
        elif params["var"] == "ymax":
            data = data.with_columns(
                ymax=nw.when(nw.col("ymax") == 0)
                .then(nw.col("ymin"))
                .otherwise(nw.col("ymax"))
            )

        data = remove_missing(
            data, vars=("x", "xmin", "xmax", "y"), name="position_stack"
        )
        return data

    @classmethod
    def compute_panel(cls, data, scales, params):
        if not params["var"]:
            return data

        # Positioning happens after scale has transformed the data,
        # and stacking only works well for linear data.
        # If the scale(transformation) is not linear, we undo it,
        # do the "stacking" and redo the transformation.
        from ..scales.scale_continuous import scale_continuous

        if isinstance(scales.y, scale_continuous):
            undo_transform = (
                not scales.y.is_linear_scale and scales.y.domain_is_numerical
            )
        else:
            undo_transform = False

        if undo_transform:
            data = cls.transform_position(data, trans_y=scales.y.inverse)

        negative = frame.to_numpy(data["ymax"]) < 0
        neg = frame.filter_rows(data, negative)
        pos = frame.filter_rows(data, ~negative)

        if len(neg):
            neg = cls.collide(neg, params=params)

        if len(pos):
            pos = cls.collide(pos, params=params)

        data = frame.concat([neg, pos])

        if undo_transform:
            data = cls.transform_position(data, trans_y=scales.y.transform)

        return data

    @staticmethod
    def strategy(data, params):
        """
        Stack overlapping intervals.

        Assumes that each set has the same horizontal position
        """
        vjust = params["vjust"]

        y = frame.to_numpy(data["y"]).astype(float)
        y[np.isnan(y)] = 0
        heights = np.append(0, y.cumsum())

        if params["fill"]:
            heights = heights / np.abs(heights[-1])

        ymin = np.min([heights[:-1], heights[1:]], axis=0)
        ymax = np.max([heights[:-1], heights[1:]], axis=0)
        # less intuitive than (ymin + vjust(ymax-ymin)), but
        # this way avoids subtracting numbers of potentially
        # similar precision
        y = (1 - vjust) * ymin + vjust * ymax
        return frame.assign(data, ymin=ymin, ymax=ymax, y=y)
