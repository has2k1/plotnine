from __future__ import annotations

import typing
from abc import ABC
from copy import copy
from warnings import warn

import numpy as np

from .._utils import check_required_aesthetics, groupby_apply
from .._utils.registry import Register, Registry
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import X_AESTHETICS, Y_AESTHETICS

if typing.TYPE_CHECKING:
    from typing import Any, Optional

    import pandas as pd

    from plotnine.iapi import pos_scales
    from plotnine.typing import Geom, Layout, TransformCol


class position(ABC, metaclass=Register):
    """Base class for all positions"""

    REQUIRED_AES: set[str] = set()
    """
    Aesthetics required for the positioning
    """
    params: dict[str, Any]

    def __init__(self):
        self.params = {}

    def setup_params(self, data: pd.DataFrame) -> dict[str, Any]:
        """
        Verify, modify & return a copy of the params.
        """
        return copy(self.params)

    def setup_data(
        self, data: pd.DataFrame, params: dict[str, Any]
    ) -> pd.DataFrame:
        """
        Verify & return data
        """
        check_required_aesthetics(
            self.REQUIRED_AES, data.columns, self.__class__.__name__
        )
        return data

    @classmethod
    def compute_layer(
        cls, data: pd.DataFrame, params: dict[str, Any], layout: Layout
    ):
        """
        Compute position for the layer in all panels

        Positions can override this function instead of
        `compute_panel` if the position computations are
        independent of the panel. i.e when not colliding
        """

        def fn(pdata: pd.DataFrame) -> pd.DataFrame:
            """
            Compute function helper
            """
            # Given data belonging to a specific panel, grab
            # the corresponding scales and call the method
            # that does the real computation
            if len(pdata) == 0:
                return pdata
            scales = layout.get_scales(pdata["PANEL"].iloc[0])
            return cls.compute_panel(pdata, scales, params)

        return groupby_apply(data, "PANEL", fn)

    @classmethod
    def compute_panel(
        cls, data: pd.DataFrame, scales: pos_scales, params: dict[str, Any]
    ) -> pd.DataFrame:
        """
        Positions must override this function

        Notes
        -----
        Make necessary adjustments to the columns in the dataframe.

        Create the position transformation functions and
        use self.transform_position() do the rest.

        See Also
        --------
        position_jitter.compute_panel
        """
        msg = "{} needs to implement this method"
        raise NotImplementedError(msg.format(cls.__name__))

    @staticmethod
    def transform_position(
        data,
        trans_x: Optional[TransformCol] = None,
        trans_y: Optional[TransformCol] = None,
    ) -> pd.DataFrame:
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

        if trans_x:
            xs = [name for name in data.columns if name in X_AESTHETICS]
            data[xs] = data[xs].apply(trans_x)

        if trans_y:
            ys = [name for name in data.columns if name in Y_AESTHETICS]
            data[ys] = data[ys].apply(trans_y)

        return data

    @staticmethod
    def from_geom(geom: Geom) -> position:
        """
        Create and return a position object for the geom

        Parameters
        ----------
        geom : geom
            An instantiated geom object.

        Returns
        -------
        out : position
            A position object

        Raises
        ------
        PlotnineError
            If unable to create a `position`.
        """
        name = geom.params["position"]
        if issubclass(type(name), position):
            return name

        if isinstance(name, type) and issubclass(name, position):
            klass = name
        elif isinstance(name, str):
            if not name.startswith("position_"):
                name = f"position_{name}"
            klass = Registry[name]
        else:
            raise PlotnineError(f"Unknown position of type {type(name)}")

        return klass()

    @staticmethod
    def strategy(data: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        """
        Calculate boundaries of geometry object
        """
        return data

    @classmethod
    def _collide_setup(cls, data, params):
        xminmax = ["xmin", "xmax"]
        width = params.get("width", None)

        # Determine width
        if width is not None:
            # Width set manually
            if not all(col in data.columns for col in xminmax):
                data["xmin"] = data["x"] - width / 2
                data["xmax"] = data["x"] + width / 2
        else:
            if not all(col in data.columns for col in xminmax):
                data["xmin"] = data["x"]
                data["xmax"] = data["x"]

            # Width determined from data, must be floating point constant
            widths = (data["xmax"] - data["xmin"]).drop_duplicates()
            widths = widths[~np.isnan(widths)]
            width = widths.iloc[0]

        return data, width

    @classmethod
    def collide(cls, data, params):
        """
        Calculate boundaries of geometry object

        Uses Strategy
        """
        xminmax = ["xmin", "xmax"]
        data, width = cls._collide_setup(data, params)
        if params.get("width", None) is None:
            params["width"] = width

        # Reorder by x position then on group, relying on stable sort to
        # preserve existing ordering. The default stacking order reverses
        # the group in order to match the legend order.
        if params and "reverse" in params and params["reverse"]:
            idx = data.sort_values(["xmin", "group"], kind="mergesort").index
        else:
            data["-group"] = -data["group"]
            idx = data.sort_values(["xmin", "-group"], kind="mergesort").index
            del data["-group"]

        data = data.loc[idx, :]

        # Check for overlap
        intervals = data[xminmax].drop_duplicates().to_numpy().flatten()
        intervals = intervals[~np.isnan(intervals)]

        if len(np.unique(intervals)) > 1 and any(
            np.diff(intervals - intervals.mean()) < -1e-6
        ):
            msg = "{} requires non-overlapping x intervals"
            warn(msg.format(cls.__name__), PlotnineWarning)

        if "ymax" in data:
            data = groupby_apply(data, "xmin", cls.strategy, params)
        elif "y" in data:
            data["ymax"] = data["y"]
            data = groupby_apply(data, "xmin", cls.strategy, params)
            data["y"] = data["ymax"]
        else:
            raise PlotnineError("Neither y nor ymax defined")

        return data

    @classmethod
    def collide2(cls, data, params):
        """
        Calculate boundaries of geometry object

        Uses Strategy
        """
        data, width = cls._collide_setup(data, params)
        if params.get("width", None) is None:
            params["width"] = width

        # Reorder by x position then on group, relying on stable sort to
        # preserve existing ordering. The default stacking order reverses
        # the group in order to match the legend order.
        if params and "reverse" in params and params["reverse"]:
            data["-group"] = -data["group"]
            idx = data.sort_values(["x", "-group"], kind="mergesort").index
            del data["-group"]
        else:
            idx = data.sort_values(["x", "group"], kind="mergesort").index

        data = data.loc[idx, :]
        data.reset_index(inplace=True, drop=True)
        return cls.strategy(data, params)


transform_position = position.transform_position
