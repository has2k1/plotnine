from __future__ import annotations

import typing
from abc import ABC
from copy import copy
from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import check_required_aesthetics, frame, groupby_apply
from .._utils.frame import native_io
from .._utils.registry import Register
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import X_AESTHETICS, Y_AESTHETICS

if typing.TYPE_CHECKING:
    from typing import Any, Optional

    from plotnine._utils.frame import DataFrame
    from plotnine.facets.layout import Layout
    from plotnine.iapi import pos_scales
    from plotnine.typing import TransformCol


class position(ABC, metaclass=Register):
    """Base class for all positions"""

    REQUIRED_AES: set[str] = set()
    """
    Aesthetics required for the positioning
    """
    params: dict[str, Any]

    def __init__(self):
        self.params = {}

    def setup_params(self, data: DataFrame) -> dict[str, Any]:
        """
        Verify, modify & return a copy of the params.
        """
        return copy(self.params)

    def setup_data(self, data: DataFrame, params: dict[str, Any]) -> DataFrame:
        """
        Verify & return data
        """
        check_required_aesthetics(
            self.REQUIRED_AES, data.columns, self.__class__.__name__
        )
        return data

    @classmethod
    def compute_layer(
        cls, data: DataFrame, params: dict[str, Any], layout: Layout
    ):
        """
        Compute position for the layer in all panels

        Positions can override this function instead of
        `compute_panel` if the position computations are
        independent of the panel. i.e when not colliding
        """

        def fn(pdata: DataFrame) -> DataFrame:
            """
            Compute function helper
            """
            # Given data belonging to a specific panel, grab
            # the corresponding scales and call the method
            # that does the real computation
            if len(pdata) == 0:
                return pdata
            scales = layout.get_scales(pdata["PANEL"].item(0))
            return cls.compute_panel(pdata, scales, params)

        return groupby_apply(data, "PANEL", fn)

    @classmethod
    def compute_panel(
        cls, data: DataFrame, scales: pos_scales, params: dict[str, Any]
    ) -> DataFrame:
        """
        Positions must override this function

        Notes
        -----
        Make necessary adjustments to the columns in the dataframe.

        Create the position transformation functions and
        use self.transform_position() do the rest.

        See Also
        --------
        plotnine.position_jitter.compute_panel
        """
        msg = "{} needs to implement this method"
        raise NotImplementedError(msg.format(cls.__name__))

    @staticmethod
    @native_io
    def transform_position(
        data: DataFrame,
        trans_x: Optional[TransformCol] = None,
        trans_y: Optional[TransformCol] = None,
    ) -> DataFrame:
        """
        Transform all the variables that map onto the x and y scales.

        Parameters
        ----------
        data : dataframe
            Data to transform
        trans_x : callable
            Transforms x scale mappings
            Takes one argument, either a scalar or an array-type
        trans_y : callable
            Transforms y scale mappings
            Takes one argument, either a scalar or an array-type
        """
        if len(data) == 0:
            return data

        transformed = {}
        for trans, aesthetics in (
            (trans_x, X_AESTHETICS),
            (trans_y, Y_AESTHETICS),
        ):
            if not trans:
                continue
            for name in data.columns:
                if name in aesthetics:
                    transformed[name] = trans(frame.to_numpy(data[name]))

        return frame.assign(data, **transformed)

    @staticmethod
    def strategy(data: DataFrame, params: dict[str, Any]) -> DataFrame:
        """
        Calculate boundaries of geometry object
        """
        return data

    @classmethod
    def _collide_setup(cls, data: DataFrame, params: dict[str, Any]):
        xminmax = ["xmin", "xmax"]
        width = params.get("width")
        has_minmax = all(col in data.columns for col in xminmax)

        # Determine width
        if width is not None:
            # Width set manually
            if not has_minmax:
                x = frame.to_numpy(data["x"])
                data = frame.assign(
                    data, xmin=x - width / 2, xmax=x + width / 2
                )
        else:
            if not has_minmax:
                data = frame.assign(data, xmin=data["x"], xmax=data["x"])

            # Width determined from data, must be floating point constant
            widths = frame.to_numpy(data["xmax"] - data["xmin"])
            widths = widths[~np.isnan(widths)]
            width = widths[0]

        return data, width

    @classmethod
    def collide(cls, data: DataFrame, params: dict[str, Any]) -> DataFrame:
        """
        Calculate boundaries of geometry object

        Uses Strategy
        """
        xminmax = ["xmin", "xmax"]
        data, width = cls._collide_setup(data, params)
        if params.get("width") is None:
            params["width"] = width

        # Reorder by x position then on group, relying on stable sort to
        # preserve existing ordering. The default stacking order reverses
        # the group in order to match the legend order.
        if params and "reverse" in params and params["reverse"]:
            data = frame.sort(data, ["xmin", "group"])
        else:
            data = frame.sort(
                data, ["xmin", "group"], descending=[False, True]
            )

        # Check for overlap
        intervals = (
            data.select(xminmax)
            .unique(maintain_order=True)
            .to_numpy()
            .flatten()
        )
        intervals = intervals[~np.isnan(intervals)]

        if len(np.unique(intervals)) > 1 and any(
            np.diff(intervals - intervals.mean()) < -1e-6
        ):
            msg = "{} requires non-overlapping x intervals"
            warn(msg.format(cls.__name__), PlotnineWarning)

        if "ymax" in data.columns:
            data = groupby_apply(data, "xmin", cls.strategy, params)
        elif "y" in data.columns:
            data = data.with_columns(ymax=nw.col("y"))
            data = groupby_apply(data, "xmin", cls.strategy, params)
            data = data.with_columns(y=nw.col("ymax"))
        else:
            raise PlotnineError("Neither y nor ymax defined")

        return data

    @classmethod
    def collide2(cls, data: DataFrame, params: dict[str, Any]) -> DataFrame:
        """
        Calculate boundaries of geometry object

        Uses Strategy
        """
        data, width = cls._collide_setup(data, params)
        if params.get("width") is None:
            params["width"] = width

        # Reorder by x position then on group, relying on stable sort to
        # preserve existing ordering. The default stacking order reverses
        # the group in order to match the legend order.
        if params and "reverse" in params and params["reverse"]:
            data = frame.sort(data, ["x", "group"], descending=[False, True])
        else:
            data = frame.sort(data, ["x", "group"])

        return cls.strategy(data, params)


transform_position = position.transform_position
