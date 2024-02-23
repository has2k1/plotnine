from __future__ import annotations

import typing
from copy import deepcopy

import numpy as np

from .._utils import jitter, resolution
from .position import position

if typing.TYPE_CHECKING:
    from typing import Optional

    from plotnine.typing import FloatArray, FloatArrayLike


class position_jitter(position):
    """
    Jitter points to avoid overplotting

    Parameters
    ----------
    width :
        Proportion to jitter in horizontal direction.
        If `None`, `0.4` of the resolution of the data.
    height :
        Proportion to jitter in vertical direction.
        If `None`, `0.4` of the resolution of the data.
    random_state :
        Seed or Random number generator to use. If `None`, then
        numpy global generator [](`numpy.random`) is used.
    """

    REQUIRED_AES = {"x", "y"}

    def __init__(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        random_state: Optional[int | np.random.RandomState] = None,
    ):
        self.params = {
            "width": width,
            "height": height,
            "random_state": random_state,
        }

    def setup_params(self, data):
        params = deepcopy(self.params)
        if params["width"] is None:
            params["width"] = resolution(data["x"]) * 0.4
        if params["height"] is None:
            params["height"] = resolution(data["y"]) * 0.4
        if not params["random_state"]:
            params["random_state"] = np.random
        return params

    @classmethod
    def compute_layer(cls, data, params, layout):
        trans_x = None  # pyright: ignore
        trans_y = None  # pyright: ignore

        if params["width"]:

            def trans_x(x: FloatArrayLike) -> FloatArray:
                return jitter(
                    x,
                    amount=params["width"],
                    random_state=params["random_state"],
                )

        if params["height"]:

            def trans_y(y):
                return jitter(
                    y,
                    amount=params["height"],
                    random_state=params["random_state"],
                )

        return cls.transform_position(data, trans_x, trans_y)
