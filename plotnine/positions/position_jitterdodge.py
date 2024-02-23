from __future__ import annotations

import typing
from contextlib import suppress
from copy import copy

from .._utils import jitter, resolution
from ..exceptions import PlotnineError
from ..mapping.aes import SCALED_AESTHETICS
from .position import position
from .position_dodge import position_dodge

if typing.TYPE_CHECKING:
    from typing import Optional

    import numpy as np


# Adjust position by simultaneously dodging and jittering
class position_jitterdodge(position):
    """
    Dodge and jitter to minimise overlap

    Useful when aligning points generated through
    [](`~plotnine.geoms.geom_point`) with dodged a
    [](`~plotnine.geoms.geom_boxplot`).

    Parameters
    ----------
    jitter_width :
        Proportion to jitter in horizontal direction.
        If `None`, `0.4` of the resolution of the data.
    jitter_height :
        Proportion to jitter in vertical direction.
    dodge_width :
        Amount to dodge in horizontal direction.
    random_state :
        Seed or Random number generator to use. If `None`, then
        numpy global generator [](`numpy.random`) is used.
    """

    REQUIRED_AES = {"x", "y"}
    strategy = staticmethod(position_dodge.strategy)

    def __init__(
        self,
        jitter_width: Optional[float] = None,
        jitter_height: float = 0,
        dodge_width: float = 0.75,
        random_state: Optional[int | np.random.RandomState] = None,
    ):
        self.params = {
            "jitter_width": jitter_width,
            "jitter_height": jitter_height,
            "dodge_width": dodge_width,
            "random_state": random_state,
        }

    def setup_params(self, data):
        params = copy(self.params)
        width = params["jitter_width"]
        if width is None:
            width = resolution(data["x"]) * 0.4

        # Adjust the x transformation based on the number
        # of dodge variables
        dvars = SCALED_AESTHETICS - self.REQUIRED_AES
        dodge_columns = data.columns.intersection(list(dvars))
        if len(dodge_columns) == 0:
            raise PlotnineError(
                "'position_jitterdodge' requires at least one "
                "aesthetic to dodge by."
            )

        s = set()
        for col in dodge_columns:
            with suppress(AttributeError):
                s.update(data[col].cat.categories)
        ndodge = len(s)

        params["jitter_width"] = width / (ndodge + 2)
        params["width"] = params["dodge_width"]
        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        trans_x = None  # pyright: ignore
        trans_y = None  # pyright: ignore

        if params["jitter_width"] > 0:

            def trans_x(x):
                return jitter(
                    x,
                    amount=params["jitter_width"],
                    random_state=params["random_state"],
                )

        if params["jitter_height"] > 0:

            def trans_y(y):
                return jitter(
                    y,
                    amount=params["jitter_height"],
                    random_state=params["random_state"],
                )

        # dodge, then jitter
        data = cls.collide(data, params=params)
        data = cls.transform_position(data, trans_x, trans_y)
        return data
